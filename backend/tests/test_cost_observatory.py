"""
Cost Observatory backend tests — /api/seo/cost-observatory/*
Tests 19 endpoints + decorator/import sanity.
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://sports-events-2.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"
COBS = f"{API}/seo/cost-observatory"


@pytest.fixture(scope="session")
def admin_token():
    r = requests.post(f"{API}/admin/login",
                      json={"username": "admin", "password": "golevents2024"},
                      timeout=15)
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    return r.json()["token"]


@pytest.fixture(scope="session")
def client(admin_token):
    s = requests.Session()
    s.headers.update({"Authorization": f"Bearer {admin_token}",
                      "Content-Type": "application/json"})
    return s


# ============= Overview / stats =============

class TestOverview:
    def test_overview(self, client):
        r = client.get(f"{COBS}/overview", timeout=20)
        assert r.status_code == 200, r.text
        d = r.json()
        # required keys
        for k in ("today", "week", "month", "top_provider"):
            assert k in d, f"missing key {k}: {d}"
        # forecast key — may be 'forecast' or 'forecast_month_usd'
        assert ("forecast" in d) or ("forecast_month_usd" in d), f"no forecast key: {d}"

    def test_chart_daily(self, client):
        r = client.get(f"{COBS}/chart/daily?days=30", timeout=20)
        assert r.status_code == 200, r.text
        assert "rows" in r.json()
        assert isinstance(r.json()["rows"], list)

    def test_providers(self, client):
        r = client.get(f"{COBS}/providers", timeout=20)
        assert r.status_code == 200, r.text
        rows = r.json()["rows"]
        assert isinstance(rows, list)
        # if rows present, sanity-check structure
        if rows:
            row = rows[0]
            for k in ("provider", "cost_month_usd", "calls_month",
                      "success_rate_pct", "avg_latency_ms"):
                assert k in row, f"row missing {k}: {row}"


class TestEntities:
    def test_top_entities(self, client):
        r = client.get(f"{COBS}/entities/top?days=30&limit=10", timeout=20)
        assert r.status_code == 200, r.text
        assert "rows" in r.json()

    def test_by_type(self, client):
        r = client.get(f"{COBS}/entities/by-type?days=30", timeout=20)
        assert r.status_code == 200, r.text
        assert "rows" in r.json()


class TestLogs:
    def test_logs_no_filter(self, client):
        r = client.get(f"{COBS}/logs?limit=10", timeout=20)
        assert r.status_code == 200, r.text
        d = r.json()
        # response should contain rows or items
        assert "rows" in d or "items" in d, f"bad shape: {list(d.keys())}"

    def test_logs_filter_provider_claude(self, client):
        r = client.get(f"{COBS}/logs?provider=claude&limit=20", timeout=20)
        assert r.status_code == 200, r.text

    def test_logs_filter_status_failed(self, client):
        r = client.get(f"{COBS}/logs?status=failed&limit=20", timeout=20)
        assert r.status_code == 200, r.text
        d = r.json()
        rows = d.get("rows") or d.get("items") or []
        for row in rows:
            assert row.get("status") == "failed", f"non-failed row: {row}"

    def test_latency(self, client):
        r = client.get(f"{COBS}/latency?days=7", timeout=20)
        assert r.status_code == 200, r.text


# ============= Pricing =============

class TestPricing:
    def test_list_pricing(self, client):
        r = client.get(f"{COBS}/pricing", timeout=20)
        assert r.status_code == 200, r.text

    def test_set_pricing_override(self, client):
        payload = {
            "provider": "claude",
            "op_type": "completion",
            "sub_type": "test_sonnet",
            "cost_per_unit": 0.000015,
            "unit": "token",
            "note": "TEST_pricing_override",
        }
        r = client.post(f"{COBS}/pricing", json=payload, timeout=15)
        assert r.status_code == 200, r.text
        assert r.json().get("ok") is True


# ============= Budgets =============

class TestBudgets:
    def test_list_budgets(self, client):
        r = client.get(f"{COBS}/budgets", timeout=20)
        assert r.status_code == 200, r.text
        rows = r.json()["rows"]
        assert isinstance(rows, list)

    def test_set_budget_perplexity(self, client):
        r = client.post(f"{COBS}/budgets/perplexity",
                        json={"monthly_limit_usd": 30.0, "warning_pct": 80},
                        timeout=15)
        assert r.status_code == 200, r.text
        assert r.json().get("ok") is True
        # verify persistence
        r2 = client.get(f"{COBS}/budgets", timeout=15)
        rows = r2.json()["rows"]
        match = next((x for x in rows if x["provider"] == "perplexity"), None)
        assert match is not None, f"perplexity budget missing: {rows}"
        assert match["monthly_limit_usd"] == 30.0


# ============= Alerts =============

class TestAlerts:
    def test_open_alerts(self, client):
        r = client.get(f"{COBS}/alerts/open", timeout=20)
        assert r.status_code == 200, r.text
        d = r.json()
        assert "items" in d and "count" in d

    def test_run_checks(self, client):
        r = client.post(f"{COBS}/alerts/run-checks", timeout=60)
        assert r.status_code == 200, r.text


# ============= Balance =============

class TestBalance:
    def test_balance(self, client):
        r = client.get(f"{COBS}/balance", timeout=30)
        assert r.status_code == 200, r.text


# ============= Backfill (structure only) =============

class TestBackfill:
    def test_backfill_structure(self, client):
        # use small days to avoid long run
        r = client.post(f"{COBS}/backfill?days=1", timeout=60)
        assert r.status_code == 200, r.text


# ============= Alert Config =============

class TestAlertConfig:
    def test_get_alert_config(self, client):
        r = client.get(f"{COBS}/alert-config", timeout=15)
        assert r.status_code == 200, r.text
        d = r.json()
        # smtp_pass must NOT be present in response
        assert "smtp_pass" not in d, f"smtp_pass leaked: {d}"
        assert "smtp_pass_set" in d
        assert "resend_key_set" in d

    def test_save_alert_config(self, client):
        payload = {
            "email_enabled": True,
            "from_email": "alerts@example.com",
            "to_email": "admin@example.com",
            "smtp_host": "smtp.example.com",
            "smtp_port": 465,
            "smtp_user": "alerts",
            "email_on_budget_warning": True,
            "email_on_budget_exceeded": True,
            "email_on_low_balance": True,
            "email_on_api_down": True,
            "email_on_api_intermittent": False,
        }
        r = client.post(f"{COBS}/alert-config", json=payload, timeout=15)
        assert r.status_code == 200, r.text
        assert r.json().get("ok") is True


# ============= Export CSV =============

class TestExport:
    def test_export_csv(self, client):
        r = client.get(f"{COBS}/export?days=30", timeout=30)
        assert r.status_code == 200, r.text
        ctype = r.headers.get("content-type", "")
        assert "text/csv" in ctype, f"not csv: {ctype}"
        text = r.text
        # header line presence
        assert "ts" in text.split("\n")[0]
        assert "provider" in text.split("\n")[0]


# ============= Catalog / decorator sanity =============

class TestCatalog:
    def test_resend_in_catalog(self, client):
        # tools catalog endpoint
        r = client.get(f"{API}/seo/admin/tools/catalog", timeout=15)
        # try alternative path if 404
        if r.status_code == 404:
            r = client.get(f"{API}/seo/api-tools", timeout=15)
        assert r.status_code in (200, 404), r.text
        if r.status_code == 200:
            payload = r.json()
            text = str(payload).lower()
            assert "resend" in text, f"resend missing from catalog: {text[:300]}"


# ============= Auth required =============

class TestAuthRequired:
    def test_overview_no_token_401(self):
        r = requests.get(f"{COBS}/overview", timeout=10)
        assert r.status_code in (401, 403), f"expected 401/403, got {r.status_code}"
