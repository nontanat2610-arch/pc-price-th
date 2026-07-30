# -*- coding: utf-8 -*-
"""
verify_prices.py — ตรวจราคาที่ขยับแรงกับหน้าสินค้าตัวจริง

ปัญหา: crawl_jib.py อ่านราคาจากหน้ารายการหมวด ซึ่งการ์ดสินค้าสลับตำแหน่งได้
       ทำให้บางรอบจับราคาของรุ่นย่อยอื่นมาใส่ผิดรายการ (เคยเจอ +55% ทั้งที่ราคาไม่ขยับ)

วิธีแก้: รายการที่ขยับเกิน THRESHOLD ให้ไปเปิดหน้าสินค้าจริงแล้วอ่าน .price_block
        ถ้าไม่ตรง = อ่านผิด → เขียนราคาที่ถูกกลับลงไป

รันต่อจาก crawl_jib.py และก่อน build_movers.py:
    python scraper/verify_prices.py
"""

import json
import os
import re
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_FILE = os.path.join(ROOT, "data", "prices.json")
JS_FILE = os.path.join(ROOT, "data", "prices.js")
LOG_FILE = os.path.join(ROOT, "data", "verify-log.json")

REAL_FROM = "2026-07-25"   # ก่อนวันนี้เป็นข้อมูลจำลอง ไม่ต้องตรวจ
THRESHOLD = 0.12           # ขยับเกิน 12% ถือว่าน่าสงสัย ต้องไปเช็คหน้าสินค้า
MAX_CHECK = 150            # เพดานจำนวนหน้าต่อรอบ กันไม่ให้ยิงร้านหนักเกินไป
STORE = "JIB"              # ร้านที่ crawl มาจากหน้าหมวด

# ดึงราคาจากหน้าสินค้า — .price_block คือกล่อง "ราคา บาท 5,800"
EXTRACT_JS = """
() => {
  const b = document.querySelector('.price_block');
  return b ? b.innerText : null;
}
"""


def to_price(text):
    """'ราคา บาท 5,800' -> 5800 (เอาเลขก้อนท้ายสุด)"""
    if not text:
        return None
    nums = re.findall(r"[\d,]{3,}", text.replace("\xa0", " "))
    if not nums:
        return None
    try:
        return int(nums[-1].replace(",", ""))
    except ValueError:
        return None


def real_points(p):
    """ราคาของร้าน STORE เฉพาะวันที่เก็บจริง"""
    return [h for h in (p.get("history", {}).get(STORE) or []) if h["date"] >= REAL_FROM]


def main():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    products = data.get("products", [])

    # 1) หารายการที่ขยับแรงในรอบล่าสุด
    cands = []
    for p in products:
        pts = real_points(p)
        if len(pts) < 2 or not p.get("source_url"):
            continue
        before, now = pts[-2]["price"], pts[-1]["price"]
        if not before or not now:
            continue
        pct = (now - before) / before
        if abs(pct) >= THRESHOLD:
            cands.append((abs(pct), pct, p, before, now))

    cands.sort(reverse=True, key=lambda x: x[0])
    cands = cands[:MAX_CHECK]
    print(f"พบรายการที่ขยับเกิน {THRESHOLD:.0%} จำนวน {len(cands)} รายการ — กำลังเช็คหน้าสินค้า")

    if not cands:
        print("ไม่มีอะไรต้องตรวจ")
        return

    fixed, confirmed, failed = [], 0, 0

    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"))

        for _, pct, p, before, now in cands:
            try:
                page.goto(p["source_url"], timeout=45000, wait_until="domcontentloaded")
                page.wait_for_selector(".price_block", timeout=15000)
                real = to_price(page.evaluate(EXTRACT_JS))
            except Exception as e:
                failed += 1
                print(f"  ✗ เปิดไม่ได้: {p['name'][:45]} ({type(e).__name__})")
                continue

            if not real:
                failed += 1
                continue

            pts = real_points(p)
            pts[-1]["checked"] = True               # ตรวจกับหน้าสินค้าแล้ว เชื่อถือได้
            if real == now:
                confirmed += 1                      # ราคาขยับจริง ปล่อยไว้
            else:
                pts[-1]["price"] = real             # แก้ราคาในรอบล่าสุด
                pts[-1]["corrected"] = True
                fixed.append({
                    "name": p["name"], "slug": p.get("slug") or p.get("id"),
                    "listing_price": now, "page_price": real, "prev": before,
                })
                print(f"  ⟳ แก้ {p['name'][:45]}: {now:,} → {real:,} (ก่อนหน้า {before:,})")

    # 2) เขียนกลับ
    data["products"] = products
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    with open(JS_FILE, "w", encoding="utf-8") as f:
        f.write("window.PRICE_DATA = " + json.dumps(data, ensure_ascii=False) + ";")

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "checked_at": datetime.date.today().isoformat(),
            "threshold_pct": THRESHOLD * 100,
            "checked": len(cands),
            "corrected": len(fixed),
            "confirmed_real": confirmed,
            "failed": failed,
            "corrections": fixed,
        }, f, ensure_ascii=False, indent=1)

    print(f"\nตรวจ {len(cands)} · แก้ราคาผิด {len(fixed)} · "
          f"ยืนยันว่าขยับจริง {confirmed} · เปิดไม่ได้ {failed}")


if __name__ == "__main__":
    main()
