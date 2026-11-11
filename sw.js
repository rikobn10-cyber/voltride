/* VoltRide Service Worker v3.1.0 */
const VERSION = "voltride-v21";
const PRECACHE = [
  "./", "index.html", "offline.html", "manifest.json",
  "site.css", "site.js", "icon-192.png", "icon-512.png",
  "icon-maskable-192.png", "icon-maskable-512.png", "blog.html", "about.html",
  "privacy.html", "contact.html", "accessories.html", "en/accessories.html",
  "fr/accessories.html", "ride-match.html", "article-1.html", "article-2.html",
  "article-3.html", "article-4.html", "article-5.html", "article-6.html",
  "article-7.html", "article-8.html", "article-9.html", "article-10.html",
  "guides/not-charging.html", "guides/battery-range.html", "guides/error-codes.html", "electric-scooter-winter-range-voltride.jpg",
  "scooter-accessories.jpg", "xiaomi-pro-2.html", "xiaomi-4-pro.html", "xiaomi-essential.html",
  "xiaomi-3-lite.html", "segway-max-g30.html", "segway-max-g2.html", "segway-e2-plus.html",
  "navee-n40.html", "navee-g5.html", "niu-kqi3-max.html", "kukirin-g2-pro.html",
  "kukirin-g2-max.html", "kukirin-g3-pro.html", "kukirin-g4.html", "ecoxtrem-bison-gt.html",
  "ecoxtrem-bison-m41.html", "dualtron-mini.html", "dualtron-victor.html", "dualtron-thunder-3.html",
  "vsett-8-plus.html", "vsett-9-plus.html", "vsett-10-plus.html", "apollo-city-pro.html",
  "apollo-ghost.html", "kaabo-wolf-king.html", "gotrax-g4.html", "gotrax-gxl-v2.html",
  "inokim-oxo.html", "nami-burn-e2-max.html", "teverun-fighter-11.html"
];
const NAV_TIMEOUT_MS = 3500;

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(VERSION)
      // كل ملف على حدة: غياب ملف واحد لا يُفشل التثبيت كله
      .then((cache) => Promise.all(PRECACHE.map((u) =>
        cache.add(new Request(u, { cache: "reload" })).catch(() => {})
      )))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("message", (e) => {
  if (e.data === "SKIP_WAITING") self.skipWaiting();
  if (e.data && e.data.type === "GET_VERSION" && e.ports && e.ports[0]) {
    e.ports[0].postMessage({ version: VERSION });
  }
  if (e.data && e.data.type === "DEBUG_CACHE" && e.ports && e.ports[0]) {
    e.waitUntil((async () => {
      const cache = await caches.open(VERSION);
      const request = new Request(e.data.url);
      const page = await matchPage(cache, request);
      const offlineUrl = new URL("offline.html", self.registration.scope).href;
      const fallback = await cache.match(offlineUrl);
      const keys = (await cache.keys()).map(item => new URL(item.url).pathname);
      e.ports[0].postMessage({
        version: VERSION,
        online: self.navigator ? self.navigator.onLine : null,
        pageStatus: page ? page.status : null,
        fallbackStatus: fallback ? fallback.status : null,
        keys
      });
    })());
  }
});

function fetchWithTimeout(req, ms) {
  return new Promise((resolve, reject) => {
    const t = setTimeout(() => reject(new Error("timeout")), ms);
    fetch(req).then((r) => { clearTimeout(t); resolve(r); }, (err) => { clearTimeout(t); reject(err); });
  });
}

// يطابق الصفحة سواء طُلبت بـ .html أو بدونها (روابط نظيفة)
async function matchPage(cache, req) {
  const url = new URL(req.url);
  const path = url.pathname;
  const tries = [req, new URL(path, self.registration.scope).href];
  if (path === "/" || path.endsWith("/")) {
    tries.push(new URL("index.html", new URL(path, self.registration.scope)).href);
  } else if (!/\.[a-z0-9]+$/i.test(path)) {
    tries.push(new URL(path.replace(/^\//, "") + ".html", self.registration.scope).href);
  }
  for (const t of tries) {
    const hit = await cache.match(t, { ignoreSearch: true });
    if (hit) return hit;
  }
  return null;
}

async function offlineNavigationFallback(cache, req) {
  const page = await matchPage(cache, req);
  if (page) {
    console.log("[VoltRide SW] offline navigation matched cached page", req.url);
    return page;
  }
  const offlineUrl = new URL("offline.html", self.registration.scope).href;
  const fallback = await cache.match(offlineUrl);
  console.log("[VoltRide SW] offline fallback lookup", JSON.stringify({ request: req.url, offlineUrl, found: Boolean(fallback) }));
  return fallback || Response.error();
}

async function navigate(req) {
  const cache = await caches.open(VERSION);
  try {
    const res = await fetchWithTimeout(req, NAV_TIMEOUT_MS);
    if (res && res.ok) {
      cache.put(req, res.clone());
      return res;
    }
    // Some browsers resolve an offline navigation to a cached HTTP 404
    // instead of rejecting fetch(). Use the offline page in that case.
    if (self.navigator && self.navigator.onLine === false) {
      return offlineNavigationFallback(cache, req);
    }
    return res;
  } catch (error) {
    console.log("[VoltRide SW] navigation fetch rejected", req.url, String(error));
    return offlineNavigationFallback(cache, req);
  }
}

async function staleWhileRevalidate(event) {
  const req = event.request;
  const cache = await caches.open(VERSION);
  const cached = await cache.match(req);
  const network = fetch(req)
    .then((res) => {
      if (res && res.ok && res.type === "basic") cache.put(req, res.clone());
      return res;
    })
    .catch(() => null);
  event.waitUntil(network);
  return cached || (await network) || Response.error();
}

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  // لا نلمس أي شيء خارج نطاقنا (Google Analytics وغيره)
  if (url.origin !== self.location.origin) return;
  // طلبات الأجزاء (Range) وملف الـAPK تذهب مباشرة للشبكة ولا تُخزَّن
  if (req.headers.has("range") || /\.apk$/i.test(url.pathname)) return;
  if (url.pathname.endsWith("/sw.js")) return;

  if (req.mode === "navigate") {
    event.respondWith(navigate(req));
    return;
  }
  event.respondWith(staleWhileRevalidate(event));
});
