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
        "title": "ราคาการ์ดจอวันนี้ 2026 พร้อมกราฟราคาย้อนหลัง | PriceSpec",
        "desc": "เช็คราคาการ์ดจอล่าสุด RTX 5060 5070 5070 Ti 5080 5090, Radeon RX 9070 XT, Intel Arc B580 จากร้านค้าปลีกไทย พร้อมกราฟราคาย้อนหลังและราคาเฉลี่ย อัปเดตทุกสัปดาห์",
        "h2": "ราคาการ์ดจอล่าสุดในไทย",
        "intro": "รวมราคาการ์ดจอ NVIDIA GeForce RTX 50 Series, AMD Radeon RX 9000 Series และ Intel Arc จากร้านค้าปลีกไทย แสดงราคาเฉลี่ยพร้อมกราฟย้อนหลัง เพื่อให้เห็นว่าราคาตอนนี้อยู่จุดสูงหรือจุดต่ำ",
    },
    "cpu": {
        "slug": "cpu",
        "name": "ซีพียู",
        "emoji": "🧠",
        "title": "ราคาซีพียู CPU วันนี้ AMD Ryzen / Intel Core พร้อมกราฟราคา | PriceSpec",
        "desc": "เช็คราคาซีพียู AMD Ryzen 5600, 9600X, 9800X3D และ Intel Core i5-14400F, Core Ultra 5 245K, i9-14900K จากร้านค้าปลีกไทย พร้อมกราฟราคาย้อนหลัง",
        "h2": "ราคาซีพียู (CPU) ล่าสุดในไทย",
        "intro": "รวมราคาซีพียู AMD Ryzen และ Intel Core จากร้านค้าปลีกไทยในหน้าเดียว พร้อมราคาย้อนหลัง ดูซ็อกเก็ตประกอบการเลือกเมนบอร์ดได้ทันที",
    },
    "mainboard": {
        "slug": "mainboard",
        "name": "เมนบอร์ด",
        "emoji": "🔲",
        "title": "ราคาเมนบอร์ด Mainboard วันนี้ AM4 AM5 LGA1700 | PriceSpec",
        "desc": "เช็คราคาเมนบอร์ด MSI, ASUS, ASRock ทั้ง B550, B650, X870, B760, B860 จากร้านค้าปลีกไทย พร้อมบอกซ็อกเก็ตและชนิดแรมที่รองรับ",
        "h2": "ราคาเมนบอร์ดล่าสุดในไทย",
        "intro": "รวมราคาเมนบอร์ดยอดนิยมทั้งฝั่ง AMD (AM4/AM5) และ Intel (LGA1700/LGA1851) ระบุซ็อกเก็ตและชนิดแรมที่รองรับ ช่วยให้จับคู่กับซีพียูได้ถูกต้อง",
    },
    "ram": {
        "slug": "ram",
        "name": "แรม",
        "emoji": "📏",
        "title": "ราคาแรม RAM DDR4 DDR5 วันนี้ พร้อมกราฟราคาย้อนหลัง | PriceSpec",
        "desc": "เช็คราคาแรม Kingston FURY, Corsair Vengeance, G.SKILL Trident Z5 ทั้ง DDR4 3200 และ DDR5 5600 6000 6400 จากร้านค้าปลีกไทย พร้อมกราฟราคาย้อนหลัง",
        "h2": "ราคาแรม (RAM) ล่าสุดในไทย",
        "intro": "รวมราคาแรมคอมพิวเตอร์ DDR4 และ DDR5 หลายบัส พร้อมกรองตามชนิดแรมและความเร็วบัสได้ในหน้าหลัก",
    },
    "ssd": {
        "slug": "ssd",
        "name": "SSD",
        "emoji": "💾",
        "title": "ราคา SSD M.2 NVMe Gen4 วันนี้ 1TB 2TB พร้อมกราฟราคา | PriceSpec",
        "desc": "เช็คราคา SSD Kingston NV3, WD Blue SN5000, Samsung 990 PRO, WD Black SN850X ความจุ 1TB และ 2TB จากร้านค้าปลีกไทย พร้อมกราฟราคาย้อนหลัง",
        "h2": "ราคา SSD ล่าสุดในไทย",
        "intro": "รวมราคา SSD M.2 NVMe Gen4 ความจุ 1TB–2TB จากแบรนด์หลัก ดูราคาย้อนหลังได้ทันที",
    },
    "psu": {
        "slug": "psu",
        "name": "พาวเวอร์ซัพพลาย",
        "emoji": "🔌",
        "title": "ราคา Power Supply PSU วันนี้ 650W 750W 850W 1000W | PriceSpec",
        "desc": "เช็คราคาพาวเวอร์ซัพพลาย Corsair CX650, RM850e, Thermaltake Smart BX1, ASUS TUF Gaming 1000W 80+ Bronze/Gold จากร้านค้าปลีกไทย พร้อมกราฟราคาย้อนหลัง",
        "h2": "ราคาพาวเวอร์ซัพพลาย (PSU) ล่าสุดในไทย",
        "intro": "รวมราคาพาวเวอร์ซัพพลายตั้งแต่ 650W ถึง 1000W ทั้ง 80+ Bronze และ Gold ใช้คู่กับหน้าจัดสเปคเพื่อคำนวณกำลังไฟที่ต้องใช้",
    },
    "case": {
        "slug": "case",
        "name": "เคสคอม",
        "emoji": "🖥️",
        "title": "ราคาเคสคอม PC Case วันนี้ ATX E-ATX พร้อมกราฟราคาย้อนหลัง | PriceSpec",
        "desc": "เช็คราคาเคสคอมพิวเตอร์ Montech AIR 1000 LITE, Lian Li LANCOOL 217, NZXT H5 Flow, Thermaltake View 270 TG จากร้านค้าปลีกไทย พร้อมกราฟราคาย้อนหลัง",
        "h2": "ราคาเคสคอมพิวเตอร์ล่าสุดในไทย",
        "intro": "รวมราคาเคสคอมยอดนิยมทั้งขนาด ATX และ E-ATX พร้อมราคาเฉลี่ยและกราฟราคาย้อนหลัง",
    },
    "monitor": {
        "slug": "monitor",
        "name": "จอมอนิเตอร์",
        "emoji": "🖵",
        "title": "ราคาจอมอนิเตอร์ วันนี้ 24 27 32 นิ้ว 144Hz 165Hz | PriceSpec",
        "desc": "เช็คราคาจอคอมพิวเตอร์และจอเกมมิ่ง ASUS, MSI, Gigabyte, LG, Samsung ทั้ง 24, 27, 32 นิ้ว รีเฟรชเรต 144Hz 165Hz 180Hz 240Hz จากร้านค้าปลีกไทย พร้อมกราฟราคาย้อนหลัง",
        "h2": "ราคาจอมอนิเตอร์ล่าสุดในไทย",
        "intro": "รวมราคาจอคอมพิวเตอร์และจอเกมมิ่งทุกขนาด พร้อมระบุขนาดหน้าจอและรีเฟรชเรตให้เทียบง่าย",
    },
    "cooling": {
        "slug": "cooling",
        "name": "ชุดระบายความร้อน",
        "emoji": "❄",
        "title": "ราคาชุดน้ำ ชุดระบายความร้อนซีพียู AIO พัดลม CPU | PriceSpec",
        "desc": "เช็คราคาชุดน้ำ AIO 240 280 360 มม. และฮีตซิงก์พัดลมซีพียู จากแบรนด์ดัง จากร้านค้าปลีกไทย พร้อมกราฟราคาย้อนหลัง อัปเดตทุกสัปดาห์",
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


CARDS_PER_CAT = 48          # การ์ดพร้อมรูปบนหน้าหมวด ที่เหลือเป็นลิสต์ลิงก์
REAL_FROM = "2026-07-25"    # ก่อนวันนี้ = ข้อมูลจำลอง → วาดเส้นประ


def pslug(p):
    return p.get("slug") or p["id"]


def spec_line(p):
    bits = []
    for k, v in (p.get("specs") or {}).items():
        if k in SPEC_LABEL:
            lab, unit = SPEC_LABEL[k]
            bits.append(f"{lab} {v}{unit}")
    return " · ".join(bits)


def series(p):
    """ราคาเฉลี่ยรายวันจากทุกร้าน (ตัดให้ยาวเท่ากัน)"""
    arrs = [a for a in p["history"].values() if a]
    if not arrs:
        return []
    n = min(len(a) for a in arrs)
    out = []
    for i in range(n):
        col = [a[len(a) - n + i] for a in arrs]
        out.append({"date": col[0]["date"],
                    "price": round(sum(c["price"] for c in col) / len(col))})
    return out


def stat(p):
    """ตัวเลขทุกอย่างที่การ์ดต้องใช้ — คิดครั้งเดียว"""
    rows = [{"store": s, "price": h[-1]["price"] if h else None,
             "date": h[-1]["date"] if h else None} for s, h in p["history"].items()]
    ok = [r for r in rows if r["price"]]
    cheap = min(ok, key=lambda r: r["price"]) if ok else None
    dear = max(ok, key=lambda r: r["price"]) if ok else None
    ser = series(p)
    ps = [x["price"] for x in ser]
    now = cheap["price"] if cheap else 0
    if len(ps) > 3:
        lo, avg = min(ps), sum(ps) / len(ps)
        if now <= lo * 1.005:
            badge = ("low", f"ต่ำสุดในรอบ {len(ps)} วัน")
        elif now < avg * 0.97:
            badge = ("low", "ถูกกว่าค่าเฉลี่ย")
        elif now > avg * 1.03:
            badge = ("high", "แพงกว่าค่าเฉลี่ย")
        else:
            badge = ("mid", "ราคาปกติ")
    else:
        badge = ("mid", "เพิ่งเริ่มเก็บราคา")
    return {"rows": rows, "ok": ok, "cheap": cheap, "dear": dear, "ser": ser,
            "badge": badge, "save": (dear["price"] - cheap["price"]) if (dear and cheap) else 0,
            "now": now}


def spark(ser, w=76, h=26, sw=1.7):
    """เส้นราคาย่อ — ช่วงข้อมูลจำลองเป็นเส้นประ"""
    if len(ser) < 2:
        return ""
    ps = [x["price"] for x in ser]
    mn, mx = min(ps), max(ps)
    rg = (mx - mn) or 1
    X = lambda i: i / (len(ps) - 1) * (w - 2) + 1
    Y = lambda v: h - 1 - (v - mn) / rg * (h - 2)
    pts = [f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(ps)]
    cut = next((i for i, x in enumerate(ser) if x["date"] >= REAL_FROM), 0)
    col = "var(--up)" if ps[-1] > ps[0] else "var(--down)"
    out = f'<svg class="spark" width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true">'
    if cut > 0:
        out += (f'<polyline points="{" ".join(pts[:cut+1])}" fill="none" stroke="{col}" '
                f'stroke-width="{sw}" stroke-dasharray="2 2" opacity=".45"/>')
    out += (f'<polyline points="{" ".join(pts[cut:])}" fill="none" stroke="{col}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    return out


def big_chart(ser, w=680, h=200):
    """กราฟราคาย้อนหลังบนหน้าสินค้า — เส้นประ = ข้อมูลจำลอง พร้อมป้ายกำกับบนกราฟ"""
    if len(ser) < 2:
        return '<p class="muted">ยังไม่มีประวัติราคาเพียงพอ — เริ่มเก็บแล้ว กราฟจะขึ้นสัปดาห์หน้า</p>'
    ps = [x["price"] for x in ser]
    mn, mx = min(ps), max(ps)
    rg = (mx - mn) or 1
    pad = 34
    X = lambda i: pad + i / (len(ps) - 1) * (w - pad - 12)
    Y = lambda v: 14 + (1 - (v - mn) / rg) * (h - 46)
    pts = [f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(ps)]
    cut = next((i for i, x in enumerate(ser) if x["date"] >= REAL_FROM), 0)
    col = "var(--up)" if ps[-1] > ps[0] else "var(--down)"
    g = f'<svg viewBox="0 0 {w} {h}" width="100%" height="{h}" role="img" aria-label="กราฟราคาย้อนหลัง">'
    for k in range(4):                                    # เส้นตารางแนวนอน + ป้ายราคา
        v = mn + rg * k / 3
        y = Y(v)
        g += (f'<line x1="{pad}" y1="{y:.1f}" x2="{w-12}" y2="{y:.1f}" stroke="var(--border)" stroke-width="1"/>'
              f'<text x="4" y="{y+4:.1f}" font-size="10" fill="var(--text3)">{round(v/1000,1)}k</text>')
    if cut > 0:
        g += (f'<polyline points="{" ".join(pts[:cut+1])}" fill="none" stroke="{col}" '
              f'stroke-width="2" stroke-dasharray="4 3" opacity=".5"/>'
              f'<line x1="{X(cut):.1f}" y1="10" x2="{X(cut):.1f}" y2="{h-30}" stroke="var(--border2)" stroke-dasharray="3 3"/>'
              f'<text x="{X(cut)-4:.1f}" y="{h-16}" font-size="10" fill="var(--text3)" text-anchor="end">ข้อมูลจำลอง</text>'
              f'<text x="{X(cut)+4:.1f}" y="{h-16}" font-size="10" fill="var(--down)">เก็บจริง</text>')
    g += (f'<polyline points="{" ".join(pts[cut:])}" fill="none" stroke="{col}" stroke-width="2.2" '
          f'stroke-linecap="round" stroke-linejoin="round"/>'
          f'<circle cx="{X(len(ps)-1):.1f}" cy="{Y(ps[-1]):.1f}" r="4" fill="{col}"/>'
          f'<text x="{pad}" y="{h-2}" font-size="10" fill="var(--text3)">{ser[0]["date"]}</text>'
          f'<text x="{w-12}" y="{h-2}" font-size="10" fill="var(--text3)" text-anchor="end">{ser[-1]["date"]}</text></svg>')
    return g


def ago(d, updated):
    if not d:
        return ""
    try:
        a = datetime.date.fromisoformat(d)
        b = datetime.date.fromisoformat(updated)
        n = (b - a).days
    except Exception:
        return d
    return "วันนี้" if n <= 0 else ("เมื่อวาน" if n == 1 else f"{n} วันที่แล้ว")


# ═══════════════════ ระบบดีไซน์ (ใช้ร่วมทุกหน้า) ═══════════════════
SHELL_CSS = """
:root{--bg:#0D1117;--surface:#161B22;--surface2:#1B222B;--border:#252C36;--border2:#323B47;
--text:#E6EDF3;--text2:#9AA7B4;--text3:#6E7C8C;--accent:#3FB6FF;--accent-ink:#04121C;
--down:#3FB950;--up:#F0603E;--warn:#D29922;--downBg:rgba(63,185,80,.12);--upBg:rgba(240,96,62,.12);
--warnBg:rgba(210,153,34,.12);--accentBg:rgba(63,182,255,.10);--r-card:12px;--r-btn:8px}
html[data-theme="light"]{--bg:#F7F9FC;--surface:#FFFFFF;--surface2:#F1F4F8;--border:#DCE3EC;--border2:#C6D0DC;
--text:#0E1620;--text2:#54606E;--text3:#7C8899;--accent:#0A6FC2;--accent-ink:#FFFFFF;
--down:#1A7F37;--up:#C2410C;--warn:#8A6100;--downBg:rgba(26,127,55,.10);--upBg:rgba(194,65,12,.10);
--warnBg:rgba(138,97,0,.10);--accentBg:rgba(10,111,194,.08)}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);line-height:1.55;
 font-family:'IBM Plex Sans Thai','Segoe UI',Tahoma,sans-serif;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
.num{font-variant-numeric:tabular-nums;font-feature-settings:"tnum" 1}
.wrap{max-width:1200px;margin:0 auto;padding:0 16px}
.muted{color:var(--text2);font-size:.9rem}
header{position:sticky;top:0;z-index:60;background:color-mix(in srgb,var(--bg) 88%,transparent);
 backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border-bottom:1px solid var(--border)}
.hbar{display:flex;align-items:center;gap:12px;height:60px}
.logo{display:flex;align-items:center;gap:9px;font-weight:700;font-size:1.05rem;letter-spacing:-.2px}
.logo img{width:30px;height:30px;border-radius:8px}
.logo i{color:var(--accent);font-style:normal}
.hspace{flex:1}
.gohome{height:38px;padding:0 15px;border:1px solid var(--border);border-radius:var(--r-btn);
 display:inline-flex;align-items:center;font-size:.87rem;color:var(--text2)}
.gohome:hover{border-color:var(--accent);color:var(--accent)}
#themebtn{width:38px;height:38px;border:1px solid var(--border);background:var(--surface);
 border-radius:var(--r-btn);cursor:pointer;color:var(--text);font-size:1rem}
#themebtn:hover{border-color:var(--accent)}
.crumb{color:var(--text3);font-size:.83rem;padding:16px 0 4px}
.crumb a:hover{color:var(--accent)}
nav{display:flex;gap:8px;overflow-x:auto;padding:12px 0 4px;scrollbar-width:none}
nav::-webkit-scrollbar{height:0}
nav a{white-space:nowrap;height:36px;padding:0 13px;background:var(--surface);border:1px solid var(--border);
 border-radius:99px;font-size:.86rem;color:var(--text2);display:inline-flex;align-items:center}
nav a:hover{border-color:var(--border2)}
nav a.on{background:var(--accent);color:var(--accent-ink);border-color:var(--accent);font-weight:600}
h1{font-size:1.6rem;font-weight:700;letter-spacing:-.4px;line-height:1.3}
h2{font-size:1.12rem;font-weight:700;margin:26px 0 10px}
.lead{color:var(--text2);font-size:.95rem;margin-top:8px;max-width:70ch}
.trust{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:16px 0 4px;padding:11px 13px;
 background:var(--surface);border:1px solid var(--border);border-radius:var(--r-card)}
.tchip{display:flex;align-items:center;gap:7px;font-size:.81rem;color:var(--text2);white-space:nowrap}
.tchip b{color:var(--text);font-weight:600}
.tsep{width:1px;height:18px;background:var(--border)}
.dot{width:7px;height:7px;border-radius:50%;background:var(--down);animation:pulse 2.4s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(63,185,80,.5)}70%{box-shadow:0 0 0 7px rgba(63,185,80,0)}100%{box-shadow:0 0 0 0 rgba(63,185,80,0)}}
.slogo{display:inline-flex;align-items:center;height:20px;padding:0 7px;border-radius:4px;font-size:.7rem;
 font-weight:700;border:1px solid var(--border2);color:var(--text2)}
.slogo.jib{color:#E8442E;border-color:rgba(232,68,46,.45)}
.slogo.adv{color:#3FB6FF;border-color:rgba(63,182,255,.45)}
.slogo.ihv{color:#F0A72E;border-color:rgba(240,167,46,.45)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(292px,1fr));gap:14px;margin-top:14px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-card);padding:14px;
 display:flex;flex-direction:column;gap:9px;transition:transform .16s,border-color .16s}
.card:hover{transform:translateY(-2px);border-color:var(--border2)}
.cimg{height:132px;display:grid;place-items:center;background:var(--surface2);border-radius:9px;overflow:hidden}
.cimg img{max-height:88%;max-width:88%;object-fit:contain}
.cname{font-size:.9rem;font-weight:600;line-height:1.35;height:2.7em;overflow:hidden;
 display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.cname:hover{color:var(--accent)}
.priceline{display:flex;align-items:center;gap:9px;flex-wrap:wrap}
.price{font-size:1.8rem;font-weight:700;letter-spacing:-.8px;line-height:1.1}
.price .baht{font-size:1.05rem;font-weight:600;opacity:.55;margin-left:2px}
.save{font-size:.79rem;font-weight:600;color:var(--down);background:var(--downBg);padding:2px 7px;border-radius:5px}
.ctx{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.badge{font-size:.75rem;font-weight:600;padding:2px 8px;border-radius:5px;white-space:nowrap}
.badge.low{background:var(--downBg);color:var(--down)}
.badge.mid{background:var(--surface2);color:var(--text2)}
.badge.high{background:var(--upBg);color:var(--up)}
.badge.warn{background:var(--warnBg);color:var(--warn);cursor:help}
.stores{border-top:1px solid var(--border);padding-top:8px;display:flex;flex-direction:column;gap:5px}
.srow{display:flex;align-items:center;justify-content:space-between;gap:8px;font-size:.82rem;color:var(--text2)}
.srow.best{color:var(--text)}.srow.best .sp{color:var(--down);font-weight:700}
.srow.none{opacity:.42}.srow .sp{font-weight:600}
.stamp{font-size:.72rem;color:var(--text3)}
.btns{display:flex;gap:8px;margin-top:2px}
.btn{height:42px;border-radius:var(--r-btn);border:1px solid transparent;cursor:pointer;font-size:.88rem;
 font-weight:600;display:inline-flex;align-items:center;justify-content:center;gap:6px;padding:0 18px}
.btn.primary{background:var(--accent);color:var(--accent-ink);flex:1}
.btn.primary:hover{filter:brightness(1.08)}
.btn.ghost{background:transparent;border-color:var(--border2);color:var(--text2)}
.btn.ghost:hover{border-color:var(--accent);color:var(--accent)}
.aff{font-size:.7rem;color:var(--text3);text-align:center}
.aff a{color:var(--text3);text-decoration:underline}
.alllist{list-style:none;margin-top:12px;columns:2;column-gap:26px}
.alllist li{display:flex;justify-content:space-between;gap:14px;padding:8px 0;border-bottom:1px solid var(--border);
 break-inside:avoid;font-size:.87rem;color:var(--text2)}
.alllist a{color:var(--text)}.alllist a:hover{color:var(--accent)}
.alllist b{color:var(--down);white-space:nowrap}
footer{margin-top:44px;border-top:1px solid var(--border);padding:24px 0 34px;font-size:.85rem;color:var(--text3)}
footer a{color:var(--text2)}footer a:hover{color:var(--accent)}
.fcols{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}
@media(max-width:760px){h1{font-size:1.35rem}.alllist{columns:1}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""

THEME_JS = """<script>(function(){var r=document.documentElement;
function set(t){r.dataset.theme=t;var b=document.getElementById('themebtn');if(b)b.textContent=t==='light'?'\\u263e':'\\u2600';
var m=document.querySelector('meta[name=theme-color]');if(m)m.content=t==='light'?'#F7F9FC':'#0D1117';}
var s=null;try{s=localStorage.getItem('theme');}catch(e){}
set(s||(window.matchMedia('(prefers-color-scheme: light)').matches?'light':'dark'));
document.addEventListener('click',function(e){if(e.target.id==='themebtn'){
var t=r.dataset.theme==='light'?'dark':'light';set(t);try{localStorage.setItem('theme',t);}catch(err){}}});})();</script>"""

FONT = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;600;700&display=swap" rel="stylesheet">')


def shell_head(title, desc, canon, extra_css="", ld=None):
    return f"""<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website"><meta property="og:locale" content="th_TH">
<meta property="og:site_name" content="PriceSpec">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{BASE}/icons/icon-512.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0D1117">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="48x48" href="/icons/favicon-48.png">
<link rel="apple-touch-icon" sizes="180x180" href="/icons/apple-touch-icon.png">
{FONT}
{'<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>' if ld else ''}
{ga_snippet()}
{THEME_JS}
<style>{SHELL_CSS}{extra_css}</style>"""


def shell_header():
    return f"""<header><div class="wrap hbar">
  <a href="{BASE}/" class="logo"><img src="/logo-mark.svg" alt="PriceSpec">Price<i>Spec</i></a>
  <span class="hspace"></span>
  <a class="gohome" href="{BASE}/">ค้นหาสินค้า</a>
  <button id="themebtn" title="สลับโทนสว่าง/มืด">☀</button>
</div></header>"""


def shell_nav(active=None):
    return '<nav>' + "".join(
        '<a href="{}/{}"{}>{} {}</a>'.format(BASE, c["slug"], ' class="on"' if k == active else "",
                                             c["emoji"], c["name"])
        for k, c in CATS.items()) + '</nav>'


def shell_footer(updated):
    cats = " · ".join(f'<a href="{BASE}/{c["slug"]}">ราคา{c["name"]}</a>' for c in CATS.values())
    return f"""<footer><div class="wrap">
  <div class="fcols">{cats}</div>
  <p>ราคารวบรวมจากร้านค้าปลีกในประเทศไทย · อัปเดตอัตโนมัติทุกวันเสาร์ ตี 5 · อัปเดตล่าสุด {updated}</p>
  <p style="margin-top:8px"><a href="{BASE}/">หน้าแรก</a> · <a href="{BASE}/about">เกี่ยวกับเรา</a> ·
     <a href="{BASE}/privacy">นโยบายความเป็นส่วนตัว</a> · <a href="{BASE}/contact">ติดต่อเรา</a> ·
     <a href="{BASE}/contact#affiliate">การเปิดเผยลิงก์แนะนำ</a></p>
</div></footer>"""


def trust_bar(n, label, updated):
    return f"""<div class="trust">
  <span class="tchip"><b class="num">{n:,}</b> {label}</span><span class="tsep"></span>
  <span class="tchip"><span class="slogo jib">กราฟราคาย้อนหลัง</span><span class="slogo adv">ต่ำสุด 30 วัน</span><span class="slogo ihv">แจ้งเตือนราคา</span></span>
  <span class="tsep"></span>
  <span class="tchip"><span class="dot"></span> อัปเดตล่าสุด <b>{updated} · 05:00</b></span>
  <span class="tsep"></span><span class="tchip">ไม่มีค่าใช้จ่ายแอบแฝง</span>
</div>"""


def product_card(p, updated):
    s = stat(p)
    slug, name = pslug(p), html.escape(p["name"])
    img = html.escape(p.get("image") or f"/images/{p['category']}.svg")
    buy, store = aff_link(p, s["now"])
    rows = ""
    for nm in ("JIB", "Advice", "iHAVECPU"):
        r = next((x for x in s["rows"] if x["store"] == nm), None)
        if not r or not r["price"]:
            rows += f'<div class="srow none"><span>{nm}</span><span>ไม่มีข้อมูล</span></div>'
        else:
            best = s["cheap"] and r["store"] == s["cheap"]["store"] and len(s["ok"]) > 1
            rows += (f'<div class="srow{" best" if best else ""}"><span>{nm}{" 🏆" if best else ""}</span>'
                     f'<span class="sp num">{fmt(r["price"])} ฿</span></div>')
    est = ('<span class="badge warn" title="ราคานี้เป็นการประมาณการ ยังไม่ได้เชื่อมข้อมูลร้านค้าโดยตรง">⚠ ประมาณการ</span>'
           if p.get("estimate") else "")
    save = f'<span class="save">ถูกกว่าอีกร้าน {fmt(s["save"])} ฿</span>' if s["save"] > 0 else ""
    return f"""<article class="card">
  <a class="cimg" href="{BASE}/p/{slug}"><img src="{img}" alt="{name}" loading="lazy"></a>
  <a class="cname" href="{BASE}/p/{slug}">{name}</a>
  <div class="priceline"><span class="price num">{fmt(s['now'])}<span class="baht">฿</span></span>{save}</div>
  <div class="ctx">{spark(s['ser'])}<span class="badge {s['badge'][0]}">{s['badge'][1]}</span>{est}</div>
  <div class="stores">{rows}</div>
  <div class="stamp">ราคาถูกสุดจาก {s['cheap']['store'] if s['cheap'] else '—'} · อัปเดต {ago(s['cheap']['date'] if s['cheap'] else None, updated)}</div>
  <div class="btns"><a class="btn primary" href="{html.escape(buy)}" target="_blank"
     rel="nofollow sponsored noopener" data-out="{slug}" data-store="{store}">ดูราคา / ซื้อ</a>
    <a class="btn ghost" href="{BASE}/#alerts" title="ตั้งแจ้งเตือนราคา">🔔</a></div>
  <div class="aff">ลิงก์แนะนำ — <a href="{BASE}/contact#affiliate">เราอาจได้ค่าตอบแทน คุณไม่จ่ายเพิ่ม</a></div>
</article>"""


def build_category(key, cfg, products, updated):
    cards = "".join(product_card(p, updated) for p in products[:CARDS_PER_CAT])
    rest = products[CARDS_PER_CAT:]
    more = ""
    if rest:
        lis = "".join(
            '<li><a href="{}/p/{}">{}</a><b class="num">{} ฿</b></li>'.format(
                BASE, pslug(q), html.escape(q["name"]), fmt(stat(q)["now"])) for q in rest)
        more = (f'<h2>สินค้า{html.escape(cfg["name"])}ทั้งหมด ({len(products):,} รายการ)</h2>'
                f'<ul class="alllist">{lis}</ul>')
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "ItemList", "name": cfg["h2"], "numberOfItems": len(products),
         "itemListElement": [{"@type": "ListItem", "position": i, "item": {
             "@type": "Product", "name": p["name"], "image": p.get("image") or "",
             "url": f"{BASE}/p/{pslug(p)}",
             "offers": {"@type": "AggregateOffer", "priceCurrency": "THB",
                        "lowPrice": stat(p)["ok"][0]["price"] if stat(p)["ok"] else 0,
                        "highPrice": stat(p)["dear"]["price"] if stat(p)["dear"] else 0,
                        "offerCount": len(stat(p)["ok"])}}}
             for i, p in enumerate(products[:CARDS_PER_CAT], 1)]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "PriceSpec", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": cfg["name"], "item": f'{BASE}/{cfg["slug"]}'}]}]}
    return f"""<!DOCTYPE html>
<html lang="th"><head>{shell_head(cfg['title'], cfg['desc'], f"{BASE}/{cfg['slug']}", "", ld)}</head>
<body>{shell_header()}
<main class="wrap">
  <p class="crumb"><a href="{BASE}/">หน้าแรก</a> › {html.escape(cfg['name'])}</p>
  <h1>{cfg['emoji']} {html.escape(cfg['h2'])}</h1>
  <p class="lead">{html.escape(cfg['intro'])}</p>
  {trust_bar(len(products), 'รายการในหมวดนี้', updated)}
  {shell_nav(key)}
  <div class="grid">{cards}</div>
  {more}
</main>
{shell_footer(updated)}
</body></html>"""


PRODUCT_CSS = """
.panel{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-card);
 padding:20px;display:flex;gap:22px;flex-wrap:wrap;margin-top:6px}
.panel .pimg{width:230px;height:230px;display:grid;place-items:center;background:var(--surface2);
 border-radius:10px;flex:none}
.panel .pimg img{max-width:88%;max-height:88%;object-fit:contain}
.pinfo{flex:1;min-width:270px}
.pbig{font-size:2.4rem;font-weight:700;letter-spacing:-1.2px;line-height:1.05;margin:10px 0 2px}
.pbig .baht{font-size:1.2rem;font-weight:600;opacity:.55;margin-left:3px}
table.st{width:100%;border-collapse:collapse;font-size:.9rem;margin-top:14px}
table.st th{text-align:left;font-size:.76rem;color:var(--text3);font-weight:600;padding:8px 10px;
 background:var(--surface2);border-bottom:1px solid var(--border)}
table.st th.r,table.st td.r{text-align:right}
table.st td{padding:9px 10px;border-bottom:1px solid var(--border)}
table.st tr:last-child td{border-bottom:none}
table.st td.best{background:var(--downBg);color:var(--down);font-weight:700}
.chartbox{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-card);padding:16px;margin-top:16px}
.rel{list-style:none;display:grid;grid-template-columns:repeat(auto-fill,minmax(212px,1fr));gap:10px;margin-top:10px}
.rel li{background:var(--surface);border:1px solid var(--border);border-radius:11px;padding:11px 13px;font-size:.85rem}
.rel li:hover{border-color:var(--accent)}
.rel b{color:var(--down);display:block;margin-top:3px}
@media(max-width:620px){.panel{padding:14px;gap:14px}.panel .pimg{width:100%;height:200px}.pbig{font-size:2rem}}
"""


def build_product(p, cfg, related, updated):
    s = stat(p)
    name, slug = html.escape(p["name"]), pslug(p)
    img = html.escape(p.get("image") or f"/images/{p['category']}.svg")
    sp = spec_line(p)
    url = f"{BASE}/p/{slug}"
    buy, store = aff_link(p, s["now"])

    trs = ""
    for nm in ("JIB", "Advice", "iHAVECPU"):
        r = next((x for x in s["rows"] if x["store"] == nm), None)
        if not r or not r["price"]:
            trs += f'<tr><td>{nm}</td><td class="r" style="color:var(--text3)">ไม่มีข้อมูล</td><td class="r" style="color:var(--text3)">—</td></tr>'
        else:
            best = s["cheap"] and r["store"] == s["cheap"]["store"] and len(s["ok"]) > 1
            trs += (f'<tr><td>{nm}{" 🏆" if best else ""}</td>'
                    f'<td class="r num{" best" if best else ""}">{fmt(r["price"])} ฿</td>'
                    f'<td class="r" style="color:var(--text3);font-size:.8rem">{ago(r["date"], updated)}</td></tr>')

    rel = "".join('<li><a href="{}/p/{}">{}<b class="num">{} ฿</b></a></li>'.format(
        BASE, pslug(q), html.escape(q["name"][:58]), fmt(stat(q)["now"])) for q in related)

    desc = f"ราคา {p['name']} วันนี้ {fmt(s['now'])} บาท"
    if len(s["ok"]) > 1:
        desc += f" ถูกสุดที่ {s['cheap']['store']} เทียบ {len(s['ok'])} ร้าน"
    if sp:
        desc += f" · {sp}"
    desc = (desc + f" · อัปเดต {updated}")[:300]

    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Product", "name": p["name"], "image": p.get("image") or "", "url": url,
         "category": cfg["name"],
         "offers": {"@type": "AggregateOffer", "priceCurrency": "THB",
                    "lowPrice": s["ok"][0]["price"] if s["ok"] else 0,
                    "highPrice": s["dear"]["price"] if s["dear"] else 0,
                    "offerCount": len(s["ok"]), "availability": "https://schema.org/InStock"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "PriceSpec", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": cfg["name"], "item": f'{BASE}/{cfg["slug"]}'},
            {"@type": "ListItem", "position": 3, "name": p["name"], "item": url}]}]}

    est = ('<span class="badge warn" title="ราคานี้เป็นการประมาณการ ยังไม่ได้เชื่อมข้อมูลร้านค้าโดยตรง">⚠ ประมาณการ</span>'
           if p.get("estimate") else "")
    save = f'<span class="save">ถูกกว่าอีกร้าน {fmt(s["save"])} ฿</span>' if s["save"] > 0 else ""

    return f"""<!DOCTYPE html>
<html lang="th"><head>{shell_head(f'ราคา {p["name"]} วันนี้ {fmt(s["now"])} บาท | PriceSpec', desc, url, PRODUCT_CSS, ld)}</head>
<body>{shell_header()}
<main class="wrap">
  <p class="crumb"><a href="{BASE}/">หน้าแรก</a> ›
     <a href="{BASE}/{cfg['slug']}">{cfg['emoji']} {html.escape(cfg['name'])}</a> › {name}</p>

  <article class="panel">
    <div class="pimg"><img src="{img}" alt="{name}" width="230" height="230"></div>
    <div class="pinfo">
      <h1>ราคา {name}</h1>
      <p class="muted">{html.escape(sp) if sp else html.escape(cfg['name'])}</p>
      <div class="pbig num">{fmt(s['now'])}<span class="baht">฿</span></div>
      <div class="ctx">{save}<span class="badge {s['badge'][0]}">{s['badge'][1]}</span>{est}</div>
      <table class="st">
        <thead><tr><th>ร้านค้า</th><th class="r">ราคา</th><th class="r">อัปเดต</th></tr></thead>
        <tbody>{trs}</tbody>
      </table>
      <div class="btns" style="margin-top:14px">
        <a class="btn primary" href="{html.escape(buy)}" target="_blank" rel="nofollow sponsored noopener"
           data-out="{slug}" data-store="{store}">ดูราคา / สั่งซื้อ</a>
        <a class="btn ghost" href="{BASE}/#alerts">🔔 ตั้งเตือน</a>
      </div>
      <p class="aff" style="text-align:left;margin-top:8px">ลิงก์แนะนำ —
        <a href="{BASE}/contact#affiliate">เราอาจได้ค่าตอบแทนเมื่อคุณซื้อผ่านลิงก์ โดยคุณไม่ต้องจ่ายเพิ่ม</a></p>
    </div>
  </article>

  <div class="chartbox">
    <h2 style="margin:0 0 4px">ราคาย้อนหลัง</h2>
    <p class="muted" style="font-size:.83rem">ค่าเฉลี่ยจากร้านที่มีข้อมูล · เส้นประ = ช่วงก่อนเริ่มเก็บจริง (ข้อมูลจำลอง)</p>
    {big_chart(s['ser'])}
  </div>

  <h2>{cfg['emoji']} {html.escape(cfg['name'])}รุ่นอื่นในช่วงราคาใกล้เคียง</h2>
  <ul class="rel">{rel}</ul>
</main>
{shell_footer(updated)}
</body></html>"""


CONTACT_EMAIL = AFF.get("contact_email") or "pricespec.th@gmail.com"

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
  <li><b>รวบรวมราคาจริงจากร้านค้าปลีกในประเทศไทย</b></li>
  <li><b>แสดงราคาถูกสุดพร้อมราคาแยกรายร้าน</b> ให้เห็นว่าร้านไหนถูกที่สุดในขณะนั้น</li>
  <li><b>เก็บประวัติราคา</b> พร้อมป้ายบอกว่าราคาตอนนี้ถูกจริงหรือแค่ดูเหมือนถูก</li>
  <li><b>แจ้งเตือนเมื่อราคาต่ำกว่าที่ตั้งไว้</b> — เก็บไว้ในเครื่องผู้ใช้เอง</li>
  <li><b>เครื่องมือจัดสเปคคอม</b> ตรวจซ็อกเก็ต ชนิดแรม และกำลังไฟ</li>
</ul>
<h2>ข้อมูลอัปเดตอย่างไร</h2>
<p>ระบบดึงราคาอัตโนมัติ<b>ทุกวันเสาร์ เวลา 05:00 น.</b> แล้วสร้างหน้าเว็บใหม่ทั้งหมดเอง
ไม่มีการแก้ราคาด้วยมือ ราคาที่เห็นจึงเป็นราคาที่ดึงจากหน้าเว็บร้านค้าโดยตรง ณ เวลานั้น</p>
<h2>ข้อจำกัดที่อยากให้ทราบ</h2>
<p>ราคาอาจเปลี่ยนแปลงระหว่างรอบอัปเดต บางรายการมีข้อมูลจากร้านเดียว และกราฟช่วงก่อนวันที่เริ่มเก็บจริง
เป็นข้อมูลจำลอง — เราแสดงเป็นเส้นประบนกราฟเสมอ
<b>โปรดตรวจสอบราคาและสต๊อกกับร้านค้าอีกครั้งก่อนตัดสินใจซื้อ</b>
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
<p class="muted">ปรับปรุงล่าสุด: 28 กรกฎาคม 2569</p>
<h2>สรุปสั้น ๆ</h2>
<p>PriceSpec <b>ไม่ต้องสมัครสมาชิก ไม่ขอข้อมูลส่วนบุคคล และไม่ขายข้อมูลผู้ใช้ให้ใคร</b></p>
<h2>ข้อมูลที่เก็บ</h2>
<ul>
  <li><b>ข้อมูลที่เก็บไว้ในเครื่องคุณเอง (Local Storage)</b> — รายการแจ้งเตือนราคาและสเปคคอมที่คุณจัดไว้
      อยู่ในเบราว์เซอร์ของคุณเท่านั้น ไม่ถูกส่งมาที่เรา ลบได้เองโดยล้างข้อมูลเว็บไซต์</li>
  <li><b>สถิติการใช้งานแบบไม่ระบุตัวตน</b> — เราอาจใช้ Google Analytics เพื่อดูจำนวนผู้เข้าชมและหน้าที่ได้รับความนิยม</li>
  <li><b>ข้อมูลทางเทคนิคของผู้ให้บริการโฮสติ้ง</b> — Vercel อาจบันทึกที่อยู่ IP และชนิดเบราว์เซอร์ตามปกติ</li>
</ul>
<h2>ข้อมูลที่ไม่เก็บ</h2>
<p>เราไม่เก็บชื่อ อีเมล เบอร์โทร ที่อยู่ ข้อมูลบัตรเครดิต หรือข้อมูลการชำระเงินใด ๆ
เพราะเว็บนี้ไม่มีระบบสมาชิกและไม่มีการขายสินค้า</p>
<h2>คุกกี้และลิงก์ไปเว็บอื่น</h2>
<p>เมื่อคุณกดลิงก์ไปยังร้านค้า เว็บปลายทางอาจวางคุกกี้ของตัวเองเพื่อบันทึกที่มาของผู้เข้าชม
ซึ่งอยู่นอกเหนือการควบคุมของเรา โปรดอ่านนโยบายของร้านค้านั้น ๆ</p>
<h2>สิทธิของคุณ</h2>
<p>ตามพระราชบัญญัติคุ้มครองข้อมูลส่วนบุคคล (PDPA) คุณมีสิทธิสอบถาม ขอแก้ไข หรือขอลบข้อมูลของคุณ
เนื่องจากเราไม่ได้เก็บข้อมูลที่ระบุตัวตน จึงมักไม่มีข้อมูลให้ลบ แต่หากมีข้อสงสัยติดต่อเราได้ตลอด</p>
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
  <li><b>ราคาผิดหรือสินค้าไม่มีขายแล้ว</b> — บอกชื่อรุ่นมาได้เลย จะตรวจสอบและแก้ในรอบอัปเดตถัดไป</li>
  <li><b>อยากให้เพิ่มสินค้าหรือหมวดใหม่</b></li>
  <li><b>ร้านค้าที่อยากให้เพิ่มเข้าระบบเทียบราคา</b></li>
  <li><b>ติดต่อเรื่องธุรกิจหรือความร่วมมือ</b></li>
</ul>
<h2 id="affiliate">การเปิดเผยเรื่องลิงก์แนะนำ (Affiliate Disclosure)</h2>
<p>PriceSpec ให้บริการฟรีและไม่มีค่าสมาชิก เราจึงมีรายได้จาก<b>ลิงก์แนะนำ (affiliate link)</b> เป็นหลัก</p>
<p>เมื่อคุณกดปุ่มไปยังร้านค้าผ่านเว็บของเราแล้วเกิดการสั่งซื้อ เราอาจได้รับค่าตอบแทนเล็กน้อยจากร้านค้านั้น
<b>โดยคุณไม่ต้องจ่ายเพิ่มแม้แต่บาทเดียว</b> ราคาที่คุณจ่ายเท่ากับการเข้าเว็บร้านค้าโดยตรง</p>
<p>สิ่งที่เรายึดถือ:</p>
<ul>
  <li>ราคาที่แสดงดึงจากหน้าเว็บร้านค้าจริง <b>เราไม่แก้ไขหรือจัดอันดับตามค่าตอบแทน</b></li>
  <li>ร้านที่ถูกที่สุดถูกทำเครื่องหมาย 🏆 เสมอ ไม่ว่าร้านนั้นจะจ่ายค่าตอบแทนให้เราหรือไม่</li>
  <li>ลิงก์แนะนำทุกลิงก์กำกับด้วย <code>rel="nofollow sponsored"</code> ตามแนวทางของ Google</li>
</ul>
""",
    },
}

DOC_CSS = """
.doc{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-card);padding:26px 30px;margin-top:6px;max-width:78ch}
.doc h1{margin-bottom:10px}
.doc h2{font-size:1.05rem;color:var(--accent);margin:24px 0 8px}
.doc p{margin:10px 0;color:var(--text2)}
.doc ul{margin:10px 0 10px 20px;color:var(--text2)}
.doc li{margin:7px 0}
.doc b{color:var(--text)}
.doc a{color:var(--accent)}
.doc a:hover{text-decoration:underline}
.doc code{background:var(--surface2);padding:2px 7px;border-radius:5px;font-size:.88em}
.mail{font-size:1.1rem;background:var(--accentBg);border:1px solid var(--accent);
 border-radius:10px;padding:14px 18px;margin:16px 0!important}
@media(max-width:620px){.doc{padding:18px 16px}}
"""


def build_static(key, cfg, updated):
    body = cfg["body"].replace("{email}", CONTACT_EMAIL)
    return f"""<!DOCTYPE html>
<html lang="th"><head>{shell_head(cfg['title'], cfg['desc'], f"{BASE}/{key}", DOC_CSS)}</head>
<body>{shell_header()}
<main class="wrap">
  <p class="crumb"><a href="{BASE}/">หน้าแรก</a> › {html.escape(cfg['h1'])}</p>
  {shell_nav()}
  <article class="doc"><h1>{html.escape(cfg['h1'])}</h1>{body}</article>
</main>
{shell_footer(updated)}
</body></html>"""


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
        items.sort(key=lambda q: stat(q)["now"])            # ถูก → แพง
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
