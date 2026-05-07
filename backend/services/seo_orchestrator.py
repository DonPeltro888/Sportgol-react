"""
SEO Pipeline Orchestrator — coordina tutti i provider AI con state machine.

Pipeline:
1. DataForSEO → keyword research (primary + related + volumes)
2. Entity Context → related_entities + breadcrumbs + canonical + geo + sameAs
3. Claude → master IT (meta+h1+intro+main+cta+og+internal_links+image_alt+legal_disclosure)
4. Perplexity → 3 FAQ live PAA (IT)
5. DeepL → traduzione IT→EN/ES (copy + FAQ + alt + anchor)
6. Gemini → JSON-LD packet completo (graph)
7. Validator → max-length truncate + keyword density + score
8. Save → seo_draft + seo_jobs (status terminale)

Ogni step ha try/except: se fallisce, il job continua con dati fallback.
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

from database import db
from services import seo_dataforseo, seo_claude, seo_perplexity, seo_deepl, seo_gemini, seo_validator
from services import seo_entity_context as ctx_helper

logger = logging.getLogger(__name__)

LANGS_NON_IT = ["en", "es"]
TRANSLATABLE_FIELDS = [
    "meta_title", "meta_description", "h1", "intro_text", "main_content",
    "cta_text", "open_graph_title", "open_graph_description",
    "twitter_card_title", "twitter_card_description", "legal_disclosure_text",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def run_pipeline(job_id: str, target_type: str, target_filter: Dict[str, Any], coll_name: str) -> None:
    """
    Esegue la pipeline completa per UN target. Aggiorna db.seo_jobs.{job_id}.
    Salva il draft sull'entity (collection coll_name).
    """
    await _job_set(job_id, {"status": "running", "started_at": _now_iso(), "progress": 0, "step": "init"})

    try:
        doc = await db[coll_name].find_one(target_filter, {"_id": 0})
        if not doc:
            return await _job_fail(job_id, "Entity not found")

        title = doc.get("title") or doc.get("name") or doc.get("slug") or ""
        if target_type == "event" and doc.get("home_team") and doc.get("away_team"):
            title = f"{doc['home_team']} vs {doc['away_team']}"

        # ── Step 1: Keyword Research ─────────────────────────────────────
        await _job_set(job_id, {"step": "keywords", "progress": 10})
        seed = title or doc.get("slug") or ""
        try:
            keywords = await seo_dataforseo.suggest_keywords(seed, lang="it")
        except Exception as e:
            logger.error(f"[job {job_id}] DataForSEO error: {e}")
            keywords = {"primary": f"biglietti {seed}", "related": []}

        # ── Step 2: Entity context (related, breadcrumbs, geo, sameAs) ──
        await _job_set(job_id, {"step": "entity_context", "progress": 20})
        # canonical IT
        canonical_it = ctx_helper.canonical_url(target_type, doc, "it")

        related = []
        breadcrumbs_it = []
        geo = None
        same_as: List[str] = []
        try:
            related = await ctx_helper.fetch_related_entities(target_type, doc, lang="it")
            breadcrumbs_it = await ctx_helper.build_breadcrumbs(target_type, doc, lang="it")
        except Exception as e:
            logger.warning(f"[job {job_id}] entity_context warn: {e}")

        # geo via Perplexity solo per event/team (con stadio)
        stadium = doc.get("stadium") or doc.get("location", "")
        if target_type in ("event", "team") and stadium:
            try:
                geo = await ctx_helper.get_geo_for_stadium(stadium)
            except Exception as e:
                logger.warning(f"[job {job_id}] geo warn: {e}")

        # sameAs (Wikipedia) solo per league/team
        if target_type in ("league", "team"):
            try:
                same_as = await ctx_helper.get_same_as(title, kind=target_type)
            except Exception as e:
                logger.warning(f"[job {job_id}] sameAs warn: {e}")

        # build ctx for Claude/Gemini
        cl_ctx: Dict[str, Any] = dict(doc)
        cl_ctx["title"] = title
        cl_ctx["canonical_url"] = canonical_it
        if geo and geo.get("city"):
            cl_ctx["city"] = geo["city"]
        if geo and geo.get("postal_code"):
            cl_ctx["postal_code"] = geo["postal_code"]

        # ── Step 3: Claude master IT ────────────────────────────────────
        await _job_set(job_id, {"step": "claude_copy_it", "progress": 35})
        master_it: Dict[str, Any] = {}
        try:
            master_it = await seo_claude.generate_master_it(target_type, cl_ctx, keywords, related)
        except Exception as e:
            logger.error(f"[job {job_id}] Claude error: {e}")
        if not master_it:
            master_it = _fallback_master_it(target_type, cl_ctx, keywords)

        # ── Step 4: Perplexity FAQ ──────────────────────────────────────
        await _job_set(job_id, {"step": "perplexity_faq", "progress": 50})
        try:
            faqs_it = await seo_perplexity.fetch_paa_faq(target_type, cl_ctx)
        except Exception as e:
            logger.warning(f"[job {job_id}] Perplexity warn: {e}")
            faqs_it = seo_perplexity._fallback_faq(target_type, cl_ctx)

        master_it["faq_items"] = faqs_it

        # Validator IT (truncate)
        master_it = seo_validator.validate_and_fix(master_it)

        # ── Step 5: DeepL translation IT→EN/ES ──────────────────────────
        await _job_set(job_id, {"step": "deepl_translate", "progress": 65})
        translations = await _translate_block(master_it, faqs_it)

        # Compose seo_draft per 3 lingue
        seo_draft: Dict[str, Any] = {"it": master_it}
        for lang in LANGS_NON_IT:
            seo_draft[lang] = translations.get(lang, {})

        # Score per lingua
        scores = {}
        for lang in ["it"] + LANGS_NON_IT:
            score, warnings = seo_validator.compute_score(seo_draft[lang], keywords.get("primary", ""))
            scores[lang] = {"score": score, "warnings": warnings}

        # ── Step 6: Gemini JSON-LD ──────────────────────────────────────
        await _job_set(job_id, {"step": "gemini_schema", "progress": 80})
        schema_jsonld = {}
        try:
            schema_jsonld = await seo_gemini.build_jsonld(
                target_type, cl_ctx,
                faq_items=faqs_it,
                breadcrumbs=breadcrumbs_it,
                geo=geo,
                same_as=same_as,
            )
        except Exception as e:
            logger.error(f"[job {job_id}] Gemini error: {e}")

        # ── Step 7: Save draft ──────────────────────────────────────────
        await _job_set(job_id, {"step": "saving", "progress": 95})
        avg_score = round(sum(s["score"] for s in scores.values()) / max(1, len(scores)))

        update = {
            "seo_draft": seo_draft,
            "seo_draft_schema_jsonld": schema_jsonld,
            "seo_draft_keywords": keywords,
            "seo_draft_scores": scores,
            "seo_score": avg_score,
            "seo_status": "Generated",
            "seo_generated_at": _now_iso(),
            "seo_generation_method": "claude+gemini+perplexity+dataforseo+deepl",
        }
        await db[coll_name].update_one(target_filter, {"$set": update})

        await _job_set(job_id, {
            "status": "succeeded",
            "step": "done",
            "progress": 100,
            "completed_at": _now_iso(),
            "seo_score": avg_score,
            "scores_per_lang": scores,
        })
        logger.info(f"[job {job_id}] DONE — score {avg_score}")
    except Exception as e:
        logger.exception(f"[job {job_id}] PIPELINE FAIL: {e}")
        await _job_fail(job_id, str(e))


async def _translate_block(master_it: Dict[str, Any], faqs_it: List[Dict[str, str]]) -> Dict[str, Dict[str, Any]]:
    """Traduce master IT + FAQ in EN e ES."""
    out: Dict[str, Dict[str, Any]] = {"en": {}, "es": {}}

    # Build flat list of texts to translate (keeps order)
    base_texts: List[str] = []
    base_keys: List[str] = []
    for k in TRANSLATABLE_FIELDS:
        v = master_it.get(k)
        if isinstance(v, str) and v:
            base_keys.append(k)
            base_texts.append(v)

    # internal_links: anchor text only
    links = master_it.get("internal_links") or []
    link_anchors = [it.get("anchor", "") for it in links if isinstance(it, dict)]

    # image_alt_texts
    alts = master_it.get("image_alt_texts") or []

    # FAQ items q+a
    faq_qs = [f.get("q", "") for f in faqs_it]
    faq_as = [f.get("a", "") for f in faqs_it]

    for lang in LANGS_NON_IT:
        try:
            translated_base = await seo_deepl.translate_batch(base_texts, lang.upper()) if base_texts else []
            translated_anchors = await seo_deepl.translate_batch(link_anchors, lang.upper()) if link_anchors else []
            translated_alts = await seo_deepl.translate_batch(alts, lang.upper()) if alts else []
            translated_q = await seo_deepl.translate_batch(faq_qs, lang.upper()) if faq_qs else []
            translated_a = await seo_deepl.translate_batch(faq_as, lang.upper()) if faq_as else []
        except Exception as e:
            logger.error(f"DeepL batch error ({lang}): {e}")
            translated_base, translated_anchors, translated_alts, translated_q, translated_a = (
                base_texts, link_anchors, alts, faq_qs, faq_as
            )

        block: Dict[str, Any] = {}
        for i, k in enumerate(base_keys):
            if i < len(translated_base):
                block[k] = translated_base[i]

        # Reassemble internal_links (keep URL, replace anchor with translated)
        new_links: List[Dict[str, str]] = []
        for i, it in enumerate(links):
            if isinstance(it, dict) and it.get("url"):
                anchor = translated_anchors[i] if i < len(translated_anchors) else it.get("anchor", "")
                new_links.append({"url": it["url"], "anchor": anchor})
        block["internal_links"] = new_links

        block["image_alt_texts"] = translated_alts

        # FAQ
        new_faqs: List[Dict[str, str]] = []
        for i in range(len(faqs_it)):
            new_faqs.append({
                "q": translated_q[i] if i < len(translated_q) else faqs_it[i].get("q", ""),
                "a": translated_a[i] if i < len(translated_a) else faqs_it[i].get("a", ""),
            })
        block["faq_items"] = new_faqs

        # Truncate
        block = seo_validator.validate_and_fix(block)
        out[lang] = block
    return out


def _fallback_master_it(target_type: str, ctx: Dict[str, Any], keywords: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback minimo se Claude fallisce: produce un draft non-vuoto."""
    title = ctx.get("title") or "?"
    if target_type == "event":
        h, a = ctx.get("home_team", ""), ctx.get("away_team", "")
        title_kw = f"{h} vs {a}" if h and a else title
    else:
        title_kw = title
    return {
        "meta_title": f"Biglietti {title_kw} | Confronta Prezzi e Posti"[:60],
        "meta_description": f"Biglietti ufficiali {title_kw}. Confronta prezzi, settori e disponibilità in tempo reale. Acquisto sicuro garantito."[:160],
        "h1": f"Biglietti {title_kw}",
        "intro_text": f"Acquista i biglietti per {title_kw} su Golevents con garanzia di autenticità. Visualizza la mappa dello stadio, scegli il settore preferito e completa l'ordine in pochi clic. Tutti i biglietti sono verificati e provengono da fornitori di fiducia.",
        "main_content": f"Stai cercando i biglietti per {title_kw}? Su Golevents trovi tutte le offerte disponibili in un'unica piattaforma. Confronta i prezzi tra diversi settori dello stadio: dalle tribune popolari ai posti premium con vista privilegiata.\n\nMappa interattiva dello stadio: scegli il settore in base alla tua esperienza preferita. Curva, distinti, tribuna laterale o tribuna centrale — ogni posto ha la sua atmosfera.\n\nAcquisto sicuro garantito: pagamento protetto SSL, biglietti consegnati via email entro 24h dall'evento, e assicurazione anti-frode inclusa. Supporto clienti 7 giorni su 7.",
        "cta_text": "Confronta i prezzi e prenota subito",
        "open_graph_title": f"Biglietti {title_kw} | Golevents",
        "open_graph_description": f"Biglietti ufficiali {title_kw}. Confronta prezzi e settori. Acquisto sicuro.",
        "twitter_card_title": f"Biglietti {title_kw}",
        "twitter_card_description": f"Confronta prezzi per {title_kw} su Golevents",
        "internal_links": [],
        "image_alt_texts": [f"Biglietti {title_kw}", f"Stadio per {title_kw}"],
        "legal_disclosure_text": "I biglietti sono offerti tramite mercato secondario; i prezzi possono essere superiori al valore nominale (DDL 145/2018).",
    }


# ─── Job state helpers ────────────────────────────────────────────────────

async def _job_set(job_id: str, fields: Dict[str, Any]) -> None:
    await db.seo_jobs.update_one({"_id": job_id}, {"$set": fields}, upsert=True)


async def _job_fail(job_id: str, err: str) -> None:
    await db.seo_jobs.update_one(
        {"_id": job_id},
        {"$set": {"status": "failed", "error": err, "completed_at": _now_iso()}},
        upsert=True,
    )


async def create_job(target_type: str, target_id: str, coll_name: str, target_filter: Dict[str, Any]) -> str:
    """Crea un nuovo job in queue. Restituisce job_id."""
    import uuid
    job_id = str(uuid.uuid4())
    await db.seo_jobs.insert_one({
        "_id": job_id,
        "target_type": target_type,
        "target_id": target_id,
        "coll_name": coll_name,
        "target_filter_repr": str(target_filter),
        "status": "queued",
        "step": "queued",
        "progress": 0,
        "created_at": _now_iso(),
    })
    # Fire-and-forget background task
    asyncio.create_task(run_pipeline(job_id, target_type, target_filter, coll_name))
    return job_id
