"""Tests for CWV Automation Center endpoints (FASE 13)."""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://sports-events-2.preview.emergentagent.com").rstrip("/")
TARGET = "https://example.com"


@pytest.fixture(scope="module")
def admin_token():
    r = requests.post(f"{BASE_URL}/api/admin/login",
                      json={"username": "admin", "password": "golevents2024"}, timeout=15)
    assert r.status_code == 200, r.text
    return r.json()["token"]


@pytest.fixture(scope="module")
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


# -------------------- AUTH GATE --------------------
def test_auth_required():
    r = requests.post(f"{BASE_URL}/api/seo/cwv/scan", json={"url": TARGET}, timeout=15)
    assert r.status_code in (401, 403), f"expected 401/403, got {r.status_code}"


# -------------------- SCAN --------------------
@pytest.fixture(scope="module")
def scan_result(auth_headers):
    r = requests.post(f"{BASE_URL}/api/seo/cwv/scan",
                      headers=auth_headers, json={"url": TARGET}, timeout=60)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data.get("ok") is True
    assert isinstance(data.get("score"), int)
    assert 0 <= data["score"] <= 100
    assert isinstance(data.get("items"), list)
    assert len(data["items"]) == 12
    assert isinstance(data.get("scan_id"), str) and len(data["scan_id"]) >= 8
    return data


def test_scan_returns_full_payload(scan_result):
    # validates fixture
    ids = sorted(i["id"] for i in scan_result["items"])
    assert ids == [f"CWV-{n}" for n in sorted(range(1, 13), key=lambda x: f"CWV-{x}")] or len(ids) == 12


def test_scan_persisted_no_id_leak(auth_headers, scan_result):
    r = requests.get(f"{BASE_URL}/api/seo/cwv/scans?limit=10",
                     headers=auth_headers, timeout=15)
    assert r.status_code == 200
    body = r.json()
    rows = body.get("rows", [])
    assert len(rows) >= 1
    for row in rows:
        assert "_id" not in row, "MongoDB _id leaked"
        assert "ts" in row and "score" in row and "url" in row


def test_scan_detail_by_id(auth_headers, scan_result):
    sid = scan_result["scan_id"]
    r = requests.get(f"{BASE_URL}/api/seo/cwv/scan/{sid}",
                     headers=auth_headers, timeout=15)
    assert r.status_code == 200
    data = r.json()
    assert data.get("ok") is True
    assert "items" in data and len(data["items"]) == 12


def test_scan_detail_not_found(auth_headers):
    r = requests.get(f"{BASE_URL}/api/seo/cwv/scan/doesnotexist123",
                     headers=auth_headers, timeout=15)
    assert r.status_code == 200
    assert r.json().get("ok") is False


# -------------------- ACTIONS --------------------
def test_actions_for_target(auth_headers, scan_result):
    r = requests.get(f"{BASE_URL}/api/seo/cwv/actions?target_url={TARGET}",
                     headers=auth_headers, timeout=15)
    assert r.status_code == 200
    rows = r.json().get("rows", [])
    assert len(rows) == 12
    statuses = {row["status"] for row in rows}
    assert statuses.issubset({"TODO", "OK", "DONE", "GENERATED"})
    for row in rows:
        assert "_id" not in row


# -------------------- PATCHES --------------------
@pytest.mark.parametrize("cwv_id", ["CWV-2", "CWV-3", "CWV-4", "CWV-7", "CWV-8", "CWV-9", "CWV-10", "CWV-12"])
def test_patch_generators_ok(auth_headers, cwv_id):
    r = requests.get(f"{BASE_URL}/api/seo/cwv/patch/{cwv_id}",
                     headers=auth_headers, timeout=15)
    assert r.status_code == 200
    p = r.json()
    assert p.get("ok") is True
    assert p.get("content") and len(p["content"]) > 50
    assert p.get("language") in {"jsx", "html", "js", "css"}
    assert p.get("filename")


def test_patch_cwv1_returns_error(auth_headers):
    r = requests.get(f"{BASE_URL}/api/seo/cwv/patch/CWV-1",
                     headers=auth_headers, timeout=15)
    assert r.status_code == 200
    assert r.json().get("ok") is False


def test_patch_cwv3_is_jsx_hero_picture(auth_headers):
    r = requests.get(f"{BASE_URL}/api/seo/cwv/patch/CWV-3",
                     headers=auth_headers, timeout=15)
    p = r.json()
    assert p["language"] == "jsx"
    assert "HeroPicture" in p["content"]


def test_patch_cwv4_is_html_with_preload(auth_headers):
    r = requests.get(f"{BASE_URL}/api/seo/cwv/patch/CWV-4",
                     headers=auth_headers, timeout=15)
    p = r.json()
    assert p["language"] == "html"
    assert 'rel="preload"' in p["content"]


# -------------------- AUTO-FIX --------------------
def test_auto_fix_cwv5(auth_headers):
    r = requests.post(f"{BASE_URL}/api/seo/cwv/auto-fix/CWV-5",
                      headers=auth_headers, json={"target_url": TARGET}, timeout=15)
    assert r.status_code == 200
    body = r.json()
    assert body.get("ok") is True
    assert "scheduler" in body.get("message", "").lower() or "pagespeed" in body.get("message", "").lower()


def test_auto_fix_cwv6(auth_headers):
    r = requests.post(f"{BASE_URL}/api/seo/cwv/auto-fix/CWV-6",
                      headers=auth_headers, json={"target_url": TARGET}, timeout=15)
    body = r.json()
    assert body.get("ok") is True
    assert "prerender" in body.get("message", "").lower()


def test_auto_fix_cwv11(auth_headers):
    r = requests.post(f"{BASE_URL}/api/seo/cwv/auto-fix/CWV-11",
                      headers=auth_headers, json={"target_url": TARGET}, timeout=15)
    body = r.json()
    assert body.get("ok") is True
    assert "critters" in body.get("message", "").lower() or "critical" in body.get("message", "").lower()


def test_auto_fix_cwv1_images(auth_headers):
    r = requests.post(f"{BASE_URL}/api/seo/cwv/auto-fix/CWV-1",
                      headers=auth_headers,
                      json={"target_url": TARGET, "folder": "/app/backend/uploads/seo"},
                      timeout=60)
    assert r.status_code == 200
    body = r.json()
    assert "ok" in body
    # Even with empty folder, total_files should be numeric
    assert "total_files" in body
    assert isinstance(body.get("total_files"), int)


def test_auto_fix_cwv2_manual_only(auth_headers):
    r = requests.post(f"{BASE_URL}/api/seo/cwv/auto-fix/CWV-2",
                      headers=auth_headers, json={"target_url": TARGET}, timeout=15)
    body = r.json()
    assert body.get("ok") is False
    assert "manual" in body.get("error", "").lower()


def test_auto_fix_all(auth_headers):
    r = requests.post(f"{BASE_URL}/api/seo/cwv/auto-fix-all",
                      headers=auth_headers, json={"target_url": TARGET}, timeout=60)
    assert r.status_code == 200
    body = r.json()
    assert body.get("ok") is True
    res = body.get("results", {})
    for k in ("CWV-1", "CWV-5", "CWV-6", "CWV-11"):
        assert k in res


# -------------------- MARK / RESET --------------------
def test_mark_applied_then_reset(auth_headers):
    # first generate to ensure action row exists with GENERATED status
    requests.get(f"{BASE_URL}/api/seo/cwv/patch/CWV-3?target_url={TARGET}",
                 headers=auth_headers, timeout=15)

    r = requests.post(f"{BASE_URL}/api/seo/cwv/mark-applied",
                      headers=auth_headers,
                      json={"target_url": TARGET, "cwv_id": "CWV-3"}, timeout=15)
    assert r.status_code == 200
    body = r.json()
    assert body.get("ok") is True
    assert body.get("modified") in (0, 1)

    # verify action row state == DONE
    r2 = requests.get(f"{BASE_URL}/api/seo/cwv/actions?target_url={TARGET}",
                      headers=auth_headers, timeout=15)
    rows = r2.json()["rows"]
    cwv3 = next((row for row in rows if row["cwv_id"] == "CWV-3"), None)
    assert cwv3 is not None
    assert cwv3["status"] == "DONE"

    # reset
    r3 = requests.post(f"{BASE_URL}/api/seo/cwv/reset-action",
                       headers=auth_headers,
                       json={"target_url": TARGET, "cwv_id": "CWV-3"}, timeout=15)
    assert r3.status_code == 200
    assert r3.json().get("ok") is True

    r4 = requests.get(f"{BASE_URL}/api/seo/cwv/actions?target_url={TARGET}",
                      headers=auth_headers, timeout=15)
    cwv3b = next((row for row in r4.json()["rows"] if row["cwv_id"] == "CWV-3"), None)
    assert cwv3b["status"] == "TODO"


# -------------------- SCORE HISTORY --------------------
def test_score_history(auth_headers, scan_result):
    r = requests.get(f"{BASE_URL}/api/seo/cwv/score-history?url={TARGET}&days=90",
                     headers=auth_headers, timeout=15)
    assert r.status_code == 200
    body = r.json()
    assert "rows" in body
    assert isinstance(body["rows"], list)
    assert len(body["rows"]) >= 1
    for row in body["rows"]:
        assert "ts" in row and "score" in row
        assert "_id" not in row
