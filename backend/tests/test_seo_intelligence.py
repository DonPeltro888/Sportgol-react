"""
SEO Intelligence Hub backend tests (iteration 12).
Covers: topic-cluster, cannibalization, hreflang, jsonld, faq (public+admin), trust-score,
team-verifier (latest only — run is slow Perplexity), and Coppa Italia case-insensitive
league regression on /api/events.
"""
import os
import time
import pytest
import requests
from pathlib import Path


def _load_backend_url():
    url = os.environ.get("REACT_APP_BACKEND_URL", "").strip()
    if url:
        return url.rstrip("/")
    env_path = Path("/app/frontend/.env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("REACT_APP_BACKEND_URL="):
                return line.split("=", 1)[1].strip().rstrip("/")
    raise RuntimeError("REACT_APP_BACKEND_URL not configured")


BASE_URL = _load_backend_url()
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "golevents2024"

API = f"{BASE_URL}/api"


# ============ Fixtures ============
@pytest.fixture(scope="session")
def admin_token():
    r = requests.post(f"{API}/admin/login", json={
        "username": ADMIN_USERNAME, "password": ADMIN_PASSWORD,
    }, timeout=15)
    assert r.status_code == 200, f"Admin login failed: {r.status_code} {r.text}"
    tok = r.json().get("token")
    assert tok
    return tok


@pytest.fixture(scope="session")
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


# ============ Topic Cluster ============
class TestTopicCluster:
    def test_overview(self, auth_headers):
        r = requests.get(f"{API}/seo/intelligence/topic-cluster/overview",
                         headers=auth_headers, timeout=30)
        assert r.status_code == 200, r.text
        d = r.json()
        for k in ("total_leagues", "total_teams", "total_events_future", "league_hubs"):
            assert k in d, f"missing key {k}: {d.keys()}"
        assert isinstance(d["league_hubs"], list)
        assert d["total_leagues"] >= 1 and d["total_teams"] >= 1 and d["total_events_future"] >= 1

    def test_league_serie_a_links(self, auth_headers):
        r = requests.get(f"{API}/seo/intelligence/topic-cluster/league/serie-a",
                         headers=auth_headers, timeout=30)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["entity_type"] == "league"
        assert d["slug"] == "serie-a"
        assert d["count"] >= 14, f"expected >=14 links, got {d['count']}"
        rels = {l.get("rel") for l in d["links"]}
        # at least one of these expected categories
        assert "child_team" in rels or "child_event" in rels, f"unexpected rels: {rels}"

    def test_team_links_has_parent_league(self, auth_headers):
        # find one team in serie-a
        r0 = requests.get(f"{API}/seo/intelligence/topic-cluster/league/serie-a",
                          headers=auth_headers, timeout=30)
        team_link = next((l for l in r0.json()["links"] if l.get("rel") == "child_team"), None)
        if not team_link:
            pytest.skip("no team child link in serie-a cluster")
        # url format: /squadra/<slug>
        url = team_link.get("url", "")
        team_slug = url.rstrip("/").split("/")[-1]
        r = requests.get(f"{API}/seo/intelligence/topic-cluster/team/{team_slug}",
                         headers=auth_headers, timeout=30)
        assert r.status_code == 200, r.text
        d = r.json()
        rels = {l.get("rel") for l in d["links"]}
        assert "parent_league" in rels, f"team must link to parent_league: {rels}"

    def test_event_links_no_inter_miami_collision(self, auth_headers):
        # Find an event involving Inter (Serie A)
        r = requests.get(f"{API}/events?league=Serie%20A&limit=100", timeout=20)
        assert r.status_code == 200, r.text
        body = r.json()
        events = body.get("events") if isinstance(body, dict) else body
        inter_event = next(
            (e for e in events if (e.get("home_team") or "").strip().lower() == "inter"
             or (e.get("away_team") or "").strip().lower() == "inter"),
            None,
        )
        if not inter_event:
            pytest.skip("no Inter event found")
        slug = inter_event["slug"]
        r2 = requests.get(f"{API}/seo/intelligence/topic-cluster/event/{slug}",
                          headers=auth_headers, timeout=30)
        assert r2.status_code == 200, r2.text
        links = r2.json()["links"]
        rels = {l.get("rel") for l in links}
        assert "parent_league" in rels
        # ensure no Inter Miami leakage in any url/anchor
        for l in links:
            blob = (l.get("anchor", "") + " " + l.get("url", "")).lower()
            assert "miami" not in blob, f"Inter Miami leakage found: {l}"


# ============ Cannibalization ============
class TestCannibalization:
    def test_scan_threshold_85(self, auth_headers):
        t0 = time.time()
        r = requests.get(f"{API}/seo/intelligence/cannibalization/scan?threshold=85&limit=200",
                         headers=auth_headers, timeout=30)
        elapsed = time.time() - t0
        assert r.status_code == 200, r.text
        d = r.json()
        assert "issues" in d
        assert elapsed < 10, f"scan too slow: {elapsed}s"
        for issue in d["issues"][:5]:
            assert "severity" in issue
            assert issue["severity"] in ("HIGH", "MEDIUM", "LOW")
            assert "recommendation" in issue

    def test_scan_threshold_95_stricter(self, auth_headers):
        r85 = requests.get(f"{API}/seo/intelligence/cannibalization/scan?threshold=85&limit=200",
                           headers=auth_headers, timeout=30).json()
        r95 = requests.get(f"{API}/seo/intelligence/cannibalization/scan?threshold=95&limit=200",
                           headers=auth_headers, timeout=30).json()
        # stricter threshold => issues count cannot grow
        n85 = len(r85.get("issues", []))
        n95 = len(r95.get("issues", []))
        assert n95 <= n85, f"95 stricter must not be more than 85 (got {n95}>{n85})"


# ============ Hreflang ============
class TestHreflang:
    def test_scan_returns_invalid(self, auth_headers):
        r = requests.get(f"{API}/seo/intelligence/hreflang/scan?limit=100",
                         headers=auth_headers, timeout=30)
        assert r.status_code == 200, r.text
        d = r.json()
        # Schema: rows + total_invalid + by_severity
        assert "rows" in d
        assert "total_invalid" in d
        assert "by_severity" in d
        if d["rows"]:
            sample = d["rows"][0]
            assert "is_valid" in sample
            assert "expected_langs" in sample

    def test_validate_serie_a(self, auth_headers):
        r = requests.get(f"{API}/seo/intelligence/hreflang/league/serie-a",
                         headers=auth_headers, timeout=15)
        assert r.status_code == 200, r.text
        d = r.json()
        # Should at minimum tell us valid/invalid + issues (if any)
        assert "valid" in d or "issues" in d or "ok" in d


# ============ FAQ ============
class TestFaq:
    def test_get_faq_admin(self, auth_headers):
        r = requests.get(f"{API}/seo/intelligence/faq/league/serie-a?lang=it",
                         headers=auth_headers, timeout=15)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["entity_type"] == "league"
        assert d["slug"] == "serie-a"
        assert d["lang"] == "it"
        assert "faq" in d
        assert isinstance(d["faq"], list)

    def test_faq_public_no_auth(self):
        r = requests.get(f"{API}/seo/intelligence/faq/league/serie-a/public?lang=it", timeout=15)
        assert r.status_code == 200, r.text
        d = r.json()
        assert "faq" in d
        # if FAQ exists, structure should be question/answer
        if d["faq"]:
            sample = d["faq"][0]
            assert "question" in sample or "q" in sample
            assert "answer" in sample or "a" in sample


# ============ JSON-LD Validator ============
class TestJsonLdValidator:
    def test_scan(self, auth_headers):
        r = requests.get(f"{API}/seo/intelligence/jsonld/scan?limit=10",
                         headers=auth_headers, timeout=30)
        assert r.status_code == 200, r.text
        d = r.json()
        assert "by_severity" in d or "issues" in d or "results" in d


# ============ Trust Score ============
class TestTrustScore:
    def test_event_public_no_auth(self):
        # Get any event slug
        r = requests.get(f"{API}/events?limit=5", timeout=15)
        assert r.status_code == 200
        body = r.json()
        events = body.get("events") if isinstance(body, dict) else body
        if not events:
            pytest.skip("no events")
        slug = events[0]["slug"]
        r2 = requests.get(f"{API}/seo/intelligence/trust-score/event/{slug}", timeout=15)
        assert r2.status_code == 200, r2.text
        d = r2.json()
        for k in ("trust_score", "badge", "color", "sources", "source_count"):
            assert k in d
        assert 0 <= d["trust_score"] <= 100
        assert isinstance(d["sources"], list)

    def test_not_found(self):
        r = requests.get(f"{API}/seo/intelligence/trust-score/event/non-existent-xyz", timeout=15)
        assert r.status_code == 404


# ============ Team Verifier (latest only — run is slow) ============
class TestTeamVerifier:
    def test_latest(self, auth_headers):
        r = requests.get(f"{API}/seo/intelligence/team-verifier/latest",
                         headers=auth_headers, timeout=20)
        # latest may return None or a doc; both acceptable
        assert r.status_code in (200, 404), r.text


# ============ Regression: /api/events case-insensitive league ============
class TestEventsLeagueCaseInsensitive:
    def test_coppa_italia_uppercase(self):
        r = requests.get(f"{API}/events?league=COPPA%20ITALIA&limit=100", timeout=15)
        assert r.status_code == 200, r.text
        body = r.json()
        events = body.get("events") if isinstance(body, dict) else body
        # not asserting count > 0 strictly — DB-dependent — but if count > 0,
        # league name must be case-insensitive match to "coppa italia"
        if events:
            for e in events:
                assert "coppa italia" in (e.get("league") or "").lower(), \
                    f"non-coppa-italia event leaked: {e.get('league')}"

    def test_coppa_italia_titlecase_returns_same(self):
        r1 = requests.get(f"{API}/events?league=COPPA%20ITALIA&limit=100", timeout=15).json()
        r2 = requests.get(f"{API}/events?league=Coppa%20Italia&limit=100", timeout=15).json()
        ev1 = r1.get("events") if isinstance(r1, dict) else r1
        ev2 = r2.get("events") if isinstance(r2, dict) else r2
        assert len(ev1 or []) == len(ev2 or []), "case-insensitive must return same count"
