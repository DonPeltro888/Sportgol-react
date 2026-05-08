"""
CWV Patch Generator — produces ready-to-paste snippets/components for the 7 manual fixes.

Each generator returns:
{
  "title": "...",
  "filename": "suggested-filename.ext",
  "language": "html|jsx|js|css",
  "content": "..."     # ready-to-copy
}
"""
from typing import Any, Dict, List


def gen_cwv2_lazy_admin() -> Dict[str, Any]:
    return {
        "title": "Lazy load admin routes (App.js patch)",
        "filename": "App.js.patch",
        "language": "jsx",
        "content": """// BEFORE (top of App.js):
// import AdminDashboard from './pages/admin/AdminDashboard';
// import AdminTeams from './pages/admin/AdminTeams';
// ...18 admin imports...

// AFTER:
import { lazy, Suspense } from 'react';
const AdminDashboard = lazy(() => import('./pages/admin/AdminDashboard'));
const AdminTeams     = lazy(() => import('./pages/admin/AdminTeams'));
const SeoDashboard   = lazy(() => import('./pages/admin/seo/SeoDashboard'));
const CostObservatory= lazy(() => import('./pages/admin/seo/CostObservatory'));
const GoogleSuite    = lazy(() => import('./pages/admin/seo/GoogleSuite'));
// ... convert ALL admin imports to lazy()

// Wrap admin <Route> blocks in <Suspense>:
<Routes>
  {/* public routes stay normal */}
  <Route path="/" element={<HomePage />} />

  {/* admin routes wrapped */}
  <Route path="/admin/*" element={
    <Suspense fallback={<div className="p-8 text-center">Loading admin…</div>}>
      <AdminDashboard />
    </Suspense>
  } />
</Routes>

// Result: visitors no longer download admin code.
""",
    }


def gen_cwv3_img_dim() -> Dict[str, Any]:
    return {
        "title": "<img> width/height (CLS fix)",
        "filename": "HeroPicture.jsx",
        "language": "jsx",
        "content": """// Drop-in component. Replaces every <img> with <picture> + width/height.
// Generates AVIF/WebP fallback if siblings exist.
import React from 'react';

export const HeroPicture = ({ src, alt, width = 1200, height = 630, priority = false, className = '' }) => {
  if (!src) return null;
  const base = src.replace(/\\.(png|jpe?g)$/i, '');
  const ext = (src.match(/\\.(png|jpe?g)$/i) || ['', 'png'])[1];
  return (
    <picture>
      <source srcSet={`${base}.avif`} type="image/avif" />
      <source srcSet={`${base}.webp`} type="image/webp" />
      <img
        src={src}
        alt={alt || ''}
        width={width}
        height={height}
        loading={priority ? 'eager' : 'lazy'}
        fetchpriority={priority ? 'high' : 'auto'}
        decoding="async"
        className={className}
      />
    </picture>
  );
};

// Usage:
// <HeroPicture src="/uploads/inter-vs-juve.png" alt="Inter vs Juve"
//   width={1200} height={630} priority />
""",
    }


def gen_cwv4_font_preload() -> Dict[str, Any]:
    return {
        "title": "Preload bold font weight (paste in <head>)",
        "filename": "preload-fonts.html",
        "language": "html",
        "content": """<!-- Paste in <head> BEFORE other <link> tags -->
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<!-- Inter Regular (already there probably) -->
<link rel="preload"
      href="https://fonts.gstatic.com/s/inter/v18/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMa1ZL7.woff2"
      as="font" type="font/woff2" crossorigin>

<!-- Inter Bold (NEW — covers H1/H2/buttons) -->
<link rel="preload"
      href="https://fonts.gstatic.com/s/inter/v18/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMa2ZL7SU8.woff2"
      as="font" type="font/woff2" crossorigin>

<style>
  /* font-display: swap fallback (avoid FOIT, accept FOUT briefly) */
  body { font-family: Inter, -apple-system, system-ui, sans-serif; }
  @font-face { font-family: Inter; font-display: swap; src: local('Inter'); }
</style>
""",
    }


def gen_cwv7_lazy_load() -> Dict[str, Any]:
    return {
        "title": 'loading="lazy" snippet',
        "filename": "lazy-img-pattern.jsx",
        "language": "jsx",
        "content": """// All <img> below the fold MUST have loading="lazy" + decoding="async".
// React snippet:

<img
  src="/team-logos/inter.png"
  alt="Inter"
  width={48}
  height={48}
  loading="lazy"     // <-- key
  decoding="async"
/>

// In Blade:
// <img src="..." width="48" height="48" loading="lazy" decoding="async">

// EXCEPTIONS (above-the-fold, hero):
// loading="eager" fetchpriority="high"
""",
    }


def gen_cwv8_preconnect() -> Dict[str, Any]:
    return {
        "title": "Preconnect to external CDNs (paste in <head>)",
        "filename": "preconnect.html",
        "language": "html",
        "content": """<!-- Paste in <head> as early as possible -->
<link rel="preconnect" href="https://upload.wikimedia.org" crossorigin>
<link rel="preconnect" href="https://a.espncdn.com" crossorigin>
<link rel="preconnect" href="https://r2.thesportsdb.com" crossorigin>
<link rel="preconnect" href="https://www.googletagmanager.com" crossorigin>

<!-- Optional dns-prefetch for non-critical hosts -->
<link rel="dns-prefetch" href="https://images.unsplash.com">
""",
    }


def gen_cwv9_defer_scripts() -> Dict[str, Any]:
    return {
        "title": "Defer non-critical scripts",
        "filename": "defer-scripts.html",
        "language": "html",
        "content": """<!-- BEFORE (blocking): -->
<!--   <script src="https://www.googletagmanager.com/gtag/js?id=GA_ID"></script> -->

<!-- AFTER (deferred): -->
<script defer src="https://www.googletagmanager.com/gtag/js?id=GA_ID"></script>

<!-- Or async if it must execute ASAP but not block parser: -->
<script async src="https://example.com/non-critical.js"></script>

<!-- Move ALL <script src> from <head> to bottom of <body>, or add defer/async. -->
<!-- EXCEPTION: scripts that must run before rendering (rare) — keep blocking but minimize. -->
""",
    }


def gen_cwv10_aspect_ratio() -> Dict[str, Any]:
    return {
        "title": "aspect-ratio CSS for stable img layouts",
        "filename": "aspect-ratio.css",
        "language": "css",
        "content": """/* Combine with width/height attributes for double safety */

/* Hero images 1200x630 */
.hero-img,
img[width="1200"][height="630"] {
  aspect-ratio: 1200 / 630;
  width: 100%;
  height: auto;
  object-fit: cover;
}

/* Team logos 48x48 (Header) */
.team-logo {
  aspect-ratio: 1 / 1;
  width: 48px;
  height: 48px;
  object-fit: contain;
}

/* Card thumbnails 16:9 */
.card-thumb {
  aspect-ratio: 16 / 9;
  width: 100%;
  height: auto;
}

/* Skeleton placeholder while image loads */
.img-skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}
@keyframes skeleton-pulse {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
""",
    }


def gen_cwv12_service_worker() -> Dict[str, Any]:
    return {
        "title": "Service Worker for offline + asset caching",
        "filename": "sw.js",
        "language": "js",
        "content": """// Service Worker — drop in /public/sw.js
// Strategy: cache-first for static assets, network-first for HTML, stale-while-revalidate for API.

const CACHE_NAME = 'app-v1';
const STATIC = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then((c) => c.addAll(STATIC)));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  // HTML: network-first
  if (e.request.mode === 'navigate') {
    e.respondWith(fetch(e.request).catch(() => caches.match('/')));
    return;
  }
  // API: stale-while-revalidate
  if (url.pathname.startsWith('/api/')) {
    e.respondWith(
      caches.open(CACHE_NAME).then((cache) =>
        cache.match(e.request).then((cached) => {
          const fetched = fetch(e.request).then((res) => { cache.put(e.request, res.clone()); return res; });
          return cached || fetched;
        })
      )
    );
    return;
  }
  // Static: cache-first
  e.respondWith(caches.match(e.request).then((c) => c || fetch(e.request)));
});

// Register in your main bundle (index.js / App.js):
// if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js');
""",
    }


GENERATORS = {
    "CWV-2":  gen_cwv2_lazy_admin,
    "CWV-3":  gen_cwv3_img_dim,
    "CWV-4":  gen_cwv4_font_preload,
    "CWV-7":  gen_cwv7_lazy_load,
    "CWV-8":  gen_cwv8_preconnect,
    "CWV-9":  gen_cwv9_defer_scripts,
    "CWV-10": gen_cwv10_aspect_ratio,
    "CWV-12": gen_cwv12_service_worker,
}


def generate_patch(cwv_id: str) -> Dict[str, Any]:
    fn = GENERATORS.get(cwv_id)
    if not fn:
        return {"ok": False, "error": f"no_generator_for_{cwv_id}"}
    return {"ok": True, **fn()}
