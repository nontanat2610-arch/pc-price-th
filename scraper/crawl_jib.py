#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
crawl_jib.py — กวาดสินค้าทั้งหมวดจาก JIB เข้า data/prices.json

ทำไมต้องมีไฟล์นี้:
  scraper.py เดิมค้นหาทีละชื่อรุ่นตาม config.json (48 รายการ) ซึ่งครอบคลุมไม่พอ
  ไฟล์นี้กวาดทั้งหมวด -> ได้หลักพันรายการ -> แต่ละรายการกลายเป็น 1 หน้า SEO

ลำดับหมวดเรียงตาม "โซนราคาที่ทำเงินได้ดีที่สุด" ภายใต้เพดานค่าคอม Shopee 225฿/ออเดอร์
  (จุดคุ้มที่สุด = ราคาราว 11,250฿ ของแพงกว่านั้นได้ค่าคอมเท่ากันแต่ขายยากกว่ามาก)

หน้าหมวด JIB เป็น JS-render จึงต้องใช้ Playwright
  pip install playwright && playwright install chromium
"""
import json, re, sys, datetime, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "prices.json"
JS_FILE = ROOT / "data" / "prices.js"
TODAY = str(datetime.date.today())
MAX_HISTORY_DAYS = 90
BASE = "https://www.jib.co.th"

# (คีย์หมวดในเว็บเรา, กลุ่ม/รหัสหมวด JIB, ชื่อไทย, จำนวนหน้าสูงสุด)
# เรียงตามความสำคัญ: โซนราคา 3,000–15,000฿ มาก่อน
CATEGORIES = [
    ("ram",       "2/53",   "แรม",              4),
    ("ssd",       "3/1471", "SSD M.2",          4),
    ("psu",       "3/185",  "พาวเวอร์ซัพพลาย",  4),
    ("case",      "3/184",  "เคสคอม",           4),
    ("cooling",   "2/1438", "ชุดน้ำ",           3),
    ("cooling",   "2/1367", "พัดลมซีพียู",      3),
    ("monitor",   "2/233",  "จอมอนิเตอร์",      5),
    ("gpu",       "2/51",   "การ์ดจอ",          4),
    ("cpu",       "2/43",   "ซีพียู",           4),
    ("mainboard", "2/46",   "เมนบอร์ด",         4),
]

PER_PAGE = 100

# JS ที่ยิงเข้าไปในหน้า เพื่อดึงการ์ดสินค้าออกมา
EXTRACT_JS = """
() => [...document.querySelectorAll('div.reladiv')].map(c => {
  const nameEl  = c.querySelector('span.promo_name');
  const priceEl = c.querySelector('.price_total');
  const link    = [...c.querySelectorAll('a')].map(a => a.getAttribute('href'))
                    .find(h => h && h.includes('readProduct')) || null;
  const img     = [...c.querySelectorAll('img')].map(i => i.getAttribute('src'))
                    .find(s => s && s.includes('/img_master/product/')) || null;
  return {
    name:  nameEl  ? nameEl.innerText.trim()  : null,
    price: priceEl ? priceEl.innerText.trim() : null,
    url:   link,
    img:   img,
  };
}).filter(x => x.name && x.price);
"""

# ตัดคำนำหน้าประเภทสินค้าที่ JIB ใส่ไว้ เช่น "VGA (การ์ดแสดงผล) ASUS ..." -> "ASUS ..."
PREFIX_RE = re.compile(r"^[A-Za-z0-9/&.\- ]{2,30}\s*\([^)]{2,40}\)\s*")


def clean_name(raw):
    n = PREFIX_RE.sub("", raw).strip()
    n = re.sub(r"\s+", " ", n)
    return n or raw.strip()


def to_price(raw):
    m = re.search(r"([\d,]{3,9})", raw.replace(" ", ""))
    return int(m.group(1).replace(",", "")) if m else None


def slugify(name):
    s = unicodedata.normalize("NFKD", name).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:70] or "item"


# จับซ็อกเก็ตจากชิปเซ็ต/ชื่อรุ่นซีพียู — เรียงจากเฉพาะเจาะจงไปกว้าง (ลำดับสำคัญ)
SOCKET_HINTS = [
    (r"\bAM5\b|\b(?:A620|B650|B840|B850|X670|X870)[A-Z]?\b|RYZEN\s*[3579]\s*[89]\d{3}|RYZEN\s*[3579]\s*7\d{3}", "AM5"),
    (r"\bAM4\b|\b(?:A320|A520|B450|B550|X470|X570)[A-Z]?\b|RYZEN\s*[3579]\s*[1-5]\d{3}", "AM4"),
    (r"\bLGA\s*1851\b|\b(?:B860|H810|Z890)[A-Z]?\b|CORE\s*ULTRA", "LGA1851"),
    (r"\bLGA\s*1700\b|\b(?:B660|B760|H610|H770|Z690|Z790)[A-Z]?\b|\bI[3579][- ]?1[2-4]\d{3}", "LGA1700"),
    (r"\bLGA\s*1200\b|\b(?:B560|H510|Z590)[A-Z]?\b|\bI[3579][- ]?1[01]\d{3}", "LGA1200"),
]


def parse_specs(name, cat):
    """เดาสเปคจากชื่อรุ่น เพื่อให้ตัวกรองบนเว็บใช้งานได้"""
    n = name.upper()
    s = {}
    if cat == "gpu":
        m = re.search(r"(\d{1,2})\s?GB", n)
        if m:
            s["vram"] = int(m.group(1))
    elif cat == "ram":
        m = re.search(r"\bDDR(\d)\b", n)
        if m:
            s["ram"] = "DDR" + m.group(1)
        m = (re.search(r"(\d{4})\s*MHZ", n) or re.search(r"DDR\d[\s-]+(\d{4})", n)
             or re.search(r"\b([2-9]\d{3})\b(?!\s?GB)", n))
        if m and 2000 <= int(m.group(1)) <= 9000:
            s["bus"] = int(m.group(1))
        m = re.search(r"(\d{1,3})\s?GB", n)
        if m:
            s["size"] = m.group(1) + "GB"
    elif cat == "ssd":
        m = re.search(r"(\d{1,2})\s?TB|(\d{3,4})\s?GB", n)
        if m:
            s["size"] = (m.group(1) + "TB") if m.group(1) else (m.group(2) + "GB")
        if "GEN5" in n or "PCIE 5" in n:
            s["gen"] = "Gen5"
        elif "GEN4" in n or "PCIE 4" in n:
            s["gen"] = "Gen4"
    elif cat == "psu":
        m = re.search(r"(\d{3,4})\s?W\b", n)
        if m:
            s["watt"] = int(m.group(1))
        for g in ("TITANIUM", "PLATINUM", "GOLD", "BRONZE"):
            if g in n:
                s["rating"] = g.title()
                break
    elif cat in ("cpu", "mainboard"):
        sock = None
        for pat, sk in SOCKET_HINTS:
            if re.search(pat, n):
                sock = sk
                break
        if sock:
            s["socket"] = sock
        if cat == "mainboard":
            m = re.search(r"\bDDR(\d)\b", n)
            if m:
                s["ram"] = "DDR" + m.group(1)
    elif cat == "monitor":
        m = re.search(r"(\d{2}(?:\.\d)?)\s?(?:\"|INCH|นิ้ว)", n)
        if m:
            s["size"] = m.group(1) + " นิ้ว"
        m = re.search(r"(\d{2,3})\s?HZ", n)
        if m:
            s["hz"] = int(m.group(1))
    return s


def crawl(page, path, max_pages):
    rows, seen = [], set()
    for i in range(max_pages):
        offset = i * PER_PAGE
        url = f"{BASE}/web/product/product_list/{path}" + (f"/{offset}" if offset else "")
        try:
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_selector("div.reladiv", timeout=20000)
            page.wait_for_timeout(1200)
            batch = page.evaluate(EXTRACT_JS)
        except Exception as e:
            print(f"    ! หน้า {i+1} ล้มเหลว: {type(e).__name__}", file=sys.stderr)
            break
        fresh = [b for b in batch if b["name"] not in seen]
        for b in fresh:
            seen.add(b["name"])
        rows += fresh
        print(f"    หน้า {i+1}: {len(batch)} รายการ (ใหม่ {len(fresh)})")
        if len(batch) < PER_PAGE or not fresh:
            break
    return rows


def main():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    products = data["products"]
    by_slug = {p.get("slug") or slugify(p["name"]): p for p in products}

    from playwright.sync_api import sync_playwright
    added = updated = 0

    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"))
        for cat, path, label, max_pages in CATEGORIES:
            print(f"  → {label} ({cat}) …")
            for r in crawl(page, path, max_pages):
                name = clean_name(r["name"])
                price = to_price(r["price"])
                if not price or price < 200:
                    continue
                slug = slugify(name)
                img = r["img"]
                if img and img.startswith("/"):
                    img = BASE + img
                if img:
                    img = img.split("?")[0]

                p = by_slug.get(slug)
                if p:                                   # มีอยู่แล้ว → อัปเดตราคา JIB
                    hist = p.setdefault("history", {}).setdefault("JIB", [])
                    if not hist or hist[-1]["date"] != TODAY:
                        hist.append({"date": TODAY, "price": price})
                    else:
                        hist[-1]["price"] = price
                    updated += 1
                else:                                   # ของใหม่
                    p = {
                        "id": slug,
                        "slug": slug,
                        "name": name,
                        "category": cat,
                        "specs": parse_specs(name, cat),
                        "image": img,
                        "source_url": (BASE + r["url"]) if r["url"] and r["url"].startswith("/") else r["url"],
                        "affiliate_url": None,
                        "history": {"JIB": [{"date": TODAY, "price": price}]},
                    }
                    products.append(p)
                    by_slug[slug] = p
                    added += 1

    # ตัดประวัติที่เก่าเกินกำหนด
    cutoff = str(datetime.date.today() - datetime.timedelta(days=MAX_HISTORY_DAYS))
    for p in products:
        for store, hist in p.get("history", {}).items():
            p["history"][store] = [h for h in hist if h["date"] >= cutoff] or hist[-1:]

    data["updated"] = TODAY
    data["products"] = products
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    JS_FILE.write_text("window.PRICE_DATA = " + json.dumps(data, ensure_ascii=False) + ";",
                       encoding="utf-8")

    from collections import Counter
    c = Counter(p["category"] for p in products)
    print(f"\n  เพิ่มใหม่ {added} · อัปเดต {updated} · รวมทั้งหมด {len(products)} รายการ")
    print("  " + " · ".join(f"{k} {v}" for k, v in c.most_common()))


if __name__ == "__main__":
    main()
