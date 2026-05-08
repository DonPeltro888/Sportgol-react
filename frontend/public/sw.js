// GOLEVENTS Service Worker — CWV-12 offline + asset caching
// Strategy: network-first for HTML, cache-first for static assets, stale-while-revalidate for /api
const CACHE_VERSION = 'golevents-v1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => cache.addAll(STATIC_ASSETS).catch(() => {}))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // Skip cross-origin (avoid caching CDN/fonts/analytics)
  if (url.origin !== location.origin) return;

  // Admin pages: never cache (always fresh)
  if (url.pathname.startsWith('/admin')) return;

  // HTML navigation: network-first with fallback
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req).catch(() => caches.match('/').then((c) => c || caches.match('/index.html')))
    );
    return;
  }

  // /api requests: stale-while-revalidate (1h cache for read-only GETs)
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      caches.open(CACHE_VERSION).then((cache) =>
        cache.match(req).then((cached) => {
          const fetched = fetch(req).then((res) => {
            if (res.ok) cache.put(req, res.clone());
            return res;
          }).catch(() => cached);
          return cached || fetched;
        })
      )
    );
    return;
  }

  // Static assets (.js, .css, .png, .webp, .avif, .woff2): cache-first
  event.respondWith(
    caches.match(req).then((cached) =>
      cached || fetch(req).then((res) => {
        if (res.ok) {
          const clone = res.clone();
          caches.open(CACHE_VERSION).then((cache) => cache.put(req, clone));
        }
        return res;
      })
    )
  );
});
