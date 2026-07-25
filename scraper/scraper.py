#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPU Price TH — scraper ดึงราคาการ์ดจอรายวัน
============================================
วิธีใช้:
    python scraper.py --mock     # โหมดทดสอบ: ขยับราคาจากข้อมูลเดิมเล็กน้อย (ไม่ต้องต่อเน็ต)
    python scraper.py            # โหมดจริง: ดึงราคาตาม config.json

หมายเหตุสำคัญ: เว็บ JIB / Advice เป็นแบบ JavaScript-render
ดึงด้วย requests ตรงๆ ไม่ได้ ต้องใช้ Playwright (ติดตั้ง: pip install playwright && playwright install chromium)
script นี้รองรับทั้ง 2 วิธี — ตั้งค่า "method": "requests" หรือ "playwright" ต่อร้านใน config.json
"""
import json, re, sys, argparse, random, datetime, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "prices.json"
JS_FILE = ROOT / "data" / "prices.js"
CONFIG_FILE = Path(__file__).resolve().parent / "config.json"
ALERTS_FILE = Path(__file__).resolve().parent / "alerts.json"
TODAY = str(datetime.date.today())
MAX_HISTORY_DAYS = 90


def load_json(path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def extract_price(text):
    """หาตัวเลขราคาจากข้อความ เช่น '฿ 22,500.-' -> 22500"""
    m = re.search(r"([\d,]{4,})", text.replace(" ", ""))
    return int(m.group(1).replace(",", "")) if m else None


def fetch_requests(url, selector):
    """ดึงด้วย requests + BeautifulSoup (สำหรับเว็บ static)"""
    from bs4 import BeautifulSoup
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (GPUPriceTH bot)"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
    el = BeautifulSoup(html, "html.parser").select_one(selector)
    return extract_price(el.get_text()) if el else None


def fetch_playwright(url, selector):
    """ดึงด้วย Playwright (สำหรับเว็บ JS-render เช่น JIB, Advice)"""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.goto(url, timeout=60000, wait_until="networkidle")
        el = page.query_selector(selector)
        price = extract_price(el.inner_text()) if el else None
        browser.close()
        return price


def scrape(config, data):
    products = {p["id"]: p for p in data["products"]}
    for item in config["products"]:
        p = products.setdefault(item["id"], {
            "id": item["id"], "name": item["name"],
            "category": item.get("category", "gpu"), "specs": item.get("specs", {}),
            "affiliate_url": item.get("affiliate_url", "#"), "history": {},
        })
        p["name"] = item["name"]
        if item.get("category"):
            p["category"] = item["category"]
        if item.get("specs"):
            p["specs"] = item["specs"]
        if item.get("image"):
            p["image"] = item["image"]
        if item.get("affiliate_url"):
            p["affiliate_url"] = item["affiliate_url"]
        for store, src in item.get("sources", {}).items():
            method = config["stores"].get(store, {}).get("method", "requests")
            try:
                fn = fetch_playwright if method == "playwright" else fetch_requests
                price = fn(src["url"], src["selector"])
            except Exception as e:
                print(f"  ! {item['id']}@{store}: {e}")
                price = None
            if price:
                append_price(p, store, price)
                print(f"  ✓ {item['id']}@{store}: {price:,} ฿")
    data["products"] = list(products.values())


def mock(data):
    """โหมดทดสอบ: ขยับราคาเดิม ±0-500 บาท"""
    for p in data["products"]:
        for store, series in p["history"].items():
            last = series[-1]["price"]
            price = max(1000, last + random.choice([0, 0, 0, -100, -200, -500, 100, 300]))
            append_price(p, store, price)
    print(f"  ✓ mock: อัปเดต {len(data['products'])} รุ่น")


def append_price(product, store, price):
    series = product["history"].setdefault(store, [])
    if series and series[-1]["date"] == TODAY:
        series[-1]["price"] = price
    else:
        series.append({"date": TODAY, "price": price})
    del series[:-MAX_HISTORY_DAYS]


def check_alerts(data):
    """แจ้งเตือนผ่าน Discord webhook เมื่อราคาต่ำกว่าเป้า (ตั้งค่าใน alerts.json)"""
    alerts = load_json(ALERTS_FILE, {"webhook": "", "rules": []})
    if not alerts.get("webhook") or "discord.com" not in alerts["webhook"]:
        return
    products = {p["id"]: p for p in data["products"]}
    msgs = []
    for rule in alerts["rules"]:
        p = products.get(rule["id"])
        if not p:
            continue
        best_store, best = None, None
        for store, series in p["history"].items():
            if series and (best is None or series[-1]["price"] < best):
                best, best_store = series[-1]["price"], store
        if best and best <= rule["target"]:
            msgs.append(f"🎉 **{p['name']}** เหลือ **{best:,} ฿** ที่ {best_store} (เป้า {rule['target']:,} ฿)")
    if msgs:
        body = json.dumps({"content": "\n".join(msgs)}).encode()
        req = urllib.request.Request(alerts["webhook"], data=body,
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=15)
        print(f"  🔔 ส่งแจ้งเตือน {len(msgs)} รายการ")


def save(data):
    data["updated"] = TODAY
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    JS_FILE.write_text("window.PRICE_DATA = " + json.dumps(data, ensure_ascii=False) + ";",
                       encoding="utf-8")
    print(f"  ✓ บันทึก {DATA_FILE.name} + {JS_FILE.name}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true", help="โหมดทดสอบ ไม่ดึงเว็บจริง")
    args = ap.parse_args()

    data = load_json(DATA_FILE, {"updated": "", "products": []})
    config = load_json(CONFIG_FILE, {"stores": {}, "products": []})

    print(f"GPU Price TH scraper — {TODAY}")
    if args.mock:
        mock(data)
    else:
        scrape(config, data)
    check_alerts(data)
    save(data)
