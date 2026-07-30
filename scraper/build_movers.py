# -*- coding: utf-8 -*-
"""
build_movers.py — สรุป "ราคาขึ้น/ลง" จาก data/prices.json ออกมาเป็น data/movers.json
ใช้เฉพาะข้อมูลที่เก็บจริง (วันที่ >= REAL_FROM) เท่านั้น ไม่แตะช่วงข้อมูลจำลอง

รันหลัง scraper.py และ crawl_jib.py:
    python scraper/build_movers.py
"""

import json
import os
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PRICES = os.path.join(ROOT, "data", "prices.json")
OUT = os.path.join(ROOT, "data", "movers.json")

REAL_FROM = "2026-07-25"   # วันแรกที่เริ่มเก็บราคาจริง
TOP_N = 15                 # เก็บอันดับละกี่รายการ

CAT_NAME = {
    "gpu": "การ์ดจอ", "cpu": "ซีพียู", "mainboard": "เมนบอร์ด", "ram": "แรม",
    "ssd": "SSD", "psu": "พาวเวอร์ซัพพลาย", "case": "เคสคอม",
    "monitor": "จอมอนิเตอร์", "cooling": "ชุดระบายความร้อน", "console": "เครื่องเกม",
}


def slug_of(p):
    return p.get("slug") or p.get("id") or ""


def real_series(p):
    """คืน {date: ราคาถูกสุดของวันนั้น} โดยใช้เฉพาะวันที่ >= REAL_FROM"""
    best = {}
    for rows in (p.get("history") or {}).values():
        for r in rows or []:
            d, price = r.get("date"), r.get("price")
            if not d or not price or d < REAL_FROM:
                continue
            if d not in best or price < best[d]:
                best[d] = price
    return best


def main():
    with open(PRICES, encoding="utf-8") as f:
        data = json.load(f)
    products = data.get("products", data if isinstance(data, list) else [])

    # หาวันเก็บข้อมูลจริงทั้งหมด เรียงจากเก่าไปใหม่
    all_dates = set()
    cache = {}
    for p in products:
        s = real_series(p)
        cache[id(p)] = s
        all_dates.update(s.keys())
    dates = sorted(all_dates)

    latest = dates[-1] if dates else None
    prev = dates[-2] if len(dates) >= 2 else None

    drops, rises, lows, unchanged = [], [], [], 0

    for p in products:
        s = cache[id(p)]
        if not s or not latest or latest not in s:
            continue
        now = s[latest]
        item = {
            "name": p.get("name", ""),
            "slug": slug_of(p),
            "category": p.get("category", ""),
            "category_th": CAT_NAME.get(p.get("category", ""), ""),
            "now": now,
            "url": "https://pricespec.vercel.app/p/" + slug_of(p),
        }

        # เทียบกับรอบเก็บก่อนหน้า
        if prev and prev in s:
            before = s[prev]
            diff = now - before
            if diff != 0:
                row = dict(item, prev=before, diff=diff,
                           pct=round(diff / before * 100, 1))
                (rises if diff > 0 else drops).append(row)
            else:
                unchanged += 1

        # ต่ำสุดตั้งแต่เริ่มเก็บจริง (ต้องมีอย่างน้อย 3 จุด กันสัญญาณหลอก)
        vals = list(s.values())
        if len(vals) >= 3 and now == min(vals) and max(vals) > now:
            lows.append(dict(item, high=max(vals),
                             save=max(vals) - now,
                             points=len(vals)))

    drops.sort(key=lambda r: r["pct"])           # ลดแรงสุดก่อน
    rises.sort(key=lambda r: -r["pct"])          # ขึ้นแรงสุดก่อน
    lows.sort(key=lambda r: -r["save"])

    # สินค้าถูกสุดในแต่ละหมวด (ใช้เป็นคอนเทนต์สำรองตอนที่ราคาไม่ขยับ)
    cheapest = {}
    for p in products:
        s = cache[id(p)]
        if not s or not latest or latest not in s:
            continue
        c = p.get("category", "")
        row = {"name": p.get("name", ""), "now": s[latest],
               "url": "https://pricespec.vercel.app/p/" + slug_of(p)}
        if c not in cheapest or row["now"] < cheapest[c]["now"]:
            cheapest[c] = row

    out = {
        "generated": datetime.date.today().isoformat(),
        "real_from": REAL_FROM,
        "snapshots": dates,
        "compare": {"from": prev, "to": latest},
        "stats": {
            "tracked": len(products),
            "with_price": sum(1 for p in products if cache[id(p)].get(latest)),
            "dropped": len(drops),
            "rose": len(rises),
            "unchanged": unchanged,
            "new_lows": len(lows),
        },
        "drops": drops[:TOP_N],
        "rises": rises[:TOP_N],
        "new_lows": lows[:TOP_N],
        "cheapest_by_category": cheapest,
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    print(f"movers.json: เทียบ {prev} → {latest} · "
          f"ลด {len(drops)} · ขึ้น {len(rises)} · เท่าเดิม {unchanged} · "
          f"ต่ำสุดใหม่ {len(lows)}")


if __name__ == "__main__":
    main()
