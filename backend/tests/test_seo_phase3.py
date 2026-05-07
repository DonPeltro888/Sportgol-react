"""
FASE 3 SEO Admin tests:
- Export Module (JSON/CSV/NDJSON)
- Hero Image generation (Nano Banana 2)
- Bulk Generate by League
- Static file serving for uploads
"""
import os
import io
import csv
import json
import time
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://sports-events-2.preview.emergentagent.com").rstrip("/")
ADMIN_USER = "admin"
ADMIN_PASS = "golevents2024"


@pytest.fixture(scope="session")
def admin_token():
    r = requests.post(f"{BASE_URL}/api/admin/login", json={"username": ADMIN_USER, "password": ADMIN_PASS}, timeout=15)
    assert r.status_code == 200, f"Admin login failed: {r.status_code} {r.text}"
    tok = r.json().get("token")
    assert tok
    return tok


@pytest.fixture(scope="session")
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


# ─── Export Module ─────────────────────────────────────────────────────────
class TestExport:
    def test_export_json_team_published(self, auth_headers):
        r = requests.get(
            f"{BASE_URL}/api/seo/export",
            params={"type": "team", "format": "json", "only_published": "true"},
            headers=auth_headers,
            timeout=30,
        )
        assert r.status_code == 200, r.text
        # Content-Disposition attachment
        cd = r.headers.get("content-disposition", "")
        assert "attachment" in cd.lower()
        data = r.json()
        assert "exported_at" in data
        assert "total" in data
        assert "counts" in data
        assert "items" in data
        assert isinstance(data["items"], list)
        # may be 0 if none published, but counts.team must exist when type=team
        assert "team" in data["counts"]
        # if at least 1 item, validate SEO fields present
        if data["items"]:
            it = data["items"][0]
            assert it.get("_entity_type") == "team"
            # at least slug should be present
            assert it.get("slug")

    def test_export_csv_all_published(self, auth_headers):
        r = requests.get(
            f"{BASE_URL}/api/seo/export",
            params={"type": "all", "format": "csv", "only_published": "true"},
            headers=auth_headers,
            timeout=30,
        )
        assert r.status_code == 200, r.text
        ct = r.headers.get("content-type", "")
        assert "text/csv" in ct
        cd = r.headers.get("content-disposition", "")
        assert "attachment" in cd.lower()
        assert ".csv" in cd
        text = r.text
        # CSV should have header line
        lines = text.splitlines()
        if lines:
            reader = csv.reader(io.StringIO(text))
            header = next(reader, [])
            assert "_entity_type" in header
            assert "slug" in header

    def test_export_ndjson_team(self, auth_headers):
        r = requests.get(
            f"{BASE_URL}/api/seo/export",
            params={"type": "team", "format": "ndjson"},
            headers=auth_headers,
            timeout=30,
        )
        assert r.status_code == 200, r.text
        ct = r.headers.get("content-type", "")
        assert "ndjson" in ct or "json" in ct
        cd = r.headers.get("content-disposition", "")
        assert "attachment" in cd.lower()
        text = r.text.strip()
        if text:
            lines = [l for l in text.split("\n") if l.strip()]
            for line in lines[:5]:
                obj = json.loads(line)
                assert isinstance(obj, dict)
                assert obj.get("_entity_type") == "team"

    def test_export_requires_auth(self):
        r = requests.get(
            f"{BASE_URL}/api/seo/export",
            params={"type": "team", "format": "json"},
            timeout=15,
        )
        assert r.status_code in (401, 403), f"Expected unauth, got {r.status_code}"


# ─── Hero Image (Nano Banana 2) ────────────────────────────────────────────
class TestHeroImage:
    def test_serve_existing_uploads(self):
        """If any PNG exists in uploads/seo, the static endpoint must serve it."""
        upload_dir = "/app/backend/uploads/seo"
        if not os.path.isdir(upload_dir):
            pytest.skip("no uploads dir")
        files = [f for f in os.listdir(upload_dir) if f.endswith(".png")]
        if not files:
            pytest.skip("no existing hero PNGs to verify static serving")
        fn = files[0]
        r = requests.get(f"{BASE_URL}/api/seo/uploads/{fn}", timeout=15)
        assert r.status_code == 200, f"Static serve failed: {r.status_code}"
        assert r.headers.get("content-type", "").startswith("image/png")
        assert len(r.content) > 1000  # at least 1KB

    def test_serve_uploads_404(self):
        r = requests.get(f"{BASE_URL}/api/seo/uploads/nonexistent-xyz-123.png", timeout=10)
        assert r.status_code == 404

    @pytest.mark.slow
    def test_generate_hero_team_inter(self, auth_headers):
        """Generate hero for inter — Nano Banana 2 takes ~15-30s."""
        r = requests.post(
            f"{BASE_URL}/api/seo/hero-image/team/inter",
            headers=auth_headers,
            json={"save_to_entity": True},
            timeout=120,
        )
        assert r.status_code == 200, f"Hero gen failed: {r.status_code} {r.text[:500]}"
        d = r.json()
        assert d.get("status") == "success", d
        assert d.get("filename", "").endswith(".png")
        assert d.get("url", "").startswith("/api/seo/uploads/")
        assert d.get("size_bytes", 0) > 50_000  # at least 50KB
        assert "prompt" in d

        # verify file is now servable
        r2 = requests.get(f"{BASE_URL}{d['url']}", timeout=15)
        assert r2.status_code == 200
        assert r2.headers.get("content-type", "").startswith("image/png")

        # verify entity now has seo_hero_image_url
        r3 = requests.get(f"{BASE_URL}/api/teams/inter", timeout=15)
        assert r3.status_code == 200
        team = r3.json()
        assert team.get("seo_hero_image_url"), "seo_hero_image_url not saved on entity"
        assert team["seo_hero_image_url"].startswith("/api/seo/uploads/")

    def test_hero_invalid_type(self, auth_headers):
        r = requests.post(
            f"{BASE_URL}/api/seo/hero-image/invalidtype/some-id",
            headers=auth_headers,
            timeout=10,
        )
        assert r.status_code == 400

    def test_hero_not_found(self, auth_headers):
        r = requests.post(
            f"{BASE_URL}/api/seo/hero-image/team/nonexistent-team-xyz-9999",
            headers=auth_headers,
            timeout=10,
        )
        assert r.status_code == 404


# ─── Bulk Generate by League ───────────────────────────────────────────────
class TestBulkGenerate:
    def test_bulk_serie_a_team(self, auth_headers):
        r = requests.post(
            f"{BASE_URL}/api/seo/targets/bulk-generate-league",
            headers=auth_headers,
            json={"league_slug": "serie-a", "type": "team", "only_pending": False, "limit": 2},
            timeout=30,
        )
        assert r.status_code == 200, r.text
        d = r.json()
        assert d.get("ok") is True
        assert "queued" in d
        assert "jobs" in d
        assert d.get("league_slug") == "serie-a"
        assert d.get("type") == "team"
        assert isinstance(d["jobs"], list)
        if d["queued"] > 0:
            j = d["jobs"][0]
            assert "job_id" in j
            assert "slug" in j
            assert "label" in j
            # check that the queued job is actually present in /api/seo/jobs
            time.sleep(1)
            jobs_r = requests.get(f"{BASE_URL}/api/seo/jobs?limit=20", headers=auth_headers, timeout=10)
            assert jobs_r.status_code == 200
            job_items = jobs_r.json().get("items", [])
            job_ids = {ji.get("_id") or ji.get("id") for ji in job_items}
            assert j["job_id"] in job_ids, f"Bulk-created job {j['job_id']} not found in /api/seo/jobs"

    def test_bulk_event_type(self, auth_headers):
        r = requests.post(
            f"{BASE_URL}/api/seo/targets/bulk-generate-league",
            headers=auth_headers,
            json={"league_slug": "serie-a", "type": "event", "only_pending": True, "limit": 1},
            timeout=30,
        )
        assert r.status_code == 200, r.text
        d = r.json()
        assert d.get("ok") is True
        assert d.get("type") == "event"

    def test_bulk_invalid_type(self, auth_headers):
        r = requests.post(
            f"{BASE_URL}/api/seo/targets/bulk-generate-league",
            headers=auth_headers,
            json={"league_slug": "serie-a", "type": "league", "only_pending": True, "limit": 1},
            timeout=15,
        )
        assert r.status_code == 400

    def test_bulk_requires_auth(self):
        r = requests.post(
            f"{BASE_URL}/api/seo/targets/bulk-generate-league",
            json={"league_slug": "serie-a", "type": "team"},
            timeout=15,
        )
        assert r.status_code in (401, 403)


# ─── Verify entity API exposes seo_hero_image_url ─────────────────────────
class TestEntitySeoHeroField:
    def test_team_api_exposes_hero_url(self):
        r = requests.get(f"{BASE_URL}/api/teams/inter", timeout=15)
        assert r.status_code == 200
        team = r.json()
        # field should be present (might be None or a URL)
        assert "seo_hero_image_url" in team

    def test_league_api_exposes_hero_url(self):
        r = requests.get(f"{BASE_URL}/api/leagues/serie-a", timeout=15)
        assert r.status_code == 200
        league = r.json()
        assert "seo_hero_image_url" in league
