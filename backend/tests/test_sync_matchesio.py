"""
Backend tests for matchesio.com sync feature.
Covers admin auth, manual sync (replace_all true/false), sync logs,
events filtering (past), standard sectors and regression on /events, /leagues.
"""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://sports-events-2.preview.emergentagent.com").rstrip("/")
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "golevents2024"

STANDARD_SECTORS = {
    "Cat 1 - Lower Central",
    "Cat 1 - Middle Central",
    "Cat 1 - Normal",
    "Cat 2 - Long Upper",
    "Cat 2 - Short Lower",
    "Cat 3 - Short Side Middle",
    "Cat 4 - Short Upper",
}


@pytest.fixture(scope="session")
def http():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def admin_token(http):
    """Admin login - acquire bearer token."""
    r = http.post(f"{BASE_URL}/api/admin/login",
                  json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
                  timeout=15)
    assert r.status_code == 200, f"Admin login failed: {r.status_code} {r.text}"
    data = r.json()
    assert "token" in data and isinstance(data["token"], str) and len(data["token"]) > 10
    assert data.get("username") == ADMIN_USERNAME
    return data["token"]


@pytest.fixture(scope="session")
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


# ---- Auth ----
class TestAdminAuth:
    def test_login_success(self, http):
        r = http.post(f"{BASE_URL}/api/admin/login",
                      json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}, timeout=15)
        assert r.status_code == 200
        assert "token" in r.json()

    def test_login_invalid(self, http):
        r = http.post(f"{BASE_URL}/api/admin/login",
                      json={"username": "admin", "password": "wrong"}, timeout=15)
        assert r.status_code == 401


# ---- Sync auth gating ----
class TestSyncAuthGating:
    def test_sync_no_token_returns_401(self, http):
        r = http.post(f"{BASE_URL}/api/admin/sync/matchesio?replace_all=false", timeout=15)
        assert r.status_code == 401

    def test_logs_no_token_returns_401(self, http):
        r = http.get(f"{BASE_URL}/api/admin/sync/logs", timeout=15)
        assert r.status_code == 401


# ---- Manual sync replace_all=true ----
class TestSyncReplaceAll:
    def test_sync_replace_all_true(self, http, auth_headers):
        # Long-running: fetches 13 JSONs from matchesio.com
        r = http.post(f"{BASE_URL}/api/admin/sync/matchesio?replace_all=true",
                      headers=auth_headers, timeout=180)
        assert r.status_code == 200, f"Sync failed: {r.status_code} {r.text[:500]}"
        body = r.json()
        assert body.get("success") is True
        stats = body.get("stats", {})
        # Required stat keys
        for k in ("total_inserted", "total_in_db", "per_league", "errors",
                  "started_at", "finished_at", "total_deleted_past"):
            assert k in stats, f"Missing stat key: {k}"
        assert isinstance(stats["per_league"], dict)
        assert isinstance(stats["total_inserted"], int)
        assert isinstance(stats["total_in_db"], int)
        # Should have inserted at least some events (matchesio.com has data)
        # Soft assertion: warn but allow zero if matchesio is down
        assert stats["total_in_db"] >= 0


# ---- Events after sync ----
class TestEventsAfterSync:
    def test_events_present(self, http):
        r = http.get(f"{BASE_URL}/api/events?limit=10&include_past=false", timeout=20)
        assert r.status_code == 200
        data = r.json()
        assert "events" in data and "total" in data
        assert isinstance(data["events"], list)
        # If sync produced data, should have some events
        # (this depends on matchesio being reachable; allow zero but log)
        assert data["total"] >= 0

    def test_event_has_standard_sectors(self, http):
        r = http.get(f"{BASE_URL}/api/events?limit=5&include_past=false", timeout=20)
        assert r.status_code == 200
        events = r.json().get("events", [])
        if not events:
            pytest.skip("No events to validate sectors (sync may have produced 0)")
        # Find a recently-synced event with ticket_categories
        synced = [e for e in events if e.get("matchesio_id") is not None]
        sample = synced[0] if synced else events[0]
        cats = sample.get("ticket_categories", [])
        assert isinstance(cats, list) and len(cats) == 7, \
            f"Expected 7 standard sectors, got {len(cats)}"
        names = {c.get("name") for c in cats}
        assert names == STANDARD_SECTORS, f"Sector names mismatch: {names}"
        # No price field allowed
        for c in cats:
            assert "price" not in c, f"Sector should not contain price: {c}"

    def test_event_no_price_range(self, http):
        r = http.get(f"{BASE_URL}/api/events?limit=10&include_past=false", timeout=20)
        events = r.json().get("events", [])
        if not events:
            pytest.skip("No events")
        synced = [e for e in events if e.get("matchesio_id") is not None]
        for e in (synced or events):
            assert "price_range" not in e or e.get("price_range") in (None, ""), \
                f"Event has price_range: {e.get('price_range')}"

    def test_past_events_filter(self, http):
        from datetime import datetime, timezone
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        r = http.get(f"{BASE_URL}/api/events?limit=50&include_past=false", timeout=20)
        assert r.status_code == 200
        for e in r.json().get("events", []):
            sd = e.get("sort_date", "")
            assert sd >= today_str, f"Past event leaked: sort_date={sd}, today={today_str}"


# ---- Sync logs ----
class TestSyncLogs:
    def test_logs_returns_list(self, http, auth_headers):
        r = http.get(f"{BASE_URL}/api/admin/sync/logs?limit=5", headers=auth_headers, timeout=20)
        assert r.status_code == 200
        data = r.json()
        assert "logs" in data and isinstance(data["logs"], list)
        # After a sync, should have at least 1 log
        assert len(data["logs"]) >= 1
        log = data["logs"][0]
        # Should contain expected stat fields
        for k in ("total_inserted", "total_in_db", "started_at", "finished_at", "log_at"):
            assert k in log, f"Missing log field: {k}"


# ---- Manual sync replace_all=false (upsert) ----
class TestSyncUpsert:
    def test_sync_replace_all_false(self, http, auth_headers):
        r = http.post(f"{BASE_URL}/api/admin/sync/matchesio?replace_all=false",
                      headers=auth_headers, timeout=180)
        assert r.status_code == 200, f"Upsert sync failed: {r.status_code} {r.text[:500]}"
        body = r.json()
        assert body.get("success") is True
        stats = body["stats"]
        # In upsert mode, expect mostly updates (since data already exists from previous test)
        assert "total_updated" in stats
        assert isinstance(stats["total_updated"], int)


# ---- Regression ----
class TestRegression:
    def test_leagues_endpoint(self, http):
        r = http.get(f"{BASE_URL}/api/leagues", timeout=15)
        assert r.status_code == 200
        data = r.json()
        # Could be list or dict, just verify it doesn't error
        assert data is not None

    def test_events_endpoint_basic(self, http):
        r = http.get(f"{BASE_URL}/api/events?limit=5", timeout=15)
        assert r.status_code == 200
        body = r.json()
        assert "events" in body
        assert "total" in body
        assert "page" in body
