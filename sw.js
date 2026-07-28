// PriceSpec — service worker: ทำให้เปิดออฟไลน์ได้ + โหลดเร็ว
const CACHE = "pricespec-v22";
const ASSETS = [
  "./index.html",
  "./manifest.json",
  "./data/prices.js", "./data/affiliate.js",
  "./icons/icon-192.png", "./logo-mark.svg", "./favicon.ico", "./icons/apple-touch-icon.png",
  "./icons/icon-512.png",
  "./images/gpu.svg", "./images/cpu.svg", "./images/mainboard.svg", "./images/ram.svg",
  "./images/ssd.svg", "./images/psu.svg", "./images/case.svg", "./images/console.svg",
  "https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// ข้อมูลราคา: เอาจากเน็ตก่อน (ให้ได้ราคาล่าสุด) ถ้าออฟไลน์ค่อยใช้ cache
// ไฟล์อื่น: เอาจาก cache ก่อน (เร็ว)
self.addEventListener("fetch", (e) => {
  const url = e.request.url;
  if (url.includes("prices.js") || url.includes("prices.json")) {
    e.respondWith(
      fetch(e.request, { cache: "no-store" })   // ข้อมูลราคาเอาสดเสมอ ไม่ใช้ HTTP cache
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(e.request, copy));
          return res;
        })
        .catch(() => caches.match(e.request))
    );
  } else {
    e.respondWith(
      caches.match(e.request).then((hit) => hit || fetch(e.request))
    );
  }
});
