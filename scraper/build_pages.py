#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
สร้างหน้าเว็บแบบ static แยกตามหมวดสินค้า เพื่อให้ Google เก็บข้อมูล (index) ได้
รันหลัง scraper.py ทุกครั้ง -> จะได้หน้าที่มีราคาล่าสุดฝังอยู่ใน HTML จริง
"""
import json, os, html, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://pricespec.vercel.app"

CATS = {
    "gpu": {
        "slug": "gpu",
        "name": "การ์ดจอ",
        "emoji": "🎮",
        "title": "ราคาการ์ดจอวันนี้ 2026 เทียบ 3 ร้าน JIB Advice iHAVECPU | PriceSpec",
        "desc": "เช็คราคาการ์ดจอล่าสุด RTX 5060 5070 5070 Ti 5080 5090, Radeon RX 9070 XT, Intel Arc B580 เทียบราคาจาก 3 ร้านไทย พร้อมกราฟราคาย้อนหลังและราคาเฉลี่ย อัปเดตทุกสัปดาห์",
        "h2": "ราคาการ์ดจอล่าสุดในไทย",
        "intro": "รวมราคาการ์ดจอ NVIDIA GeForce RTX 50 Series, AMD Radeon RX 9000 Series และ Intel Arc จากร้านค้าไทย 3 ร้าน (JIB, Advice, iHAVECPU) แสดงราคาเฉลี่ยพร้อมราคาแยกรายร้าน เพื่อให้เห็นว่าร้านไหนถูกที่สุด",
    },
    "cpu": {
        "slug": "cpu",
        "name": "ซีพียู",
        "emoji": "🧠",
        "title": "ราคาซีพียู CPU วันนี้ AMD Ryzen / Intel Core เทียบ 3 ร้าน | PriceSpec",
        "desc": "เช็คราคาซีพียู AMD Ryzen 5600, 9600X, 9800X3D และ Intel Core i5-14400F, Core Ultra 5 245K, i9-14900K เทียบราคา JIB Advice iHAVECPU พร้อมกราฟราคาย้อนหลัง",
        "h2": "ราคาซีพียู (CPU) ล่าสุดในไทย",
        "intro": "รวมราคาซีพียู AMD Ryzen และ Intel Core จากร้านคอมไทย เทียบราคา 3 ร้านในหน้าเดียว ดูซ็อกเก็ตประกอบการเลือกเมนบอร์ดได้ทันที",
    },
    "mainboard": {
        "slug": "mainboard",
        "name": "เมนบอร์ด",
        "emoji": "🔲",
        "title": "ราคาเมนบอร์ด Mainboard วันนี้ AM4 AM5 LGA1700 | PriceSpec",
        "desc": "เช็คราคาเมนบอร์ด MSI, ASUS, ASRock ทั้ง B550, B650, X870, B760, B860 เทียบ 3 ร้านไทย พร้อมบอกซ็อกเก็ตและชนิดแรมที่รองรับ",
        "h2": "ราคาเมนบอร์ดล่าสุดในไทย",
        "intro": "รวมราคาเมนบอร์ดยอดนิยมทั้งฝั่ง AMD (AM4/AM5) และ Intel (LGA1700/LGA1851) ระบุซ็อกเก็ตและชนิดแรมที่รองรับ ช่วยให้จับคู่กับซีพียูได้ถูกต้อง",
    },
    "ram": {
        "slug": "ram",
        "name": "แรม",
        "emoji": "📏",
        "title": "ราคาแรม RAM DDR4 DDR5 วันนี้ เทียบ 3 ร้านไทย | PriceSpec",
        "desc": "เช็คราคาแรม Kingston FURY, Corsair Vengeance, G.SKILL Trident Z5 ทั้ง DDR4 3200 และ DDR5 5600 6000 6400 เทียบราคา JIB Advice iHAVECPU",
        "h2": "ราคาแรม (RAM) ล่าสุดในไทย",
        "intro": "รวมราคาแรมคอมพิวเตอร์ DDR4 และ DDR5 หลายบัส พร้อมกรองตามชนิดแรมและความเร็วบัสได้ในหน้าหลัก",
    },
    "ssd": {
        "slug": "ssd",
        "name": "SSD",
        "emoji": "💾",
        "title": "ราคา SSD M.2 NVMe Gen4 วันนี้ 1TB 2TB เทียบ 3 ร้าน | PriceSpec",
        "desc": "เช็คราคา SSD Kingston NV3, WD Blue SN5000, Samsung 990 PRO, WD Black SN850X ความจุ 1TB และ 2TB เทียบราคาร้านไทย 3 ร้าน",
        "h2": "ราคา SSD ล่าสุดในไทย",
        "intro": "รวมราคา SSD M.2 NVMe Gen4 ความจุ 1TB–2TB จากแบรนด์หลัก เทียบราคาระหว่างร้านได้ทันที",
    },
    "psu": {
        "slug": "psu",
        "name": "พาวเวอร์ซัพพลาย",
        "emoji": "🔌",
        "title": "ราคา Power Supply PSU วันนี้ 650W 750W 850W 1000W | PriceSpec",
        "desc": "เช็คราคาพาวเวอร์ซัพพลาย Corsair CX650, RM850e, Thermaltake Smart BX1, ASUS TUF Gaming 1000W 80+ Bronze/Gold เทียบ 3 ร้านไทย",
        "h2": "ราคาพาวเวอร์ซัพพลาย (PSU) ล่าสุดในไทย",
        "intro": "รวมราคาพาวเวอร์ซัพพลายตั้งแต่ 650W ถึง 1000W ทั้ง 80+ Bronze และ Gold ใช้คู่กับหน้าจัดสเปคเพื่อคำนวณกำลังไฟที่ต้องใช้",
    },
    "case": {
        "slug": "case",
        "name": "เคสคอม",
        "emoji": "🖥️",
        "title": "ราคาเคสคอม PC Case วันนี้ ATX E-ATX เทียบ 3 ร้านไทย | PriceSpec",
        "desc": "เช็คราคาเคสคอมพิวเตอร์ Montech AIR 1000 LITE, Lian Li LANCOOL 217, NZXT H5 Flow, Thermaltake View 270 TG เทียบราคา 3 ร้าน",
        "h2": "ราคาเคสคอมพิวเตอร์ล่าสุดในไทย",
        "intro": "รวมราคาเคสคอมยอดนิยมทั้งขนาด ATX และ E-ATX พร้อมราคาเฉลี่ยและราคาแยกรายร้าน",
    },
    "console": {
        "slug": "console",
        "name": "เครื่องเกม",
        "emoji": "⭐",
        "title": "ราคาเครื่องเกม PS5 Switch 2 Xbox Steam Deck วันนี้ | PriceSpec",
        "desc": "เช็คราคาเครื่องเกม PlayStation 5 Slim, PS5 Pro, Nintendo Switch 2, Switch OLED, Xbox Series X/S, Steam Deck OLED, ROG Ally X, Meta Quest 3S ในไทย",
        "h2": "ราคาเครื่องเกมล่าสุดในไทย",
        "intro": "รวมราคาเครื่องเกมคอนโซลและเครื่องเกมพกพาที่ขายในไทย ทั้ง PlayStation, Xbox, Nintendo, Steam Deck และแว่น VR",
    },
}

SPEC_LABEL = {
    "vram": ("แรมการ์ดจอ", " GB"), "tdp": ("กินไฟ", " W"),
    "socket": ("ซ็อกเก็ต", ""), "ram": ("รองรับแรม", ""),
    "bus": ("บัส", " MHz"), "watt": ("กำลังไฟ", " W"),
    "size": ("ความจุ", ""), "form": ("ขนาด", ""),
}


def avg_price(p):
    now = [(s, hist[-1]["price"]) for s, hist in p["history"].items()]
    mid = round(sum(v for _, v in now) / len(now))
    cheapest = min(now, key=lambda x: x[1])
    return mid, sorted(now, key=lambda x: x[1]), cheapest


def fmt(n):
    return f"{n:,}"


def build_category(key, cfg, products, updated):
    rows = []
    ld_items = []
    for i, p in enumerate(products, 1):
        mid, stores, cheapest = avg_price(p)
        spec_bits = []
        for k, v in (p.get("specs") or {}).items():
            if k in SPEC_LABEL:
                lab, unit = SPEC_LABEL[k]
                spec_bits.append(f"{lab} {html.escape(str(v))}{unit}")
        store_rows = "".join(
            f'<li><span>{html.escape(s)}{" 🏆" if (s, v) == cheapest else ""}</span>'
            f'<b>{fmt(v)} ฿</b></li>'
            for s, v in stores
        )
        img = html.escape(p.get("image") or f"{BASE}/images/{key}.svg")
        name = html.escape(p["name"])
        est = ' <span class="est">⚠ ราคาประมาณการ</span>' if p.get("estimate") else ""
        rows.append(f"""
      <article class="item">
        <img src="{img}" alt="{name}" loading="lazy" width="120" height="120">
        <div class="info">
          <h3>{name}</h3>
          <p class="spec">{html.escape(' · '.join(spec_bits))}</p>
          <p class="price"><b>{fmt(mid)} ฿</b> <small>ราคาเฉลี่ย {len(stores)} ร้าน</small>{est}</p>
          <ul class="stores">{store_rows}</ul>
          <a class="btn" href="{html.escape(p.get('affiliate_url') or BASE)}" rel="nofollow sponsored" target="_blank">ดูดีลบน Shopee</a>
        </div>
      </article>""")
        ld_items.append({
            "@type": "ListItem",
            "position": i,
            "item": {
                "@type": "Product",
                "name": p["name"],
                "image": p.get("image") or f"{BASE}/images/{key}.svg",
                "offers": {
                    "@type": "AggregateOffer",
                    "priceCurrency": "THB",
                    "lowPrice": stores[0][1],
                    "highPrice": stores[-1][1],
                    "offerCount": len(stores),
                },
            },
        })

    nav_links = "".join(
        '<a href="{}/{}"{}>{} {}</a>'.format(
            BASE, c["slug"], ' class="on"' if k == key else "", c["emoji"], c["name"])
        for k, c in CATS.items()
    )

    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "ItemList", "name": cfg["h2"], "numberOfItems": len(products),
             "itemListElement": ld_items},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "PriceSpec", "item": BASE + "/"},
                {"@type": "ListItem", "position": 2, "name": cfg["name"],
                 "item": f'{BASE}/{cfg["slug"]}'},
            ]},
        ],
    }

    return f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(cfg["title"])}</title>
<meta name="description" content="{html.escape(cfg["desc"])}">
<link rel="canonical" href="{BASE}/{cfg['slug']}">
<meta property="og:type" content="website">
<meta property="og:locale" content="th_TH">
<meta property="og:site_name" content="PriceSpec">
<meta property="og:title" content="{html.escape(cfg["title"])}">
<meta property="og:description" content="{html.escape(cfg["desc"])}">
<meta property="og:url" content="{BASE}/{cfg['slug']}">
<meta property="og:image" content="{BASE}/icons/icon-512.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0d1117">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="48x48" href="/icons/favicon-48.png">
<link rel="apple-touch-icon" sizes="180x180" href="/icons/apple-touch-icon.png">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>
:root{{--bg:#0d1117;--card:#161b22;--card2:#1c2330;--border:#2d3748;--text:#e6edf3;--muted:#8b949e;--accent:#58e08c}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font-family:'Segoe UI',Tahoma,sans-serif;line-height:1.55}}
a{{color:inherit;text-decoration:none}}
.wrap{{max-width:1100px;margin:0 auto;padding:16px}}
header{{padding:22px 0 8px}}
h1{{font-size:1.5rem;display:flex;align-items:center;gap:12px;flex-wrap:wrap}}
h1 .g{{color:var(--accent)}}
h2{{font-size:1.15rem;margin:18px 0 6px}}
.lead{{color:var(--muted);font-size:.95rem;margin-bottom:6px}}
nav{{display:flex;gap:6px;overflow-x:auto;padding:12px 0;margin-bottom:6px}}
nav a{{white-space:nowrap;background:var(--card);border:1px solid var(--border);color:var(--muted);padding:8px 14px;border-radius:20px;font-size:.92rem}}
nav a.on{{background:var(--accent);color:#0d1117;font-weight:700;border-color:var(--accent)}}
.grid{{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));margin-top:12px}}
.item{{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:14px;display:flex;gap:14px}}
.item img{{width:120px;height:120px;object-fit:contain;background:#fff;border-radius:10px;flex:none}}
.info{{min-width:0;flex:1}}
.item h3{{font-size:1rem;margin-bottom:4px}}
.spec{{color:var(--muted);font-size:.83rem}}
.price{{margin:6px 0 4px}}
.price b{{color:var(--accent);font-size:1.25rem}}
.price small{{color:var(--muted);font-size:.78rem}}
.est{{color:#ffd43b;font-size:.75rem}}
.stores{{list-style:none;font-size:.85rem;border-top:1px solid var(--border);padding-top:6px;margin-top:6px}}
.stores li{{display:flex;justify-content:space-between;padding:2px 0;color:var(--muted)}}
.stores b{{color:var(--text)}}
.btn{{display:inline-block;margin-top:8px;background:var(--accent);color:#0d1117;font-weight:700;padding:7px 14px;border-radius:8px;font-size:.85rem}}
footer{{margin:34px 0 20px;color:var(--muted);font-size:.85rem;border-top:1px solid var(--border);padding-top:14px}}
footer a{{color:var(--accent)}}
.cta{{display:inline-block;margin-top:10px;border:1px solid var(--accent);color:var(--accent);padding:8px 16px;border-radius:8px;font-weight:600}}
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1><a href="{BASE}/"><img src="/logo-mark.svg" alt="โลโก้ PriceSpec" width="42" height="42" style="border-radius:10px;vertical-align:middle"></a>
  <a href="{BASE}/">Price<span class="g">Spec</span></a></h1>
  <p class="lead">เช็คราคาอุปกรณ์คอมและเครื่องเกม เทียบ 3 ร้านไทย · อัปเดตล่าสุด {updated}</p>
</header>
<nav>{nav_links}</nav>
<main>
  <h2>{cfg['emoji']} {html.escape(cfg['h2'])}</h2>
  <p class="lead">{html.escape(cfg['intro'])}</p>
  <a class="cta" href="{BASE}/#{cfg['slug']}">ดูกราฟราคาย้อนหลัง + ตั้งแจ้งเตือนลดราคา →</a>
  <div class="grid">{''.join(rows)}
  </div>
</main>
<footer>
  <p>ราคารวบรวมจาก JIB, Advice และ iHAVECPU อัปเดตอัตโนมัติทุกวันเสาร์ · ราคาอาจเปลี่ยนแปลงได้ โปรดตรวจสอบกับร้านค้าอีกครั้งก่อนสั่งซื้อ</p>
  <p style="margin-top:8px"><a href="{BASE}/">หน้าแรก</a> · <a href="{BASE}/#builder">จัดสเปคคอม</a> · <a href="{BASE}/#alerts">แจ้งเตือนราคา</a></p>
</footer>
</div>
</body>
</html>
"""


def main():
    with open(os.path.join(ROOT, "data", "prices.json"), encoding="utf-8") as f:
        data = json.load(f)
    updated = data.get("updated", str(datetime.date.today()))
    products = data["products"]

    made = []
    for key, cfg in CATS.items():
        items = [p for p in products if p["category"] == key]
        if not items:
            continue
        with open(os.path.join(ROOT, cfg["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(build_category(key, cfg, items, updated))
        made.append(cfg["slug"])
        print(f"  ✓ /{cfg['slug']}  ({len(items)} รายการ)")

    # sitemap
    urls = [(BASE + "/", "1.0")] + [(f"{BASE}/{s}", "0.8") for s in made]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, pr in urls:
        sm.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{updated}</lastmod>"
                  f"\n    <changefreq>weekly</changefreq>\n    <priority>{pr}</priority>\n  </url>")
    sm.append("</urlset>\n")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(sm))
    print(f"  ✓ sitemap.xml ({len(urls)} URL)")


if __name__ == "__main__":
    main()
