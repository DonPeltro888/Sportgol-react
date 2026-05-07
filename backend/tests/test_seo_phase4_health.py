"""
FASE 4 — SEO Health Check (Perplexity + Gemini Vision) + bug fix Inter↔Inter Miami leakage.
"""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://sports-events-2.preview.emergentagent.com").rstrip("/")
ADMIN_USER = "admin"
ADMIN_PASS = "golevents2024"


@pytest.fixture(scope="module")
def auth_token():
    r = requests.post(
        f"{BASE_URL}/api/admin/login",
        json={"username": ADMIN_USER, "password": ADMIN_PASS},
        timeout=15,
    )
    if r.status_code != 200:
        pytest.skip(f"Auth failed: {r.status_code} {r.text}")
    tok = r.json().get("token")
    assert tok, "No token returned"
    return tok


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


# ─── BUG FIX #1: Inter ≠ Inter Miami leakage ────────────────────────────────

class TestTeamSlugLeakage:
    def test_inter_returns_only_serie_a_no_inter_miami(self):
        r = requests.get(f"{BASE_URL}/api/events/by-team-slug/inter", timeout=20)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["team"]["slug"] == "inter"
        assert d["team"]["name"].lower() == "inter"
        assert d["team"].get("league_slug") == "serie-a"
        # NO Inter Miami in any event
        for ev in d["events"]:
            ht = (ev.get("home_team") or "").lower()
            at = (ev.get("away_team") or "").lower()
            assert "miami" not in ht, f"Leakage in home_team: {ev.get('home_team')}"
            assert "miami" not in at, f"Leakage in away_team: {ev.get('away_team')}"
            assert ht == "inter" or at == "inter", f"Event without Inter: {ht} vs {at}"
        # total should match length
        assert d["total"] == len(d["events"])

    def test_roma_no_collision(self):
        r = requests.get(f"{BASE_URL}/api/events/by-team-slug/roma", timeout=20)
        # If team exists, validate
        if r.status_code == 200:
            d = r.json()
            assert d["team"]["slug"] == "roma"
            for ev in d["events"]:
                ht = (ev.get("home_team") or "").lower()
                at = (ev.get("away_team") or "").lower()
                # Should not include FC Roma or other roma-prefixed/suffixed
                assert ht == "roma" or at == "roma", f"Wrong match: {ht} vs {at}"
        elif r.status_code == 404:
            pytest.skip("Team 'roma' not in DB")
        else:
            pytest.fail(f"Unexpected status: {r.status_code}")


# ─── BUG FIX #2: Public team page H1 (server-side rendered or SPA) ───────────

class TestPublicTeamPage:
    def test_biglietti_inter_no_long_h1_pattern(self):
        r = requests.get(f"{BASE_URL}/biglietti-inter", timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        # Accept 200 (SPA) — check that no problematic long H1 phrase is hardcoded
        assert r.status_code == 200, r.text
        body_lower = r.text.lower()
        # Long pattern that should NOT be in H1
        assert "confronta prezzi e posti" not in body_lower, "Long H1 pattern still present"


# ─── HEALTH SCAN ─────────────────────────────────────────────────────────────

class TestHealthScan:
    def test_scan_endpoint_returns_summary(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/seo/health/scan", headers=auth_headers, timeout=60)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d.get("ok") is True
        assert "summary" in d
        s = d["summary"]
        assert "total_issues" in s
        assert "by_category" in s
        assert "by_severity" in s
        # severity buckets
        for k in ("high", "medium", "low"):
            assert k in s["by_severity"], f"Missing severity {k}"
        # 6 expected categories present in code (might not all appear if no issues - check structure)
        assert "teams" in d and "issues" in d["teams"]
        assert "events" in d and "issues" in d["events"]
        assert "leagues" in d and "issues" in d["leagues"]
        # at least one of these categories should be possible
        expected_cats = {"missing_data", "logo_collision", "name_confusion", "fuzzy_duplicate",
                         "orphan_event_team", "league_missing_data", "event_missing_data", "duplicate_slug"}
        actual_cats = set(s["by_category"].keys())
        # at least one expected cat present (DB has issues)
        assert actual_cats & expected_cats, f"No expected categories: {actual_cats}"

    def test_scan_requires_auth(self):
        r = requests.get(f"{BASE_URL}/api/seo/health/scan", timeout=15)
        assert r.status_code in (401, 403), f"Expected auth required, got {r.status_code}"


class TestHealthRunSave:
    def test_run_saves_report(self, auth_headers):
        r = requests.post(f"{BASE_URL}/api/seo/health/run", headers=auth_headers, timeout=60)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d.get("ok") is True
        assert "report_id" in d
        assert "summary" in d

    def test_latest_report(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/seo/health/report/latest", headers=auth_headers, timeout=20)
        assert r.status_code == 200, r.text
        d = r.json()
        # If a report exists, should have summary
        assert "summary" in d or d.get("error"), "No summary nor error"
        if "summary" in d:
            assert "total_issues" in d["summary"]


# ─── EXPORT ──────────────────────────────────────────────────────────────────

class TestHealthExport:
    def test_export_json(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/seo/health/export?format=json",
                         headers=auth_headers, timeout=30)
        assert r.status_code == 200, r.text
        cd = r.headers.get("content-disposition", "")
        assert "attachment" in cd
        assert ".json" in cd

    def test_export_csv(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/seo/health/export?format=csv",
                         headers=auth_headers, timeout=30)
        assert r.status_code == 200, r.text
        cd = r.headers.get("content-disposition", "")
        assert "attachment" in cd
        assert ".csv" in cd
        # CSV should have header line
        first_line = r.text.split("\n", 1)[0]
        assert "category" in first_line and "severity" in first_line


# ─── BULK FIX (job queue) ────────────────────────────────────────────────────

class TestBulkFixJobQueue:
    def test_bulk_fix_creates_job(self, auth_headers):
        payload = {"mode": "balanced",
                   "only_categories": ["missing_data", "logo_collision"],
                   "limit": 2}
        r = requests.post(f"{BASE_URL}/api/seo/health/fix-bulk",
                          headers=auth_headers, json=payload, timeout=20)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d.get("ok") is True
        if d.get("queued", 0) == 0:
            pytest.skip("No issues to fix in current report")
        assert "job_id" in d
        job_id = d["job_id"]
        # poll
        rj = requests.get(f"{BASE_URL}/api/seo/health/fix-jobs/{job_id}",
                          headers=auth_headers, timeout=15)
        assert rj.status_code == 200, rj.text
        jd = rj.json()
        assert jd["_id"] == job_id
        assert jd["status"] in ("queued", "running", "succeeded", "failed")


# ─── FIX TEAM (Perplexity + Gemini Vision) ──────────────────────────────────
# Long-running: ~30-60s. Run last.

class TestFixTeam:
    def test_fix_team_inter_returns_response(self, auth_headers):
        # idempotent: may return applied:false if already fixed
        r = requests.post(
            f"{BASE_URL}/api/seo/health/fix-team/inter",
            headers={**auth_headers, "Content-Type": "application/json"},
            json={"mode": "balanced"},
            timeout=120,
        )
        assert r.status_code == 200, r.text
        d = r.json()
        assert "ok" in d
        assert "applied" in d
        # actions key exists
        assert "actions" in d or d.get("ok") is False
