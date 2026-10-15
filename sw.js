/* VoltRide Service Worker v2.0.0 */
const CACHE = "voltride-v3";
const ASSETS = ["./", "./index.html", "./manifest.json"];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  
  const url = new URL(e.request.url);
  const isHTML = e.request.mode === "navigate" || 
                 url.pathname.endsWith(".html") || 
                 url.pathname === "/" ||
                 url.pathname.endsWith("/");
  
  if (isHTML) {
    // HTML: شبكة أولًا (يجلب دائمًا آخر نسخة)، ثم كاش
    e.respondWith(
      fetch(e.request).then((res) => {
        if (res && res.status === 200) {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(e.request, copy));
        }
        return res;
      }).catch(() => caches.match(e.request))
    );
  } else {
    // أصول ثابتة (أيقونات، manifest): كاش أولًا
    e.respondWith(
      caches.match(e.request).then((cached) => {
        if (cached) return cached;
        return fetch(e.request).then((res) => {
          if (res && res.status === 200) {
            const copy = res.clone();
            caches.open(CACHE).then((c) => c.put(e.request, copy));
          }
          return res;
        });
      })
    );
  }
});