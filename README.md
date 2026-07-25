# PC Price TH ⚡ — เว็บเช็คราคาอุปกรณ์คอมในไทย + จัดสเปค

Prototype เว็บเช็คราคาอุปกรณ์คอม 7 หมวด (การ์ดจอ, ซีพียู, เมนบอร์ด, แรม, SSD, PSU, เคส) จากร้านไทย พร้อมกราฟราคาย้อนหลัง 30 วัน ระบบแจ้งเตือนเมื่อราคาลดถึงเป้า และ **หน้าจัดสเปคคอม** ที่คำนวณราคารวม กินไฟโดยประมาณ และเช็คความเข้ากันได้อัตโนมัติ (socket CPU-เมนบอร์ด, ชนิดแรม DDR4/DDR5, วัตต์ PSU)

มีหน้า ⭐ Special รวมเครื่องเกมทุกชนิด — PS5, Xbox, Nintendo Switch, เครื่องเกมพกพา (Steam Deck, ROG Ally, Legion Go) และ VR

หมายเหตุ: สินค้าใน `scraper/config.json` ใส่ `category` (gpu/cpu/mainboard/ram/ssd/psu/case/console) และ `specs` (เช่น socket, ram, tdp, watt) เพื่อให้หน้าจัดสเปคเช็คความเข้ากันได้

## ลองเปิดดูทันที

ดับเบิลคลิก `index.html` — เปิดในเบราว์เซอร์ได้เลย ไม่ต้องติดตั้งอะไร (ตอนนี้เป็นข้อมูลตัวอย่าง)

## โครงสร้างโปรเจกต์

    index.html                       หน้าเว็บ (ไฟล์เดียวจบ)
    data/prices.json                 ฐานข้อมูลราคา + ประวัติ
    data/prices.js                   ข้อมูลเดียวกันสำหรับหน้าเว็บ (สร้างอัตโนมัติ)
    scraper/scraper.py               script ดึงราคารายวัน
    scraper/config.json              ตั้งค่า URL สินค้า + CSS selector
    scraper/alerts.json              กฎแจ้งเตือน + Discord webhook
    .github/workflows/update-prices.yml   รันอัตโนมัติทุกวันบน GitHub (ฟรี)

## ขั้นตอนใช้งานจริง

1. **ทดสอบ scraper** (ไม่ต้องต่อเน็ต): `python scraper/scraper.py --mock` แล้วรีเฟรชหน้าเว็บ จะเห็นราคาวันใหม่เพิ่มเข้ากราฟ
2. **ใส่สินค้าจริง**: เปิดหน้าสินค้าใน JIB/Advice → คลิกขวาที่ราคา → Inspect → หา CSS selector → ใส่ใน `scraper/config.json` (JIB/Advice เป็นเว็บ JS-render script จึงใช้ Playwright ให้อยู่แล้ว: `pip install beautifulsoup4 playwright && playwright install chromium`)
3. **สมัคร [Shopee Affiliate](https://affiliate.shopee.co.th/)** → สร้างลิงก์สินค้า → แทนที่ `YOUR_AFFILIATE_LINK` ใน config
4. **Deploy ฟรี**: สร้าง repo บน GitHub → push โค้ดทั้งหมด → Settings > Pages > เลือก branch main → ได้เว็บจริงที่ `https://ชื่อคุณ.github.io/gpu-price-tracker/` และ GitHub Actions จะดึงราคาให้อัตโนมัติ**ทุกวันเสาร์ 05:00 น.** (แก้เวลาได้ที่บรรทัด cron ใน `.github/workflows/update-prices.yml` หรือกดรันเองได้ที่แท็บ Actions > Run workflow)
5. **เปิดแจ้งเตือน Discord**: สร้าง webhook ใน Discord server ของคุณ ใส่ใน `scraper/alerts.json`

## ติดตั้งเป็นแอปมือถือ (PWA)

เว็บนี้เป็น PWA — ติดตั้งลงหน้าจอมือถือได้เหมือนแอปจริง (เต็มจอ มีไอคอน เปิดออฟไลน์ได้) **ต้อง deploy ขึ้น GitHub Pages ก่อน** (PWA ต้องรันบน HTTPS ไม่ทำงานจากไฟล์ในเครื่อง)

- **Android (Chrome)**: เปิดเว็บ → จะมีปุ่ม "📲 ติดตั้งแอปลงเครื่อง" หรือเมนู ⋮ > "เพิ่มลงในหน้าจอหลัก"
- **iPhone (Safari)**: เปิดเว็บ → ปุ่มแชร์ → "เพิ่มลงในหน้าจอโฮม"

ไฟล์ที่เกี่ยวข้อง: `manifest.json` (ชื่อ/ไอคอน/สีแอป), `sw.js` (cache ให้เปิดออฟไลน์และโหลดเร็ว), `icons/`

ถ้าอนาคตอยากลง Google Play จริงๆ ใช้ [PWABuilder](https://www.pwabuilder.com/) แปลง PWA นี้เป็นไฟล์ .aab ได้เลย (ค่าสมัครนักพัฒนา Google $25 ครั้งเดียว)

## แนวทางหารายได้

- ปุ่ม "ซื้อเลย" ทุกปุ่มคือลิงก์ affiliate — ได้ค่าคอมทุกออเดอร์ที่คลิกผ่าน
- โปรโมตเว็บในกลุ่ม Facebook จัดสเปคคอม, Pantip ห้องซิลิคอนวัลเลย์, TikTok
- ต่อยอด: เพิ่ม CPU/RAM/SSD, สมัครสมาชิกรับแจ้งเตือนทางอีเมล/LINE OA, หน้าเทียบสเปค

## รูปสินค้า

การ์ดสินค้าแสดงรูปอัตโนมัติ: ถ้าสินค้ามี field `image` จะใช้รูปนั้น ถ้าไม่มีจะใช้ไอคอนตามหมวด (`images/หมวด.svg`)

วิธีใส่รูปจริง: บันทึกรูปสินค้า (แนะนำรูป press จากเว็บผู้ผลิต เช่น asus.com, nvidia.com หรือถ่ายเอง — เลี่ยง hotlink รูปจากร้านค้าเพราะลิงก์เสียบ่อยและมีเรื่องลิขสิทธิ์) → วางไว้ในโฟลเดอร์ `images/` → ใส่ `"image": "images/ชื่อไฟล์.jpg"` ให้สินค้านั้นใน `scraper/config.json` (scraper จะพาเข้า data ให้เอง) หรือแก้ตรงใน `data/prices.json` ก็ได้

## ข้อควรระวัง

- ราคาในไฟล์ตอนนี้เป็น **ข้อมูลตัวอย่าง** — ต้องตั้ง scraper ให้ดึงราคาจริงก่อนเปิดใช้
- ดึงข้อมูลวันละครั้งพอ อย่าถี่เกิน เพื่อไม่เป็นภาระเซิร์ฟเวอร์ร้านค้า และควรตรวจ Terms of Service ของแต่ละร้าน
