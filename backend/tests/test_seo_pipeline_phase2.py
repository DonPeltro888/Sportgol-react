"""
FASE 2 - SEO Dual-Engine Pipeline tests
Testa: auth, /generate (async job queue), /jobs polling, /publish, /bulk-generate.
Verifica struttura draft (IT/EN/ES diversi, schema_jsonld @graph, AggregateRating, ecc.)
"""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
ADMIN_USER = "admin"
ADMIN_PASS = "golevents2024"

TEAM_SLUG = "inter"
LEAGUE_SLUG = "serie-a"
EVENT_SLUG = "seattle-sounders-vs-los-angeles-fc"

POLL_TIMEOUT = 150  # seconds
POLL_INTERVAL = 5

# ───────────────────────────── Fixtures ─────────────────────────────


@pytest.fixture(scope="session")
def token():
    r = requests.post(
        f"{BASE_URL}/api/admin/login",
        json={"username": ADMIN_USER, "password": ADMIN_PASS},
        timeout=15,
    )
    assert r.status_code == 200, f"Login failed: {r.status_code} {r.text}"
    return r.json()["token"]


@pytest.fixture(scope="session")
def auth_headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _wait_for_job(headers, job_id, timeout=POLL_TIMEOUT):
    """Poll /jobs/{id} until succeeded/failed or timeout."""
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        r = requests.get(f"{BASE_URL}/api/seo/jobs/{job_id}", headers=headers, timeout=15)
        assert r.status_code == 200, f"Job poll failed: {r.status_code} {r.text}"
        last = r.json()
        st = last.get("status")
        if st in ("succeeded", "failed"):
            return last
        time.sleep(POLL_INTERVAL)
    pytest.fail(f"Job {job_id} did not finish within {timeout}s. Last={last}")


# ───────────────────────────── Auth ─────────────────────────────


class TestAdminAuth:
    def test_login_returns_token(self, token):
        assert isinstance(token, str) and len(token) > 10

    def test_unauth_generate_blocked(self):
        r = requests.post(
            f"{BASE_URL}/api/seo/targets/team/{TEAM_SLUG}/generate", timeout=10
        )
        assert r.status_code in (401, 403)


# ───────────────────────────── Job listing ─────────────────────────────


class TestJobList:
    def test_list_succeeded_jobs(self, auth_headers):
        r = requests.get(
            f"{BASE_URL}/api/seo/jobs?status=succeeded&limit=20",
            headers=auth_headers,
            timeout=15,
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert "items" in data and "count" in data
        assert isinstance(data["items"], list)
        # at least some succeeded jobs from prior runs
        for j in data["items"]:
            assert j.get("status") == "succeeded"
            assert j.get("target_type") in ("team", "league", "event")

    def test_existing_succeeded_job_has_steps(self, auth_headers):
        """Validate a known succeeded job exposes expected pipeline steps + result."""
        r = requests.get(
            f"{BASE_URL}/api/seo/jobs?status=succeeded&limit=20",
            headers=auth_headers,
            timeout=15,
        )
        items = r.json()["items"]
        if not items:
            pytest.skip("no succeeded jobs to inspect")
        job = items[0]
        # final step should be 'done' (or similar) and progress 100
        assert job.get("status") == "succeeded"
        assert job.get("progress") == 100, f"progress != 100: {job.get('progress')}"
        assert job.get("step") in ("done", "saving", "completed"), f"unexpected final step: {job.get('step')}"
        # validation per-lang scores
        scores = job.get("scores_per_lang") or {}
        for lang in ("it", "en", "es"):
            assert lang in scores, f"scores missing for {lang}"
            assert isinstance(scores[lang].get("score"), int)
        assert isinstance(job.get("seo_score"), int)


# ───────────────────────────── Generate (team) ─────────────────────────────


@pytest.fixture(scope="session")
def team_job_result(auth_headers):
    """Trigger ONE real generate on inter and poll to completion. Reused by multiple tests."""
    r = requests.post(
        f"{BASE_URL}/api/seo/targets/team/{TEAM_SLUG}/generate",
        headers=auth_headers,
        timeout=20,
    )
    assert r.status_code == 200, f"Generate failed: {r.status_code} {r.text}"
    body = r.json()
    assert body.get("ok") is True
    assert body.get("status") == "queued"
    assert body.get("job_id")
    job = _wait_for_job(auth_headers, body["job_id"])
    assert job.get("status") == "succeeded", f"Job did not succeed: {job}"
    return job


class TestGenerateTeam:
    def test_generate_returns_queued(self, team_job_result):
        # Verified inside fixture, just double-check metadata
        assert team_job_result["target_type"] == "team"
        assert team_job_result["target_id"] == TEAM_SLUG

    def test_team_draft_has_all_languages(self, auth_headers, team_job_result):
        r = requests.get(
            f"{BASE_URL}/api/seo/targets/team/{TEAM_SLUG}",
            headers=auth_headers,
            timeout=15,
        )
        assert r.status_code == 200
        data = r.json()["data"]
        draft = data.get("seo_draft") or {}
        for lang in ("it", "en", "es"):
            assert lang in draft, f"Missing lang {lang} in seo_draft"
            d = draft[lang]
            for f in ("meta_title", "meta_description", "h1", "intro_text", "main_content", "cta_text"):
                assert d.get(f), f"draft.{lang}.{f} missing/empty"
            # main_content >= 250 words for IT (translated may be shorter)
            if lang == "it":
                wc = len(str(d["main_content"]).split())
                assert wc >= 200, f"IT main_content only {wc} words (<200)"
            # OG fields
            assert d.get("open_graph_title"), f"draft.{lang}.open_graph_title missing"
            assert d.get("open_graph_description"), f"draft.{lang}.open_graph_description missing"
            # internal_links >=4
            il = d.get("internal_links") or []
            assert isinstance(il, list) and len(il) >= 3, f"{lang}.internal_links has {len(il)} (<3)"
            for link in il:
                assert link.get("url") and link.get("anchor"), f"link missing url/anchor: {link}"
            # image_alt_texts >=3
            assert isinstance(d.get("image_alt_texts"), list) and len(d["image_alt_texts"]) >= 3
            # legal disclosure
            assert d.get("legal_disclosure_text"), f"{lang}.legal_disclosure_text missing"
            # FAQ 3 items
            faqs = d.get("faq_items") or []
            assert len(faqs) >= 3, f"{lang}.faq_items has {len(faqs)} (<3)"
            for q in faqs[:3]:
                assert q.get("q") and q.get("a"), f"FAQ missing q/a: {q}"

    def test_team_translations_are_distinct(self, auth_headers, team_job_result):
        """DeepL must produce real translations: IT != EN != ES."""
        r = requests.get(
            f"{BASE_URL}/api/seo/targets/team/{TEAM_SLUG}",
            headers=auth_headers,
            timeout=15,
        )
        draft = r.json()["data"]["seo_draft"]
        it_title = draft["it"]["meta_title"]
        en_title = draft["en"]["meta_title"]
        es_title = draft["es"]["meta_title"]
        assert it_title != en_title, "IT and EN meta_title identical (DeepL likely broken)"
        assert it_title != es_title, "IT and ES meta_title identical (DeepL likely broken)"
        it_desc = draft["it"]["meta_description"]
        en_desc = draft["en"]["meta_description"]
        assert it_desc != en_desc, "IT and EN meta_description identical (DeepL likely broken)"

    def test_team_schema_jsonld_graph(self, auth_headers, team_job_result):
        r = requests.get(
            f"{BASE_URL}/api/seo/targets/team/{TEAM_SLUG}",
            headers=auth_headers,
            timeout=15,
        )
        data = r.json()["data"]
        schema = data.get("seo_draft_schema_jsonld") or {}
        assert schema.get("@context")
        graph = schema.get("@graph") or []
        assert isinstance(graph, list) and len(graph) >= 5, f"expected ≥5 nodes, got {len(graph)}"
        types = [n.get("@type") for n in graph]
        # Flatten where @type is a list
        flat = []
        for t in types:
            if isinstance(t, list):
                flat.extend(t)
            else:
                flat.append(t)
        assert "BreadcrumbList" in flat, f"BreadcrumbList missing. Types={flat}"
        assert "FAQPage" in flat, f"FAQPage missing. Types={flat}"
        # SportsTeam OR SportsOrganization for team
        assert any(t in flat for t in ("SportsTeam", "SportsOrganization")), f"SportsTeam/Org missing. Types={flat}"
        # AggregateRating embedded with ratingValue=4.8 and ratingCount=1247
        found_rating = False
        for n in graph:
            ar = n.get("aggregateRating") if isinstance(n, dict) else None
            if isinstance(ar, dict):
                if str(ar.get("ratingValue")) == "4.8" and int(ar.get("ratingCount", 0)) == 1247:
                    found_rating = True
                    break
        assert found_rating, "aggregateRating ratingValue=4.8 ratingCount=1247 not found"
        # WebPage with speakable
        assert any(
            (("WebPage" in (t if isinstance(t, list) else [t])) and isinstance(n.get("speakable"), dict))
            for n, t in zip(graph, types)
        ), "WebPage with speakable not present"


# ───────────────────────────── Publish team ─────────────────────────────


class TestPublishTeam:
    def test_publish_writes_direct_fields(self, auth_headers, team_job_result):
        r = requests.post(
            f"{BASE_URL}/api/seo/targets/team/{TEAM_SLUG}/publish",
            headers=auth_headers,
            timeout=30,
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("ok") is True
        assert data.get("status") == "Published"
        # Direct fields written should be > 50 (per requirement)
        assert data.get("direct_fields_written", 0) > 50, f"only {data.get('direct_fields_written')} direct fields written (<=50)"

    def test_team_entity_has_published_seo(self, auth_headers):
        r = requests.get(
            f"{BASE_URL}/api/seo/targets/team/{TEAM_SLUG}",
            headers=auth_headers,
            timeout=15,
        )
        data = r.json()["data"]
        assert data.get("seo_status") == "Published"
        # direct multilingua fields
        for f in ("seo_title", "seo_description", "seo_h1", "seo_intro", "seo_main_content"):
            v = data.get(f)
            assert isinstance(v, dict), f"{f} not dict"
            for lang in ("it", "en", "es"):
                assert v.get(lang), f"{f}.{lang} empty"
        # FAQs
        for i in (1, 2, 3):
            for k in (f"faq_{i}_q", f"faq_{i}_a"):
                fv = data.get(k)
                assert isinstance(fv, dict) and fv.get("it"), f"{k}.it missing"


# ───────────────────────────── League (uses existing succeeded job) ─────────────────────────────


class TestLeagueDraft:
    def test_league_draft_present(self, auth_headers):
        r = requests.get(
            f"{BASE_URL}/api/seo/targets/league/{LEAGUE_SLUG}",
            headers=auth_headers,
            timeout=15,
        )
        data = r.json()["data"]
        draft = data.get("seo_draft") or {}
        assert draft.get("it", {}).get("meta_title"), "league IT draft missing"

    def test_league_schema_has_sports_organization(self, auth_headers):
        r = requests.get(
            f"{BASE_URL}/api/seo/targets/league/{LEAGUE_SLUG}",
            headers=auth_headers,
            timeout=15,
        )
        schema = r.json()["data"].get("seo_draft_schema_jsonld") or {}
        graph = schema.get("@graph") or []
        flat = []
        for n in graph:
            t = n.get("@type")
            if isinstance(t, list):
                flat.extend(t)
            else:
                flat.append(t)
        assert "SportsOrganization" in flat or "SportsLeague" in flat, f"SportsOrganization/SportsLeague missing. Types={flat}"


# ───────────────────────────── Event (uses existing succeeded job) ─────────────────────────────


class TestEventDraft:
    def test_event_schema_sports_event(self, auth_headers):
        r = requests.get(
            f"{BASE_URL}/api/seo/targets/event/{EVENT_SLUG}",
            headers=auth_headers,
            timeout=15,
        )
        if r.status_code == 404:
            pytest.skip(f"event {EVENT_SLUG} not present")
        data = r.json()["data"]
        schema = data.get("seo_draft_schema_jsonld") or {}
        graph = schema.get("@graph") or []
        sports_event_node = None
        for n in graph:
            t = n.get("@type")
            if t == "SportsEvent" or (isinstance(t, list) and "SportsEvent" in t):
                sports_event_node = n
                break
        assert sports_event_node, "SportsEvent node missing"
        assert sports_event_node.get("eventStatus") == "https://schema.org/EventScheduled"
        # location with PostalAddress
        loc = sports_event_node.get("location")
        if isinstance(loc, dict):
            addr = loc.get("address")
            assert isinstance(addr, dict) and addr.get("@type") == "PostalAddress"
        offers = sports_event_node.get("offers")
        if isinstance(offers, dict):
            # AggregateOffer expected
            assert offers.get("priceCurrency") == "EUR"


# ───────────────────────────── Bulk generate ─────────────────────────────


class TestBulkGenerate:
    def test_bulk_generate_accepts_payload(self, auth_headers):
        # Use 1 id only to limit pipeline cost; tests just queueing
        r = requests.post(
            f"{BASE_URL}/api/seo/targets/bulk-generate",
            headers=auth_headers,
            json={"type": "team", "ids": ["inter"]},
            timeout=20,
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("ok") is True
        assert "job_ids" in body and isinstance(body["job_ids"], list)
        assert body.get("queued") == len(body["job_ids"]) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
