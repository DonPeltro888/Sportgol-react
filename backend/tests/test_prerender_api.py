"""
Backend SEO + Prerender API regression tests.
Covers the 4 new /api/prerender/* endpoints + regression checks that existing
endpoints (/api/health, /api/events, /api/sitemap.xml, /api/admin/*) still work
after the prerender router was added to server.py.

Target: production preview URL via REACT_APP_BACKEND_URL.
"""
import os
import re
import json as _json
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://sports-events-2.preview.emergentagent.com").rstrip("/")
TIMEOUT = 30


@pytest.fixture(scope="module")
def api_client():
    s = requests.Session()
    return s


@pytest.fixture(scope="module")
def sample_event_id(api_client):
    r = api_client.get(f"{BASE_URL}/api/events?limit=1", timeout=TIMEOUT)
    assert r.status_code == 200, f"/api/events failed: {r.status_code}"
    data = r.json()
    events = data.get("events") or data  # tolerate both shapes
    assert events and len(events) > 0, "No events in DB - can't test /prerender/event"
    ev = events[0]
    eid = ev.get("_id") or ev.get("id")
    assert eid, f"Event missing id field: {ev}"
    return str(eid)


# ----------------------------- Regression --------------------------------- #
class TestRegressionExistingEndpoints:
    """Ensure including prerender router didn't break existing endpoints."""

    def test_health_ok(self, api_client):
        r = api_client.get(f"{BASE_URL}/api/health", timeout=TIMEOUT)
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") in ("ok", "degraded")
        assert data.get("db") == "ok"
        assert isinstance(data.get("events_count"), int)
        assert data["events_count"] > 0

    def test_events_listing(self, api_client):
        r = api_client.get(f"{BASE_URL}/api/events?limit=5", timeout=TIMEOUT)
        assert r.status_code == 200
        data = r.json()
        events = data.get("events") or data
        assert isinstance(events, list)
        assert len(events) > 0
        # No raw Mongo ObjectId binary should leak - should be str
        for ev in events:
            eid = ev.get("_id") or ev.get("id")
            assert isinstance(eid, str)

    def test_sitemap_xml(self, api_client):
        r = api_client.get(f"{BASE_URL}/api/sitemap.xml", timeout=TIMEOUT)
        assert r.status_code == 200
        assert "xml" in r.headers.get("content-type", "").lower()
        body = r.text
        assert "<urlset" in body
        assert f"{BASE_URL}/" in body
        # Must contain some league slug
        assert "biglietti-serie-a" in body
        assert "biglietti-champions-league" in body
        # Must contain events URLs
        assert "/event/" in body

    def test_robots_backend_endpoint(self, api_client):
        r = api_client.get(f"{BASE_URL}/api/robots.txt", timeout=TIMEOUT)
        assert r.status_code == 200
        assert "User-agent:" in r.text
        assert "Sitemap:" in r.text
        assert "Disallow: /admin/" in r.text

    def test_static_robots_txt_served_by_frontend(self, api_client):
        # Frontend serves /robots.txt (not under /api). Should return static file.
        r = api_client.get(f"{BASE_URL}/robots.txt", timeout=TIMEOUT)
        assert r.status_code == 200, f"/robots.txt returned {r.status_code}"
        assert "Sitemap:" in r.text
        assert "/api/sitemap.xml" in r.text
        assert "Disallow: /admin/" in r.text

    def test_static_llms_txt_served_by_frontend(self, api_client):
        r = api_client.get(f"{BASE_URL}/llms.txt", timeout=TIMEOUT)
        assert r.status_code == 200, f"/llms.txt returned {r.status_code}"
        # Minimal sanity checks
        assert "GOLEVENTS" in r.text
        assert "Serie A" in r.text or "serie-a" in r.text

    def test_admin_login_still_works(self, api_client):
        r = api_client.post(
            f"{BASE_URL}/api/admin/login",
            json={"username": "admin", "password": "golevents2024"},
            timeout=TIMEOUT,
        )
        assert r.status_code == 200, f"admin login failed: {r.status_code} {r.text[:300]}"
        data = r.json()
        assert "token" in data or "access_token" in data


# --------------------------- Prerender: Home ------------------------------ #
class TestPrerenderHome:
    def test_home_returns_html_200(self, api_client):
        r = api_client.get(f"{BASE_URL}/api/prerender/home", timeout=TIMEOUT)
        assert r.status_code == 200
        assert "text/html" in r.headers.get("content-type", "").lower()

    def test_home_contains_seo_basics(self, api_client):
        html = api_client.get(f"{BASE_URL}/api/prerender/home", timeout=TIMEOUT).text
        # Title + description
        assert "<title>" in html and "GOLEVENTS" in html
        assert 'name="description"' in html
        assert 'rel="canonical"' in html
        # OG + Twitter cards
        assert 'property="og:title"' in html
        assert 'name="twitter:card"' in html
        # hreflang
        assert 'hreflang="it"' in html and 'hreflang="en"' in html and 'hreflang="es"' in html

    def test_home_has_jsonld_org_and_website(self, api_client):
        html = api_client.get(f"{BASE_URL}/api/prerender/home", timeout=TIMEOUT).text
        scripts = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>',
            html,
            flags=re.DOTALL,
        )
        assert len(scripts) >= 2, f"Expected >=2 JSON-LD blocks, found {len(scripts)}"
        types = []
        for s in scripts:
            try:
                types.append(_json.loads(s).get("@type"))
            except Exception as e:
                pytest.fail(f"Invalid JSON-LD: {e} -> {s[:200]}")
        assert "Organization" in types
        assert "WebSite" in types

    def test_home_contains_keyword_content(self, api_client):
        html = api_client.get(f"{BASE_URL}/api/prerender/home", timeout=TIMEOUT).text
        # Must include keywords crawlers look for
        for kw in ["Serie A", "Premier League", "Champions League", "Biglietti"]:
            assert kw in html, f"Missing keyword '{kw}' in prerender home"
        # Must include at least one league link
        assert "/biglietti-" in html


# ------------------------ Prerender: League ------------------------------- #
class TestPrerenderLeague:
    @pytest.mark.parametrize("slug", ["serie-a", "champions-league"])
    def test_league_200_with_schema(self, api_client, slug):
        r = api_client.get(f"{BASE_URL}/api/prerender/league/{slug}", timeout=TIMEOUT)
        assert r.status_code == 200, f"/league/{slug} -> {r.status_code}"
        html = r.text
        assert "<title>" in html
        # Schema org SportsOrganization or SportsEvent (cup)
        scripts = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', html, flags=re.DOTALL
        )
        assert scripts, "No JSON-LD in league page"
        types = [_json.loads(s).get("@type") for s in scripts]
        assert any(t in ("SportsOrganization", "SportsEvent") for t in types), types

    def test_league_404_for_unknown_slug(self, api_client):
        r = api_client.get(f"{BASE_URL}/api/prerender/league/does-not-exist-xyz", timeout=TIMEOUT)
        assert r.status_code == 404


# ------------------------ Prerender: Team --------------------------------- #
class TestPrerenderTeam:
    @pytest.mark.parametrize("slug", ["inter", "liverpool"])
    def test_team_200_with_schema(self, api_client, slug):
        r = api_client.get(f"{BASE_URL}/api/prerender/team/{slug}", timeout=TIMEOUT)
        assert r.status_code == 200, f"/team/{slug} -> {r.status_code}"
        html = r.text
        assert "<title>" in html
        assert "Biglietti" in html
        scripts = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', html, flags=re.DOTALL
        )
        assert scripts, "No JSON-LD in team page"
        parsed = _json.loads(scripts[0])
        assert parsed.get("@type") == "SportsTeam"
        assert parsed.get("name")


# ------------------------ Prerender: Event -------------------------------- #
class TestPrerenderEvent:
    def test_event_200_valid(self, api_client, sample_event_id):
        r = api_client.get(f"{BASE_URL}/api/prerender/event/{sample_event_id}", timeout=TIMEOUT)
        assert r.status_code == 200, f"event {sample_event_id} -> {r.status_code}"
        html = r.text
        assert "<title>" in html and "Biglietti" in html
        scripts = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', html, flags=re.DOTALL
        )
        assert len(scripts) >= 1
        types = [_json.loads(s).get("@type") for s in scripts]
        assert "SportsEvent" in types
        assert "BreadcrumbList" in types

    def test_event_404_invalid(self, api_client):
        r = api_client.get(f"{BASE_URL}/api/prerender/event/nonexistent-event-id-xxx", timeout=TIMEOUT)
        assert r.status_code == 404


# ---------------------- Googlebot simulation ------------------------------ #
class TestGooglebotHomepage:
    """Simulate Googlebot hitting the React homepage to ensure index.html
    fallback content (JSON-LD, keywords, meta tags) is served."""

    def test_homepage_as_googlebot_has_seo_fallback(self, api_client):
        headers = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}
        r = api_client.get(f"{BASE_URL}/", headers=headers, timeout=TIMEOUT)
        assert r.status_code == 200
        html = r.text
        # Title + meta description
        assert "<title>" in html
        assert 'name="description"' in html
        # JSON-LD schema blocks (Organization, WebSite, SportsActivityLocation)
        scripts = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', html, flags=re.DOTALL
        )
        assert len(scripts) >= 3, f"Expected >=3 JSON-LD blocks in index.html, got {len(scripts)}"
        types = []
        for s in scripts:
            try:
                types.append(_json.loads(s).get("@type"))
            except Exception:
                pass
        for t in ("Organization", "WebSite", "SportsActivityLocation"):
            assert t in types, f"Missing @type={t} in index.html JSON-LD; got {types}"
        # Keyword content visible in fallback (noscript/hidden text)
        for kw in ["Serie A", "Premier League", "Juventus", "Inter", "Champions League"]:
            assert kw in html, f"Missing keyword '{kw}' in Googlebot homepage HTML"
