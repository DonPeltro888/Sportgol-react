"""
CWV HTML Analyzer — fetch any URL and diagnose the 12 Core Web Vitals issues.

Returns a structured report with one entry per CWV id, marking each as detected/clean.
"""
import logging
import re
from typing import Any, Dict, List
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

KNOWN_CDNS = {
    "fonts.googleapis.com", "fonts.gstatic.com",
    "upload.wikimedia.org", "a.espncdn.com", "r2.thesportsdb.com",
    "www.googletagmanager.com", "www.google-analytics.com",
}

# 12 CWV IDs aligned with the user's Tier P0/P1/P2 list
CWV_CATALOG: List[Dict[str, Any]] = [
    {"id": "CWV-1",  "title": "Hero image WebP/AVIF",       "tier": "P0", "kind": "auto",   "category": "LCP"},
    {"id": "CWV-2",  "title": "Lazy load admin routes",      "tier": "P0", "kind": "manual", "category": "TTI"},
    {"id": "CWV-3",  "title": "<img> width/height (CLS)",    "tier": "P0", "kind": "manual", "category": "CLS"},
    {"id": "CWV-4",  "title": "Preload bold font weight",    "tier": "P0", "kind": "manual", "category": "LCP"},
    {"id": "CWV-5",  "title": "PageSpeed weekly cron",       "tier": "P0", "kind": "auto",   "category": "Monitor"},
    {"id": "CWV-6",  "title": "SSR JSON-LD injection",       "tier": "P1", "kind": "auto",   "category": "FCP"},
    {"id": "CWV-7",  "title": 'loading="lazy" below-fold',   "tier": "P1", "kind": "manual", "category": "LCP"},
    {"id": "CWV-8",  "title": "Preconnect external CDNs",    "tier": "P1", "kind": "manual", "category": "TTFB"},
    {"id": "CWV-9",  "title": "Defer non-critical scripts",  "tier": "P1", "kind": "manual", "category": "FCP"},
    {"id": "CWV-10", "title": "Image aspect-ratio CSS",      "tier": "P1", "kind": "manual", "category": "CLS"},
    {"id": "CWV-11", "title": "Critical CSS extraction",     "tier": "P2", "kind": "auto",   "category": "FCP"},
    {"id": "CWV-12", "title": "Service Worker offline",      "tier": "P2", "kind": "manual", "category": "Cache"},
]


async def _fetch(url: str) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True,
                                      headers={"User-Agent": "GoLeventsCWVAudit/1.0"}) as c:
            r = await c.get(url)
        if r.status_code >= 400:
            return {"ok": False, "error": f"HTTP {r.status_code}"}
        return {"ok": True, "html": r.text, "headers": dict(r.headers)}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


def _check_each(soup: BeautifulSoup, html: str, url: str) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    imgs = soup.find_all("img")
    scripts = soup.find_all("script")
    links = soup.find_all("link")
    base_host = urlparse(url).netloc

    # CWV-1: Hero PNG (any img with png src as first 2 imgs)
    hero_imgs = imgs[:3]
    pngs = [i for i in hero_imgs if (i.get("src") or "").lower().endswith(".png")]
    out["CWV-1"] = {
        "detected": bool(pngs),
        "count": len(pngs),
        "samples": [(i.get("src") or "")[:120] for i in pngs[:3]],
        "detail": f"{len(pngs)} hero <img> in PNG (no WebP/AVIF fallback)" if pngs else "All hero images use modern formats",
    }

    # CWV-2: Heuristic — multiple admin route imports = no lazy
    # Without source access we look at JS chunks: a single huge JS = no splitting
    main_scripts = [s for s in scripts if s.get("src") and "main" in (s.get("src") or "").lower()]
    out["CWV-2"] = {
        "detected": False,  # cannot detect from HTML alone
        "count": 0,
        "note": "Cannot detect via HTML scan. Recommend checking with Lighthouse 'Reduce unused JavaScript'.",
        "detail": "Open Coverage tab in DevTools to confirm.",
    }

    # CWV-3: img without width/height
    imgs_no_dim = [i for i in imgs if not (i.get("width") and i.get("height"))]
    out["CWV-3"] = {
        "detected": bool(imgs_no_dim),
        "count": len(imgs_no_dim),
        "samples": [str(i)[:160] for i in imgs_no_dim[:5]],
        "detail": f"{len(imgs_no_dim)} <img> without explicit width/height (CLS risk)" if imgs_no_dim else "All imgs have dimensions",
    }

    # CWV-4: Font preload coverage
    font_preloads = [l for l in links if l.get("rel") and "preload" in l.get("rel") and (l.get("as") or "") == "font"]
    has_google_fonts = any("fonts.googleapis.com" in (l.get("href") or "") for l in links)
    insufficient = has_google_fonts and len(font_preloads) < 2
    out["CWV-4"] = {
        "detected": insufficient,
        "count": len(font_preloads),
        "detail": (f"Only {len(font_preloads)} font preload(s) but Google Fonts in use (need bold weight too)"
                   if insufficient else f"{len(font_preloads)} font preloads — OK"),
    }

    # CWV-5: PageSpeed cron — backend feature, not detectable from HTML
    out["CWV-5"] = {
        "detected": False,
        "note": "Backend feature (cron). Already shipped in golevents — apply on target via tool.",
        "detail": "Click 'Fix Now' to enable weekly PageSpeed scan on this URL.",
    }

    # CWV-6: SSR JSON-LD vs runtime injection
    jsonld_in_html = soup.find_all("script", attrs={"type": "application/ld+json"})
    has_jsonld_ssr = any(s.string and len(s.string.strip()) > 50 for s in jsonld_in_html)
    out["CWV-6"] = {
        "detected": not has_jsonld_ssr,
        "count": len(jsonld_in_html),
        "detail": ("No JSON-LD found in raw HTML (likely injected via JS — bad for SEO)"
                   if not has_jsonld_ssr else f"{len(jsonld_in_html)} JSON-LD blocks SSR-rendered — OK"),
    }

    # CWV-7: lazy load below fold
    eager_imgs = [i for i in imgs if (i.get("loading") or "") != "lazy" and not i.get("fetchpriority")]
    below_fold = max(0, len(eager_imgs) - 3)  # heuristic: first 3 are above fold
    out["CWV-7"] = {
        "detected": below_fold > 0,
        "count": below_fold,
        "detail": f"{below_fold} <img> below-fold without loading=lazy" if below_fold else "Lazy load coverage OK",
    }

    # CWV-8: preconnect to used CDNs
    preconnects = {urlparse(l.get("href") or "").netloc for l in links if l.get("rel") and "preconnect" in l.get("rel")}
    used_cdns = set()
    for tag in soup.find_all(["img", "script", "link", "iframe"]):
        a = tag.get("src") or tag.get("href") or ""
        try:
            host = urlparse(urljoin(url, a)).netloc
            if host and host != base_host:
                used_cdns.add(host)
        except Exception:
            pass
    relevant = used_cdns & KNOWN_CDNS
    missing = relevant - preconnects
    out["CWV-8"] = {
        "detected": bool(missing),
        "count": len(missing),
        "missing_cdns": sorted(missing),
        "detail": f"{len(missing)} external CDNs without preconnect" if missing else "Preconnect coverage OK",
    }

    # CWV-9: scripts in <head> without async/defer
    head_scripts = [s for s in scripts if s.find_parent("head") and s.get("src")
                    and not (s.get("async") or s.get("defer") or (s.get("type") or "") == "module")]
    out["CWV-9"] = {
        "detected": bool(head_scripts),
        "count": len(head_scripts),
        "samples": [(s.get("src") or "")[:120] for s in head_scripts[:5]],
        "detail": f"{len(head_scripts)} blocking scripts in <head>" if head_scripts else "No blocking scripts",
    }

    # CWV-10: aspect-ratio CSS (heuristic: search inline style)
    has_aspect = bool(re.search(r"aspect-ratio\s*:", html))
    out["CWV-10"] = {
        "detected": not has_aspect and bool(imgs_no_dim),
        "count": 0 if has_aspect else len(imgs_no_dim),
        "detail": "No aspect-ratio CSS detected; combine with width/height for stable layout"
                  if not has_aspect else "aspect-ratio CSS found",
    }

    # CWV-11: critical CSS extraction (heuristic: <style> in head with substantial content?)
    head_styles = [s for s in soup.find_all("style") if s.find_parent("head") and len((s.string or "")) > 1000]
    sync_css = [l for l in links if l.get("rel") and "stylesheet" in l.get("rel") and not l.get("media")]
    out["CWV-11"] = {
        "detected": (len(sync_css) > 2 and not head_styles),
        "count": len(sync_css),
        "detail": (f"{len(sync_css)} sync CSS sheets, no inline critical CSS"
                   if not head_styles else "Critical CSS appears inlined"),
    }

    # CWV-12: service worker registration (heuristic: search for navigator.serviceWorker.register)
    sw_register = bool(re.search(r"navigator\.serviceWorker\.register", html))
    out["CWV-12"] = {
        "detected": not sw_register,
        "count": 0,
        "detail": "No Service Worker registration detected" if not sw_register else "Service Worker active",
    }

    # Bonus: meta viewport, canonical
    out["BONUS-VIEWPORT"] = {
        "detected": not soup.find("meta", attrs={"name": "viewport"}),
        "detail": "Missing <meta viewport>" if not soup.find("meta", attrs={"name": "viewport"}) else "Viewport OK",
    }
    out["BONUS-CANONICAL"] = {
        "detected": not soup.find("link", rel="canonical"),
        "detail": "Missing <link rel=canonical>" if not soup.find("link", rel="canonical") else "Canonical OK",
    }

    return out


async def analyze_url(url: str) -> Dict[str, Any]:
    fetched = await _fetch(url)
    if not fetched.get("ok"):
        return {"url": url, "ok": False, "error": fetched.get("error")}
    html = fetched["html"]
    soup = BeautifulSoup(html, "html.parser")
    checks = _check_each(soup, html, url)

    # Score: 100 - 8pt per detected CWV-x, 4pt per detected BONUS
    detected = sum(1 for k, v in checks.items() if v.get("detected") and k.startswith("CWV-"))
    bonus_detected = sum(1 for k, v in checks.items() if v.get("detected") and k.startswith("BONUS"))
    score = max(0, 100 - 8 * detected - 4 * bonus_detected)

    items: List[Dict[str, Any]] = []
    for c in CWV_CATALOG:
        d = checks.get(c["id"], {})
        items.append({**c, **d})

    return {
        "url": url,
        "ok": True,
        "score": score,
        "detected_count": detected,
        "total_imgs": len(soup.find_all("img")),
        "total_scripts": len(soup.find_all("script")),
        "html_size": len(html),
        "items": items,
        "bonus": {k: v for k, v in checks.items() if k.startswith("BONUS")},
    }
