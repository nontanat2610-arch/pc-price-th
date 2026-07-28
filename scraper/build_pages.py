#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
สร้างหน้าเว็บแบบ static แยกตามหมวดสินค้า เพื่อให้ Google เก็บข้อมูล (index) ได้
รันหลัง scraper.py ทุกครั้ง -> จะได้หน้าที่มีราคาล่าสุดฝังอยู่ใน HTML จริง
"""
import json, os, html, datetime, urllib.parse

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
    "monitor": {
        "slug": "monitor",
        "name": "จอมอนิเตอร์",
        "emoji": "🖵",
        "title": "ราคาจอมอนิเตอร์ วันนี้ 24 27 32 นิ้ว 144Hz 165Hz | PriceSpec",
        "desc": "เช็คราคาจอคอมพิวเตอร์และจอเกมมิ่ง ASUS, MSI, Gigabyte, LG, Samsung ทั้ง 24, 27, 32 นิ้ว รีเฟรชเรต 144Hz 165Hz 180Hz 240Hz เทียบราคาร้านไทย",
        "h2": "ราคาจอมอนิเตอร์ล่าสุดในไทย",
        "intro": "รวมราคาจอคอมพิวเตอร์และจอเกมมิ่งทุกขนาด พร้อมระบุขนาดหน้าจอและรีเฟรชเรตให้เทียบง่าย",
    },
    "cooling": {
        "slug": "cooling",
        "name": "ชุดระบายความร้อน",
        "emoji": "❄",
        "title": "ราคาชุดน้ำ ชุดระบายความร้อนซีพียู AIO พัดลม CPU | PriceSpec",
        "desc": "เช็คราคาชุดน้ำ AIO 240 280 360 มม. และฮีตซิงก์พัดลมซีพียู จากแบรนด์ดัง เทียบราคาร้านคอมไทย อัปเดตทุกสัปดาห์",
        "h2": "ราคาชุดระบายความร้อนล่าสุดในไทย",
        "intro": "รวมราคาชุดน้ำปิด (AIO) และฮีตซิงก์ระบายความร้อนด้วยอากาศ สำหรับซีพียูทุกซ็อกเก็ต",
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
    "gen": ("อินเทอร์เฟซ", ""), "rating": ("มาตรฐาน", " 80+"), "hz": ("รีเฟรชเรต", " Hz"),
}


def load_aff():
    f = os.path.join(ROOT, "data", "affiliate.json")
    try:
        with open(f, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


AFF = load_aff()


def aff_link(p, price):
    """เลือกร้านที่จ่ายค่าคอมสูงสุดสำหรับสินค้าชิ้นนั้น
    Shopee 2% แต่ตันที่ 225฿ · Power Buy 3.15% ไม่มีเพดาน → ของแพงกว่า ~7,143฿ Power Buy ชนะ"""
    def payout(rate, cap):
        v = price * (rate or 0)
        return min(v, cap) if cap else v

    cands = []
    if p.get("affiliate_url"):
        cands.append((payout(AFF.get("shopee_rate", .02), AFF.get("shopee_cap", 225)),
                      p["affiliate_url"], "shopee"))

    aid, oid = AFF.get("involve_aff_id"), AFF.get("involve_powerbuy_offer_id")
    if aid and oid and p.get("powerbuy_url"):
        url = (f"https://invol.co/aff_m?offer_id={oid}&aff_id={aid}"
               f"&url={urllib.parse.quote(p['powerbuy_url'], safe='')}")
        cands.append((payout(AFF.get("powerbuy_rate", .0315), AFF.get("powerbuy_cap", 0)),
                      url, "powerbuy"))

    if not cands:
        return (p.get("source_url") or BASE), "direct"
    cands.sort(reverse=True)
    return cands[0][1], cands[0][2]


def ga_snippet():
    gid = AFF.get("ga4_id")
    if not gid:
        return ""
    return (f'<script async src="https://www.googletagmanager.com/gtag/js?id={gid}"></script>\n'
            f'<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}\n'
            f'gtag("js",new Date());gtag("config","{gid}");\n'
            'document.addEventListener("click",function(e){var a=e.target.closest("a[data-out]");'
            'if(a)gtag("event","outbound_click",{item:a.dataset.out,store:a.dataset.store||""})});</script>')


def avg_price(p):
    now = [(s, hist[-1]["price"]) for s, hist in p["history"].items()]
    mid = round(sum(v for _, v in now) / len(now))
    cheapest = min(now, key=lambda x: x[1])
    return mid, sorted(now, key=lambda x: x[1]), cheapest


def fmt(n):
    return f"{n:,}"


CARDS_PER_CAT = 48          # จำนวนการ์ดพร้อมรูปที่โชว์บนหน้าหมวด ที่เหลือเป็นลิงก์รายการ


def pslug(p):
    return p.get("slug") or p["id"]


def spec_line(p):
    bits = []
    for k, v in (p.get("specs") or {}).items():
        if k in SPEC_LABEL:
            lab, unit = SPEC_LABEL[k]
            bits.append(f"{lab} {v}{unit}")
    return " · ".join(bits)


def build_category(key, cfg, products, updated):
    rows = []
    ld_items = []
    for i, p in enumerate(products[:CARDS_PER_CAT], 1):
        mid, stores, cheapest = avg_price(p)
        spec_bits = []
        for k, v in (p.get("specs") or {}).items():
            if k in SPEC_LABEL:
                lab, unit = SPEC_LABEL[k]
                spec_bits.append(f"{lab} {v}{unit}")
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
        <a href="{BASE}/p/{pslug(p)}"><img src="{img}" alt="{name}" loading="lazy" width="120" height="120"></a>
        <div class="info">
          <h3><a href="{BASE}/p/{pslug(p)}">{name}</a></h3>
          <p class="spec">{html.escape(' · '.join(spec_bits))}</p>
          <p class="price"><b>{fmt(mid)} ฿</b> <small>ราคาเฉลี่ย {len(stores)} ร้าน</small>{est}</p>
          <ul class="stores">{store_rows}</ul>
          <a class="btn" href="{BASE}/p/{pslug(p)}">ดูราคาและกราฟ →</a>
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

    # รายการสินค้าทั้งหมดในหมวด (แบบลิงก์ล้วน) — ให้ Google ไต่เข้าถึงทุกหน้าสินค้าได้
    rest = products[CARDS_PER_CAT:]
    if rest:
        lis = "".join(
            '<li><a href="{}/p/{}">{}</a><b>{} ฿</b></li>'.format(
                BASE, pslug(q), html.escape(q["name"]), fmt(avg_price(q)[0]))
            for q in rest)
        all_list = (f'<h2>สินค้า{html.escape(cfg["name"])}ทั้งหมด ({len(products)} รายการ)</h2>'
                    f'<ul class="alllist">{lis}</ul>')
    else:
        all_list = ""

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
{ga_snippet()}
<script>(function(){{var r=document.documentElement;
var b=document.createElement('button');b.id='themebtn';b.title='สลับโทนสว่าง/มืด';
function set(t){{r.dataset.theme=t;b.textContent=t==='light'?'☾':'☀';}}
var s=null;try{{s=localStorage.getItem('theme');}}catch(e){{}}
set(s||(window.matchMedia('(prefers-color-scheme: light)').matches?'light':'dark'));
b.onclick=function(){{var t=r.dataset.theme==='light'?'dark':'light';set(t);try{{localStorage.setItem('theme',t);}}catch(e){{}}}};
document.addEventListener('DOMContentLoaded',function(){{document.body.appendChild(b);}});}})();</script>
<style>
:root{{--bg:#0d1117;--card:#161b22;--card2:#1c2330;--border:#2d3748;--text:#e6edf3;--muted:#8b949e;--accent:#58e08c;--accent2:#4dabf7;--glow1:rgba(88,224,140,.20);--glow2:rgba(77,171,247,.17);--bgTop:#0a0f16;--grid:rgba(255,255,255,.038);--heroA:rgba(32,43,58,.78);--heroB:rgba(15,20,29,.82);--heroBd:rgba(88,224,140,.22);--nameA:#ffffff;--navBg:rgba(13,17,23,.88);--cardA:rgba(28,35,48,.9);--cardB:rgba(19,24,33,.92)}}
html[data-theme="light"]{{--bg:#f4f7fb;--card:#fff;--card2:#eef2f7;--border:#d8e0ea;--text:#101720;
  --muted:#5b6b7d;--accent:#0f9d58;--accent2:#1668c9;--glow1:rgba(15,157,88,.13);--glow2:rgba(22,104,201,.11);
  --bgTop:#fff;--grid:rgba(16,23,32,.05);--heroA:rgba(255,255,255,.95);--heroB:rgba(240,246,252,.95);
  --heroBd:rgba(15,157,88,.28);--nameA:#0b3d2c;--navBg:rgba(244,247,251,.92);--cardA:#fff;--cardB:#f7fafd}}
html[data-theme="light"] .item img,html[data-theme="light"] .panel img{{background:#fff}}
html[data-theme="light"] .btn{{color:#fff}}
#themebtn{{position:fixed;top:14px;right:14px;z-index:50;background:var(--card);border:1px solid var(--border);
  color:var(--text);width:40px;height:40px;border-radius:11px;cursor:pointer;font-size:1.15rem;line-height:1}}
#themebtn:hover{{border-color:var(--accent)}}

*{{box-sizing:border-box;margin:0;padding:0}}
body{{
  color:var(--text);font-family:'Segoe UI',Tahoma,sans-serif;line-height:1.55;min-height:100vh;
  background:
    radial-gradient(900px 500px at 10% -10%, var(--glow1), transparent 60%),
    radial-gradient(820px 460px at 90% -6%, var(--glow2), transparent 62%),
    linear-gradient(180deg,var(--bgTop) 0%, var(--bg) 42%);
  background-attachment:fixed;background-repeat:no-repeat;
}}
body::before{{
  content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
  background-image:
    linear-gradient(var(--grid) 1px, transparent 1px),
    linear-gradient(90deg, var(--grid) 1px, transparent 1px);
  background-size:58px 58px;
  -webkit-mask-image:radial-gradient(120% 70% at 50% 0%, #000 0%, transparent 72%);
  mask-image:radial-gradient(120% 70% at 50% 0%, #000 0%, transparent 72%);
}}
a{{color:inherit;text-decoration:none}}
.wrap{{max-width:1100px;margin:0 auto;padding:16px;position:relative;z-index:1}}
.hero{{
  position:relative;overflow:hidden;margin:14px 0 4px;padding:24px 26px 22px;border-radius:22px;
  background:linear-gradient(145deg, var(--heroA), var(--heroB));
  border:1px solid var(--heroBd);
  box-shadow:0 26px 70px -30px rgba(0,0,0,.95), inset 0 1px 0 rgba(255,255,255,.07);
  -webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);
}}
.hero::after{{content:"";position:absolute;width:440px;height:440px;right:-150px;top:-220px;pointer-events:none;
  background:radial-gradient(circle, rgba(88,224,140,.30), transparent 62%)}}
.hero::before{{content:"";position:absolute;width:400px;height:400px;left:-170px;bottom:-250px;pointer-events:none;
  background:radial-gradient(circle, rgba(77,171,247,.24), transparent 62%)}}
h1{{font-size:1.5rem;display:flex;align-items:center;gap:14px;flex-wrap:wrap;position:relative}}
h1 img{{border-radius:13px;filter:drop-shadow(0 10px 22px rgba(88,224,140,.38))}}
h1 .name{{font-size:2.05rem;font-weight:800;letter-spacing:-.6px;line-height:1.1;
  background:linear-gradient(92deg,var(--nameA) 0%,var(--accent) 48%,var(--accent2) 100%);
  -webkit-background-clip:text;background-clip:text;color:transparent}}
h2{{font-size:1.3rem;margin:22px 0 6px}}
.lead{{color:var(--muted);font-size:.95rem;margin-bottom:6px;position:relative}}
.stats{{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px;position:relative}}
.stat{{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.10);
  border-radius:999px;padding:6px 14px;font-size:.83rem;color:var(--muted);white-space:nowrap}}
.stat b{{color:var(--accent);font-weight:700}}
.stat.blue b{{color:var(--accent2)}}
@media(max-width:560px){{.hero{{padding:20px 18px;border-radius:18px}} h1 .name{{font-size:1.65rem}}}}
nav{{display:flex;gap:6px;overflow-x:auto;padding:12px 0;margin-bottom:6px;position:sticky;top:0;
  background:var(--navBg);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);z-index:10}}
nav a{{white-space:nowrap;background:var(--card);border:1px solid var(--border);color:var(--muted);padding:8px 14px;border-radius:20px;font-size:.92rem}}
nav a.on{{background:var(--accent);color:#fff;font-weight:700;border-color:var(--accent);box-shadow:0 6px 18px -6px rgba(88,224,140,.7)}}
.grid{{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));margin-top:12px}}
.item{{background:linear-gradient(160deg,var(--cardA),var(--cardB));border:1px solid var(--border);border-radius:14px;padding:14px;display:flex;gap:14px;
  box-shadow:0 14px 34px -22px rgba(0,0,0,.9);transition:border-color .18s, transform .18s}}
.item:hover{{border-color:rgba(88,224,140,.45);transform:translateY(-2px)}}
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
.btn{{display:inline-block;margin-top:8px;background:var(--accent);color:#fff;font-weight:700;padding:7px 14px;border-radius:8px;font-size:.85rem}}
footer{{margin:34px 0 20px;color:var(--muted);font-size:.85rem;border-top:1px solid var(--border);padding-top:14px}}
footer a{{color:var(--accent)}}
.cta{{display:inline-block;margin-top:10px;border:1px solid var(--accent);color:var(--accent);padding:8px 16px;border-radius:8px;font-weight:600}}
.alllist{{list-style:none;margin-top:10px;columns:2;column-gap:26px}}
.alllist li{{display:flex;justify-content:space-between;gap:14px;padding:7px 0;border-bottom:1px solid var(--border);
  break-inside:avoid;font-size:.88rem;color:var(--muted)}}
.alllist a{{color:var(--text)}}
.alllist a:hover{{color:var(--accent)}}
.alllist b{{color:var(--accent);white-space:nowrap}}
@media(max-width:760px){{.alllist{{columns:1}}}}
</style>
</head>
<body>
<div class="wrap">
<header class="hero">
  <h1><a href="{BASE}/"><img src="/logo-mark.svg" alt="โลโก้ PriceSpec" width="58" height="58"></a>
  <a href="{BASE}/" class="name">PriceSpec</a></h1>
  <div class="stats">
    <span class="stat"><b>{len(products)}</b> รายการในหมวด{html.escape(cfg['name'])}</span>
    <span class="stat blue"><b>3</b> ร้าน · JIB · Advice · iHAVECPU</span>
    <span class="stat">ล่าสุด <b>{updated}</b></span>
  </div>
  <p class="lead" style="margin-top:14px">เช็คราคาอุปกรณ์คอมและเครื่องเกมในไทย เทียบราคาเฉลี่ยพร้อมราคาแยกรายร้าน อัปเดตอัตโนมัติทุกวันเสาร์</p>
</header>
<nav>{nav_links}</nav>
<main>
  <h2>{cfg['emoji']} {html.escape(cfg['h2'])}</h2>
  <p class="lead">{html.escape(cfg['intro'])}</p>
  <a class="cta" href="{BASE}/#{cfg['slug']}">ดูกราฟราคาย้อนหลัง + ตั้งแจ้งเตือนลดราคา →</a>
  <div class="grid">{''.join(rows)}
  </div>
  {all_list}
</main>
<footer>
  <p>ราคารวบรวมจาก JIB, Advice และ iHAVECPU อัปเดตอัตโนมัติทุกวันเสาร์ · ราคาอาจเปลี่ยนแปลงได้ โปรดตรวจสอบกับร้านค้าอีกครั้งก่อนสั่งซื้อ</p>
  <p style="margin-top:8px"><a href="{BASE}/">หน้าแรก</a> · <a href="{BASE}/#builder">จัดสเปคคอม</a> ·
     <a href="{BASE}/about">เกี่ยวกับเรา</a> · <a href="{BASE}/privacy">นโยบายความเป็นส่วนตัว</a> ·
     <a href="{BASE}/contact">ติดต่อเรา</a></p>
  <p style="margin-top:6px;font-size:.8rem">เว็บนี้มีลิงก์แนะนำ (affiliate) — เราอาจได้ค่าตอบแทนเมื่อคุณซื้อผ่านลิงก์ โดยคุณไม่ต้องจ่ายเพิ่ม
     <a href="{BASE}/contact#affiliate">อ่านรายละเอียด</a></p>
</footer>
</div>
</body>
</html>
"""


PRODUCT_CSS = """
:root{--bg:#0d1117;--card:#161b22;--card2:#1c2330;--border:#2d3748;--text:#e6edf3;--muted:#8b949e;--accent:#58e08c;--accent2:#4dabf7;--glow1:rgba(88,224,140,.20);--glow2:rgba(77,171,247,.17);--bgTop:#0a0f16;--heroA:rgba(32,43,58,.78);--heroB:rgba(15,20,29,.85);--heroBd:rgba(88,224,140,.20);--nameA:#ffffff;--cardA:rgba(28,35,48,.9);--cardB:rgba(19,24,33,.92)}
html[data-theme="light"]{--bg:#f4f7fb;--card:#fff;--card2:#eef2f7;--border:#d8e0ea;--text:#101720;--muted:#5b6b7d;--accent:#0f9d58;--accent2:#1668c9;--glow1:rgba(15,157,88,.13);--glow2:rgba(22,104,201,.11);--bgTop:#fff;--heroA:rgba(255,255,255,.95);--heroB:rgba(240,246,252,.95);--heroBd:rgba(15,157,88,.28);--nameA:#0b3d2c;--cardA:#fff;--cardB:#f7fafd}
html[data-theme="light"] .btn{color:#fff}
html[data-theme="light"] .doc p,html[data-theme="light"] .doc ul{color:#2b3947}
#themebtn{position:fixed;top:14px;right:14px;z-index:50;background:var(--card);border:1px solid var(--border);color:var(--text);width:40px;height:40px;border-radius:11px;cursor:pointer;font-size:1.15rem;line-height:1}
#themebtn:hover{border-color:var(--accent)}
*{box-sizing:border-box;margin:0;padding:0}
body{color:var(--text);font-family:'Segoe UI',Tahoma,sans-serif;line-height:1.55;min-height:100vh;
  background:radial-gradient(900px 500px at 10% -10%,var(--glow1),transparent 60%),
    radial-gradient(820px 460px at 90% -6%,var(--glow2),transparent 62%),
    linear-gradient(180deg,var(--bgTop) 0%,var(--bg) 42%);
  background-attachment:fixed;background-repeat:no-repeat}
a{color:inherit;text-decoration:none}
.wrap{max-width:900px;margin:0 auto;padding:16px;position:relative;z-index:1}
.top{display:flex;align-items:center;gap:10px;padding:16px 0 6px}
.top .name{font-size:1.35rem;font-weight:800;background:linear-gradient(92deg,var(--nameA),var(--accent) 55%,var(--accent2));
  -webkit-background-clip:text;background-clip:text;color:transparent}
.crumb{color:var(--muted);font-size:.85rem;margin:6px 0 14px}
.crumb a:hover{color:var(--accent)}
.panel{background:linear-gradient(145deg,var(--heroA),var(--heroB));
  border:1px solid var(--heroBd);border-radius:20px;padding:22px;display:flex;gap:22px;flex-wrap:wrap;
  box-shadow:0 26px 70px -34px rgba(0,0,0,.95)}
.panel img{width:230px;height:230px;object-fit:contain;background:#fff;border-radius:14px;flex:none}
.info{flex:1;min-width:250px}
h1{font-size:1.35rem;line-height:1.35;margin-bottom:8px}
.spec{color:var(--muted);font-size:.88rem;margin-bottom:12px}
.big{font-size:2.1rem;font-weight:800;color:var(--accent);line-height:1.1}
.bigsub{color:var(--muted);font-size:.83rem;margin-bottom:12px}
table{width:100%;border-collapse:collapse;font-size:.92rem;margin-top:6px}
th,td{text-align:left;padding:9px 8px;border-bottom:1px solid var(--border)}
th{color:var(--muted);font-weight:500;font-size:.82rem}
td.p{text-align:right;font-weight:700;white-space:nowrap}
tr.best td{color:var(--accent)}
.btn{display:inline-block;margin-top:14px;background:var(--accent);color:#fff;font-weight:700;
  padding:10px 20px;border-radius:9px;font-size:.92rem}
.btn.ghost{background:transparent;border:1px solid var(--accent);color:var(--accent);margin-left:8px}
h2{font-size:1.05rem;margin:28px 0 8px}
.rel{list-style:none;display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px}
.rel li{background:linear-gradient(160deg,var(--cardA),var(--cardB));border:1px solid var(--border);border-radius:11px;padding:11px 13px;font-size:.86rem}
.rel li:hover{border-color:rgba(88,224,140,.45)}
.rel b{color:var(--accent);display:block;margin-top:3px}
footer{margin:34px 0 20px;color:var(--muted);font-size:.83rem;border-top:1px solid var(--border);padding-top:14px}
footer a{color:var(--accent)}
@media(max-width:620px){.panel{padding:16px;gap:14px}.panel img{width:100%;height:200px}}
"""


def build_product(p, cfg, related, updated):
    mid, stores, cheapest = avg_price(p)
    name = html.escape(p["name"])
    img = html.escape(p.get("image") or f"{BASE}/images/{p['category']}.svg")
    spec = spec_line(p)
    url = f"{BASE}/p/{pslug(p)}"

    rows = "".join(
        '<tr class="{}"><td>{}{}</td><td class="p">{} ฿</td></tr>'.format(
            "best" if (s, v) == cheapest else "", html.escape(s),
            " 🏆 ถูกที่สุด" if (s, v) == cheapest else "", fmt(v))
        for s, v in stores)

    rel = "".join(
        '<li><a href="{}/p/{}">{}<b>{} ฿</b></a></li>'.format(
            BASE, pslug(q), html.escape(q["name"][:60]), fmt(avg_price(q)[0]))
        for q in related)

    buy, store_tag = aff_link(p, mid)
    desc = f"ราคา {p['name']} วันนี้ {fmt(mid)} บาท"
    if len(stores) > 1:
        desc += f" ถูกสุดที่ {cheapest[0]} {fmt(cheapest[1])} บาท เทียบ {len(stores)} ร้าน"
    if spec:
        desc += f" · {spec}"
    desc += f" · อัปเดต {updated}"
    desc = desc[:300]

    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Product", "name": p["name"], "image": p.get("image") or "",
             "category": cfg["name"], "url": url,
             "offers": {"@type": "AggregateOffer", "priceCurrency": "THB",
                        "lowPrice": stores[0][1], "highPrice": stores[-1][1],
                        "offerCount": len(stores), "availability": "https://schema.org/InStock"}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "PriceSpec", "item": BASE + "/"},
                {"@type": "ListItem", "position": 2, "name": cfg["name"], "item": f'{BASE}/{cfg["slug"]}'},
                {"@type": "ListItem", "position": 3, "name": p["name"], "item": url}]},
        ],
    }

    return f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ราคา {name} วันนี้ {fmt(mid)} บาท | PriceSpec</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="product">
<meta property="og:locale" content="th_TH">
<meta property="og:site_name" content="PriceSpec">
<meta property="og:title" content="ราคา {name} — {fmt(mid)} บาท">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#0d1117">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="48x48" href="/icons/favicon-48.png">
<link rel="apple-touch-icon" sizes="180x180" href="/icons/apple-touch-icon.png">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
{ga_snippet()}
<script>(function(){{var r=document.documentElement;
var b=document.createElement('button');b.id='themebtn';b.title='สลับโทนสว่าง/มืด';
function set(t){{r.dataset.theme=t;b.textContent=t==='light'?'☾':'☀';}}
var s=null;try{{s=localStorage.getItem('theme');}}catch(e){{}}
set(s||(window.matchMedia('(prefers-color-scheme: light)').matches?'light':'dark'));
b.onclick=function(){{var t=r.dataset.theme==='light'?'dark':'light';set(t);try{{localStorage.setItem('theme',t);}}catch(e){{}}}};
document.addEventListener('DOMContentLoaded',function(){{document.body.appendChild(b);}});}})();</script>
<style>{PRODUCT_CSS}</style>
</head>
<body>
<div class="wrap">
<div class="top">
  <a href="{BASE}/"><img src="/logo-mark.svg" alt="โลโก้ PriceSpec" width="38" height="38" style="border-radius:9px"></a>
  <a href="{BASE}/" class="name">PriceSpec</a>
</div>
<p class="crumb"><a href="{BASE}/">หน้าแรก</a> › <a href="{BASE}/{cfg['slug']}">{cfg['emoji']} {html.escape(cfg['name'])}</a> › {name}</p>

<article class="panel">
  <img src="{img}" alt="{name}" width="230" height="230">
  <div class="info">
    <h1>ราคา {name}</h1>
    <p class="spec">{html.escape(spec) if spec else html.escape(cfg['name'])}</p>
    <div class="big">{fmt(mid)} ฿</div>
    <div class="bigsub">ราคาเฉลี่ยจาก {len(stores)} ร้าน · อัปเดต {updated}</div>
    <table>
      <thead><tr><th>ร้านค้า</th><th style="text-align:right">ราคา</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    <a class="btn" href="{html.escape(buy)}" rel="nofollow sponsored" target="_blank"
       data-out="{pslug(p)}" data-store="{store_tag}">ดูดีล / สั่งซื้อ</a>
    <a class="btn ghost" href="{BASE}/#{cfg['slug']}">ตั้งแจ้งเตือนราคาลด</a>
  </div>
</article>

<h2>{cfg['emoji']} {html.escape(cfg['name'])}รุ่นอื่นในช่วงราคาใกล้เคียง</h2>
<ul class="rel">{rel}</ul>

<footer>
  <p>ราคารวบรวมจาก JIB, Advice และ iHAVECPU · อัปเดตอัตโนมัติทุกวันเสาร์ · ราคาอาจเปลี่ยนแปลงได้ โปรดตรวจสอบกับร้านค้าก่อนสั่งซื้อ</p>
  <p style="margin-top:8px"><a href="{BASE}/{cfg['slug']}">ดูราคา{html.escape(cfg['name'])}ทั้งหมด</a> ·
     <a href="{BASE}/">หน้าแรก</a> · <a href="{BASE}/about">เกี่ยวกับเรา</a> ·
     <a href="{BASE}/privacy">นโยบายความเป็นส่วนตัว</a> · <a href="{BASE}/contact">ติดต่อเรา</a></p>
  <p style="margin-top:6px;font-size:.8rem">เว็บนี้มีลิงก์แนะนำ (affiliate) — เราอาจได้ค่าตอบแทนเมื่อคุณซื้อผ่านลิงก์ โดยคุณไม่ต้องจ่ายเพิ่ม
     <a href="{BASE}/contact#affiliate">อ่านรายละเอียด</a></p>
</footer>
</div>
</body>
</html>
"""


CONTACT_EMAIL = AFF.get("contact_email") or "nontanat2610@gmail.com"

# หน้ามาตรฐานที่เครือข่าย affiliate ตรวจก่อนอนุมัติ (About / นโยบาย / ติดต่อ)
STATIC_PAGES = {
    "about": {
        "title": "เกี่ยวกับ PriceSpec — เว็บเทียบราคาอุปกรณ์คอมในไทย",
        "desc": "PriceSpec คือเว็บเทียบราคาอุปกรณ์คอมพิวเตอร์และเครื่องเกมในไทย รวบรวมราคาจากร้านค้าไทยอัตโนมัติทุกสัปดาห์ ใช้งานฟรี",
        "h1": "เกี่ยวกับ PriceSpec",
        "body": """
<p>PriceSpec เป็นเว็บไซต์เทียบราคาอุปกรณ์คอมพิวเตอร์และเครื่องเกมสำหรับผู้ซื้อในประเทศไทย
เกิดจากปัญหาที่เจอเอง — เวลาจะซื้อการ์ดจอหรือประกอบคอมสักเครื่อง ต้องเปิดเว็บร้านทีละร้านเพื่อเทียบราคา
และไม่มีทางรู้ว่าราคาที่เห็นวันนี้ถูกหรือแพงกว่าสัปดาห์ก่อน</p>

<h2>เราทำอะไร</h2>
<ul>
  <li><b>รวบรวมราคาจริงจากร้านค้าไทย</b> — JIB, Advice และ iHAVECPU</li>
  <li><b>แสดงราคาเฉลี่ยพร้อมราคาแยกรายร้าน</b> ให้เห็นว่าร้านไหนถูกที่สุดในขณะนั้น</li>
  <li><b>เก็บประวัติราคา</b> เพื่อให้รู้ว่าราคาปัจจุบันถูกจริงหรือแค่ดูเหมือนถูก</li>
  <li><b>แจ้งเตือนเมื่อราคาต่ำกว่าที่ตั้งไว้</b> — ตั้งค่าเก็บไว้ในเครื่องผู้ใช้เอง</li>
  <li><b>เครื่องมือจัดสเปคคอม</b> ตรวจความเข้ากันได้ของซ็อกเก็ต ชนิดแรม และกำลังไฟ</li>
</ul>

<h2>ข้อมูลอัปเดตอย่างไร</h2>
<p>ระบบดึงราคาอัตโนมัติ<b>ทุกวันเสาร์ เวลา 05:00 น.</b> แล้วสร้างหน้าเว็บใหม่ทั้งหมดเอง
ไม่มีการแก้ราคาด้วยมือ ราคาที่เห็นจึงเป็นราคาที่ดึงมาจากหน้าเว็บร้านค้าโดยตรง ณ เวลานั้น</p>
<p>ปัจจุบันมีสินค้าในระบบมากกว่า 2,200 รายการ ใน 10 หมวด ได้แก่ การ์ดจอ ซีพียู เมนบอร์ด แรม SSD
พาวเวอร์ซัพพลาย เคส จอมอนิเตอร์ ชุดระบายความร้อน และเครื่องเกม</p>

<h2>ข้อจำกัดที่อยากให้ทราบ</h2>
<p>ราคาอาจเปลี่ยนแปลงระหว่างรอบอัปเดต และบางรายการอาจมีข้อมูลจากร้านเดียว
<b>โปรดตรวจสอบราคาและสต๊อกกับร้านค้าอีกครั้งก่อนตัดสินใจซื้อเสมอ</b>
PriceSpec ไม่ได้ขายสินค้าเอง และไม่มีส่วนเกี่ยวข้องกับการสั่งซื้อหรือการจัดส่ง</p>

<h2>ใครทำเว็บนี้</h2>
<p>PriceSpec ดูแลโดยบุคคลธรรมดาในประเทศไทย ผู้สนใจด้านไอทีและการประกอบคอมพิวเตอร์
เว็บนี้ใช้งานได้ฟรี ไม่มีค่าสมาชิก และไม่ต้องสมัครบัญชี</p>
""",
    },
    "privacy": {
        "title": "นโยบายความเป็นส่วนตัว | PriceSpec",
        "desc": "นโยบายความเป็นส่วนตัวของ PriceSpec — เราไม่เก็บข้อมูลส่วนบุคคล ไม่ต้องสมัครสมาชิก และไม่ขายข้อมูลผู้ใช้",
        "h1": "นโยบายความเป็นส่วนตัว",
        "body": """
<p class="upd">ปรับปรุงล่าสุด: 28 กรกฎาคม 2569</p>

<h2>สรุปสั้น ๆ</h2>
<p>PriceSpec <b>ไม่ต้องสมัครสมาชิก ไม่ขอข้อมูลส่วนบุคคล และไม่ขายข้อมูลผู้ใช้ให้ใคร</b></p>

<h2>ข้อมูลที่เก็บ</h2>
<ul>
  <li><b>ข้อมูลที่เก็บไว้ในเครื่องคุณเอง (Local Storage)</b> — รายการแจ้งเตือนราคาและสเปคคอมที่คุณจัดไว้
      ข้อมูลนี้อยู่ในเบราว์เซอร์ของคุณเท่านั้น ไม่ถูกส่งมาที่เรา และลบได้เองโดยล้างข้อมูลเว็บไซต์</li>
  <li><b>สถิติการใช้งานแบบไม่ระบุตัวตน</b> — เราอาจใช้ Google Analytics เพื่อดูจำนวนผู้เข้าชมและหน้าที่ได้รับความนิยม
      ข้อมูลนี้เป็นภาพรวม ไม่สามารถระบุตัวบุคคลได้</li>
  <li><b>ข้อมูลทางเทคนิคของผู้ให้บริการโฮสติ้ง</b> — Vercel อาจบันทึกที่อยู่ IP และชนิดเบราว์เซอร์ตามปกติของการให้บริการเว็บ</li>
</ul>

<h2>ข้อมูลที่ไม่เก็บ</h2>
<p>เราไม่เก็บชื่อ อีเมล เบอร์โทร ที่อยู่ ข้อมูลบัตรเครดิต หรือข้อมูลการชำระเงินใด ๆ
เพราะเว็บนี้ไม่มีระบบสมาชิกและไม่มีการขายสินค้า</p>

<h2>คุกกี้และลิงก์ไปเว็บอื่น</h2>
<p>เมื่อคุณกดลิงก์ไปยังร้านค้า เว็บปลายทางอาจวางคุกกี้ของตัวเองเพื่อบันทึกที่มาของผู้เข้าชม
ซึ่งอยู่นอกเหนือการควบคุมของเรา โปรดอ่านนโยบายความเป็นส่วนตัวของร้านค้านั้น ๆ</p>

<h2>สิทธิของคุณ</h2>
<p>ตามพระราชบัญญัติคุ้มครองข้อมูลส่วนบุคคล (PDPA) คุณมีสิทธิสอบถาม ขอแก้ไข หรือขอลบข้อมูลของคุณ
เนื่องจากเราไม่ได้เก็บข้อมูลที่ระบุตัวตน จึงมักไม่มีข้อมูลให้ลบ แต่หากมีข้อสงสัยติดต่อเราได้ตลอด</p>

<h2>การเปลี่ยนแปลงนโยบาย</h2>
<p>หากมีการแก้ไขนโยบายนี้ เราจะอัปเดตวันที่ด้านบนของหน้า</p>
""",
    },
    "contact": {
        "title": "ติดต่อเรา และการเปิดเผยเรื่องลิงก์แนะนำ | PriceSpec",
        "desc": "ช่องทางติดต่อ PriceSpec สำหรับแจ้งราคาผิด เสนอสินค้าที่อยากให้เพิ่ม หรือติดต่อเรื่องธุรกิจ พร้อมการเปิดเผยเรื่องลิงก์ affiliate",
        "h1": "ติดต่อเรา",
        "body": """
<p>มีอะไรอยากบอก ทักมาได้เลย เราอ่านทุกฉบับ</p>

<p class="mail">อีเมล: <a href="mailto:{email}">{email}</a></p>

<h2>เรื่องที่ติดต่อเข้ามาบ่อย</h2>
<ul>
  <li><b>ราคาผิดหรือสินค้าไม่มีขายแล้ว</b> — บอกชื่อรุ่นมาได้เลย เราจะตรวจสอบและแก้ในรอบอัปเดตถัดไป</li>
  <li><b>อยากให้เพิ่มสินค้าหรือหมวดใหม่</b> — ยินดีรับข้อเสนอเสมอ</li>
  <li><b>ร้านค้าที่อยากให้เพิ่มเข้าระบบเทียบราคา</b></li>
  <li><b>ติดต่อเรื่องธุรกิจหรือความร่วมมือ</b></li>
</ul>

<h2 id="affiliate">การเปิดเผยเรื่องลิงก์แนะนำ (Affiliate Disclosure)</h2>
<p>PriceSpec ให้บริการฟรีและไม่มีค่าสมาชิก เราจึงมีรายได้จาก<b>ลิงก์แนะนำ (affiliate link)</b> เป็นหลัก</p>
<p>เมื่อคุณกดปุ่มไปยังร้านค้าผ่านเว็บของเราแล้วเกิดการสั่งซื้อ เราอาจได้รับค่าตอบแทนเล็กน้อยจากร้านค้านั้น
<b>โดยคุณไม่ต้องจ่ายเพิ่มแม้แต่บาทเดียว</b> ราคาที่คุณจ่ายเท่ากับการเข้าเว็บร้านค้าโดยตรง</p>
<p>สิ่งที่เรายึดถือ:</p>
<ul>
  <li>ราคาที่แสดงเป็นราคาที่ดึงจากหน้าเว็บร้านค้าจริง <b>เราไม่แก้ไขหรือจัดอันดับตามค่าตอบแทน</b></li>
  <li>ร้านที่ถูกที่สุดจะถูกทำเครื่องหมาย 🏆 เสมอ ไม่ว่าร้านนั้นจะจ่ายค่าตอบแทนให้เราหรือไม่</li>
  <li>ลิงก์แนะนำทุกลิงก์กำกับด้วย <code>rel="nofollow sponsored"</code> ตามแนวทางของ Google</li>
</ul>
""",
    },
}


def build_static(key, cfg, updated):
    nav_links = "".join(
        '<a href="{}/{}">{} {}</a>'.format(BASE, c["slug"], c["emoji"], c["name"])
        for c in CATS.values())
    body = cfg["body"].replace("{email}", CONTACT_EMAIL)
    return f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(cfg['title'])}</title>
<meta name="description" content="{html.escape(cfg['desc'])}">
<link rel="canonical" href="{BASE}/{key}">
<meta property="og:type" content="website">
<meta property="og:locale" content="th_TH">
<meta property="og:site_name" content="PriceSpec">
<meta property="og:title" content="{html.escape(cfg['title'])}">
<meta property="og:description" content="{html.escape(cfg['desc'])}">
<meta property="og:url" content="{BASE}/{key}">
<meta name="theme-color" content="#0d1117">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="48x48" href="/icons/favicon-48.png">
<link rel="apple-touch-icon" sizes="180x180" href="/icons/apple-touch-icon.png">
{ga_snippet()}
<script>(function(){{var r=document.documentElement;
var b=document.createElement('button');b.id='themebtn';b.title='สลับโทนสว่าง/มืด';
function set(t){{r.dataset.theme=t;b.textContent=t==='light'?'☾':'☀';}}
var s=null;try{{s=localStorage.getItem('theme');}}catch(e){{}}
set(s||(window.matchMedia('(prefers-color-scheme: light)').matches?'light':'dark'));
b.onclick=function(){{var t=r.dataset.theme==='light'?'dark':'light';set(t);try{{localStorage.setItem('theme',t);}}catch(e){{}}}};
document.addEventListener('DOMContentLoaded',function(){{document.body.appendChild(b);}});}})();</script>
<style>{PRODUCT_CSS}
.doc{{background:linear-gradient(145deg,var(--heroA),var(--heroB));
  border:1px solid var(--heroBd);border-radius:20px;padding:30px 34px;margin-top:6px}}
.doc h1{{font-size:1.7rem;margin-bottom:14px}}
.doc h2{{font-size:1.12rem;margin:26px 0 8px;color:var(--accent)}}
.doc p{{margin:10px 0;color:#c6d2de}}
.doc ul{{margin:10px 0 10px 20px;color:#c6d2de}}
.doc li{{margin:7px 0}}
.doc b{{color:var(--text)}}
.doc a{{color:var(--accent2)}}
.doc a:hover{{text-decoration:underline}}
.doc code{{background:rgba(255,255,255,.07);padding:2px 7px;border-radius:5px;font-size:.88em}}
.upd{{color:var(--muted);font-size:.86rem}}
.mail{{font-size:1.15rem;background:rgba(88,224,140,.09);border:1px solid rgba(88,224,140,.3);
  border-radius:12px;padding:14px 18px;margin:16px 0!important}}
nav{{display:flex;gap:6px;overflow-x:auto;padding:12px 0;margin-bottom:6px;scrollbar-width:none}}
nav::-webkit-scrollbar{{height:0}}
nav a{{white-space:nowrap;background:var(--card);border:1px solid var(--border);color:var(--muted);
  padding:8px 14px;border-radius:20px;font-size:.92rem}}
@media(max-width:620px){{.doc{{padding:22px 18px}}}}
</style>
</head>
<body>
<div class="wrap">
<div class="top">
  <a href="{BASE}/"><img src="/logo-mark.svg" alt="โลโก้ PriceSpec" width="38" height="38" style="border-radius:9px"></a>
  <a href="{BASE}/" class="name">PriceSpec</a>
</div>
<p class="crumb"><a href="{BASE}/">หน้าแรก</a> › {html.escape(cfg['h1'])}</p>
<nav>{nav_links}</nav>
<article class="doc">
  <h1>{html.escape(cfg['h1'])}</h1>
  {body}
</article>
<footer>
  <p>ราคารวบรวมจาก JIB, Advice และ iHAVECPU · อัปเดตอัตโนมัติทุกวันเสาร์ · อัปเดตล่าสุด {updated}</p>
  <p style="margin-top:8px"><a href="{BASE}/">หน้าแรก</a> · <a href="{BASE}/about">เกี่ยวกับเรา</a> ·
     <a href="{BASE}/privacy">นโยบายความเป็นส่วนตัว</a> · <a href="{BASE}/contact">ติดต่อเรา</a></p>
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

    pdir = os.path.join(ROOT, "p")
    os.makedirs(pdir, exist_ok=True)
    for old in os.listdir(pdir):                 # ลบหน้าสินค้าที่เลิกขายแล้ว
        if old.endswith(".html"):
            try:
                os.remove(os.path.join(pdir, old))
            except OSError:
                pass

    made, prod_urls = [], []
    for key, cfg in CATS.items():
        items = [p for p in products if p["category"] == key]
        if not items:
            continue
        items.sort(key=lambda q: avg_price(q)[0])            # ถูก → แพง
        with open(os.path.join(ROOT, cfg["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(build_category(key, cfg, items, updated))
        made.append(cfg["slug"])

        # หน้าสินค้ารายตัว + ลิงก์ไปรุ่นที่ราคาใกล้เคียง (ช่วยให้ Google ไต่ต่อได้)
        for i, p in enumerate(items):
            lo, hi = max(0, i - 3), min(len(items), i + 5)
            related = [q for q in items[lo:hi] if q is not p][:6]
            with open(os.path.join(pdir, pslug(p) + ".html"), "w", encoding="utf-8") as f:
                f.write(build_product(p, cfg, related, updated))
            prod_urls.append(f"{BASE}/p/{pslug(p)}")
        print(f"  ✓ /{cfg['slug']}  ({len(items)} รายการ → {len(items)} หน้าสินค้า)")

    # sitemap
    urls = ([(BASE + "/", "1.0")] + [(f"{BASE}/{s}", "0.8") for s in made]
            + [(f"{BASE}/{k}", "0.5") for k in STATIC_PAGES]
            + [(u, "0.6") for u in prod_urls])
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, pr in urls:
        sm.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{updated}</lastmod>"
                  f"\n    <changefreq>weekly</changefreq>\n    <priority>{pr}</priority>\n  </url>")
    sm.append("</urlset>\n")
    for key, cfg in STATIC_PAGES.items():
        with open(os.path.join(ROOT, key + ".html"), "w", encoding="utf-8") as f:
            f.write(build_static(key, cfg, updated))
    print(f"  ✓ /about /privacy /contact")

    pub = {k: v for k, v in AFF.items() if not k.startswith("_")}
    with open(os.path.join(ROOT, "data", "affiliate.js"), "w", encoding="utf-8") as f:
        f.write("window.AFFILIATE = " + json.dumps(pub, ensure_ascii=False) + ";")

    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(sm))
    print(f"  ✓ sitemap.xml ({len(urls)} URL)")


if __name__ == "__main__":
    main()
