"""
Backend regression tests for event slug feature (multilingual SEO URLs).
Covers:
- GET /api/events/by-slug/{slug} (new endpoint)
- GET /api/events/{id} returns 'slug' field
- GET /api/events?limit=20 returns 'slug' for each
- GET /api/sitemap.xml uses /biglietti-{slug}, /{slug}-tickets, /entradas-{slug}
- POST /api/admin/sync/event-slugs (auth required)
- GET /api/prerender/event/{slug} works with slug
- GET /api/prerender/event/{ObjectId} backward compat
- Slug uniqueness in DB (no duplicates without -2/-3 suffix)
- Regression: /api/health, /api/admin/login, /api/prerender/home
"""
import os
import re
import requests
import pytest

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://sports-events-2.preview.emergentagent.com").rstrip("/")
ADMIN_USER = "admin"
ADMIN_PASS = "golevents2024"


# ---------- fixtures ----------
@pytest.fixture(scope="session")
def http():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def admin_token(http):
    r = http.post(f"{BASE_URL}/api/admin/login", json={"username": ADMIN_USER, "password": ADMIN_PASS})
    if r.status_code != 200:
        pytest.skip(f"Admin login failed: {r.status_code} {r.text}")
    tok = r.json().get("token") or r.json().get("access_token")
    if not tok:
        pytest.skip("No token in admin login response")
    return tok


@pytest.fixture(scope="session")
def sample_event(http):
    """Pick an arbitrary real event from /api/events."""
    r = http.get(f"{BASE_URL}/api/events?limit=20")
    assert r.status_code == 200, r.text
    events = r.json().get("events", [])
    assert events, "No events available in DB"
    # Prefer an event that has a slug containing -vs-
    for ev in events:
        if ev.get("slug") and "-vs-" in ev["slug"]:
            return ev
    return events[0]


# ---------- /api/events list ----------
class TestEventsList:
    def test_events_list_has_slug_per_event(self, http):
        r = http.get(f"{BASE_URL}/api/events?limit=20")
        assert r.status_code == 200, r.text
        data = r.json()
        events = data.get("events", [])
        assert len(events) > 0, "Expected at least one event"
        missing = [e.get("id") for e in events if not e.get("slug")]
        assert not missing, f"Events missing slug: {missing}"
        # Slug should be lowercase-dashes only
        for e in events:
            slug = e["slug"]
            assert re.match(r"^[a-z0-9][a-z0-9\-]*$", slug), f"Bad slug format: {slug}"


# ---------- /api/events/by-slug/{slug} ----------
class TestEventBySlug:
    def test_get_event_by_real_slug(self, http, sample_event):
        slug = sample_event["slug"]
        r = http.get(f"{BASE_URL}/api/events/by-slug/{slug}")
        assert r.status_code == 200, f"Slug={slug} -> {r.status_code} {r.text}"
        ev = r.json()
        assert ev.get("slug") == slug
        assert ev.get("id"), "Event must have id"
        # Required fields per request
        for f in ("home_team", "away_team", "stadium", "date"):
            assert f in ev, f"Missing field {f} in by-slug response"

    def test_get_event_by_nonexistent_slug_returns_404(self, http):
        r = http.get(f"{BASE_URL}/api/events/by-slug/non-esistente-abc-zzz-12345")
        assert r.status_code == 404


# ---------- /api/events/{id} ----------
class TestEventById:
    def test_get_event_by_id_includes_slug(self, http, sample_event):
        eid = sample_event["id"]
        r = http.get(f"{BASE_URL}/api/events/{eid}")
        assert r.status_code == 200, r.text
        ev = r.json()
        assert ev.get("slug"), f"Slug must be populated. Got: {ev}"
        assert ev["id"] == eid


# ---------- /api/sitemap.xml ----------
class TestSitemapEventUrls:
    def test_sitemap_uses_new_event_slug_urls(self, http, sample_event):
        r = http.get(f"{BASE_URL}/api/sitemap.xml")
        assert r.status_code == 200
        body = r.text
        slug = sample_event["slug"]
        # New format URLs
        assert f"/biglietti-{slug}" in body, f"sitemap missing /biglietti-{slug}"
        assert f"/{slug}-tickets" in body, f"sitemap missing /{slug}-tickets"
        assert f"/entradas-{slug}" in body, f"sitemap missing /entradas-{slug}"

    def test_sitemap_does_not_emit_old_event_id_urls(self, http, sample_event):
        r = http.get(f"{BASE_URL}/api/sitemap.xml")
        assert r.status_code == 200
        eid = sample_event["id"]
        # Should not have /event/{ObjectId} for sample_event in sitemap anymore
        assert f"/event/{eid}" not in r.text, "sitemap still references legacy /event/{id}"


# ---------- /api/admin/sync/event-slugs ----------
class TestAdminSyncEventSlugs:
    def test_sync_event_slugs_requires_auth(self, http):
        r = http.post(f"{BASE_URL}/api/admin/sync/event-slugs")
        assert r.status_code in (401, 403), f"Expected 401/403, got {r.status_code}"

    def test_sync_event_slugs_with_admin_token(self, http, admin_token):
        r = http.post(
            f"{BASE_URL}/api/admin/sync/event-slugs",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert r.status_code == 200, f"{r.status_code} {r.text}"
        data = r.json()
        # Response wraps stats: {success: True, stats: {updated, skipped, total_slugs}}
        stats = data.get("stats", data)
        for key in ("updated", "skipped", "total_slugs"):
            assert key in stats, f"Missing key {key} in response: {data}"
        assert isinstance(stats["total_slugs"], int)
        assert stats["total_slugs"] > 0


# ---------- /api/prerender/event/{slug | id} ----------
class TestPrerenderEvent:
    def test_prerender_event_by_slug(self, http, sample_event):
        slug = sample_event["slug"]
        r = http.get(f"{BASE_URL}/api/prerender/event/{slug}")
        assert r.status_code == 200, f"{r.status_code} {r.text[:300]}"
        html = r.text
        assert "<title>" in html
        assert "application/ld+json" in html
        assert '"@type":"SportsEvent"' in html or '"@type": "SportsEvent"' in html

    def test_prerender_event_by_objectid_backward_compat(self, http, sample_event):
        eid = sample_event["id"]
        r = http.get(f"{BASE_URL}/api/prerender/event/{eid}")
        assert r.status_code == 200, f"ObjectId prerender failed: {r.status_code}"
        assert "<title>" in r.text


# ---------- DB-level slug guarantees ----------
class TestDBSlugIntegrity:
    def test_all_events_in_listing_have_slug(self, http):
        # paginate first 100
        r = http.get(f"{BASE_URL}/api/events?limit=100&include_past=true")
        assert r.status_code == 200
        events = r.json().get("events", [])
        assert events
        no_slug = [e["id"] for e in events if not e.get("slug")]
        assert not no_slug, f"Events without slug: {no_slug[:5]}"

    def test_no_duplicate_slugs_in_first_pages(self, http):
        slug_to_id = {}
        seen_ids = set()
        for page in range(1, 6):  # check first 5 pages * 100 = 500 events
            r = http.get(f"{BASE_URL}/api/events?limit=100&page={page}&include_past=true")
            if r.status_code != 200:
                break
            evs = r.json().get("events", [])
            if not evs:
                break
            for e in evs:
                eid = e.get("id")
                slug = e.get("slug")
                if not slug or not eid:
                    continue
                # Skip if same event already seen (pagination overlap on tied sort_date)
                if eid in seen_ids:
                    continue
                seen_ids.add(eid)
                if slug in slug_to_id and slug_to_id[slug] != eid:
                    pytest.fail(f"Duplicate slug '{slug}' for distinct events {slug_to_id[slug]} and {eid}")
                slug_to_id[slug] = eid


# ---------- Regression ----------
class TestRegression:
    def test_health(self, http):
        r = http.get(f"{BASE_URL}/api/health")
        assert r.status_code == 200

    def test_admin_login(self, http):
        r = http.post(f"{BASE_URL}/api/admin/login", json={"username": ADMIN_USER, "password": ADMIN_PASS})
        assert r.status_code == 200
        assert r.json().get("token") or r.json().get("access_token")

    def test_prerender_home(self, http):
        r = http.get(f"{BASE_URL}/api/prerender/home")
        assert r.status_code == 200
        assert "<title>" in r.text
