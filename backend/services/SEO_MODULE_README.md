# SEO Automation Module — Portable

Modulo SEO **portatile** per portali di biglietti calcio. Riusabile in qualsiasi progetto FastAPI + React + MongoDB.

## Architettura Dual-Engine

```
DataForSEO (keywords) → Claude 4.5 (master IT copy) → Perplexity (FAQ live) → DeepL (IT→EN/ES) → Gemini 3 Pro (JSON-LD schema) → Validator (truncate + score)
                                                  ↓
                                          Nano Banana 2 (Gemini Image Gen) per Hero banner 1200x630
```

## Backend (file da copiare in nuovo progetto)

### Routes
- `routes/seo_admin.py` — gestione catalog tools + key encrypted
- `routes/seo_targets.py` — list/edit/generate/publish entity SEO
- `routes/seo_tools.py` — Hero Image (Nano Banana), Export Module, Bulk Generate by League

### Services
- `services/seo_keys.py` — encrypted storage chiavi 3rd party (Fernet)
- `services/seo_crypto.py` — Fernet helper
- `services/seo_tools_catalog.py` — catalog 10 tool API (Claude, Gemini, Perplexity, DataForSEO, DeepL, ecc.)
- `services/seo_orchestrator.py` — pipeline state machine async + job queue
- `services/seo_claude.py` — copywriting master IT
- `services/seo_gemini.py` — JSON-LD schema (SportsEvent/Team/Org + AggregateRating + BreadcrumbList + FAQPage + HowTo + Speakable)
- `services/seo_perplexity.py` — FAQ PAA live + GeoCoordinates + sameAs Wikipedia
- `services/seo_deepl.py` — translation IT→EN/ES con glossario tecnico
- `services/seo_dataforseo.py` — keyword research
- `services/seo_validator.py` — max-length + keyword density + score 0-100
- `services/seo_entity_context.py` — DB lookup related entities + breadcrumbs + canonical
- `services/seo_image_gen.py` — Nano Banana 2 (gemini-3.1-flash-image-preview)

### Frontend pages
- `pages/admin/seo/SeoDashboard.jsx`
- `pages/admin/seo/SeoApiTools.jsx`
- `pages/admin/seo/SeoPagesList.jsx`
- `pages/admin/seo/SeoTargetEditor.jsx`
- `pages/admin/seo/SeoBulkRunner.jsx`

### Components condivisi
- `components/SeoContentBlock.jsx` — rendering pubblico contenuto SEO
- `components/SeoSchemaInjector.jsx` — inject JSON-LD nel `<head>`

## Routes API endpoints (prefix `/api/seo`)

### Admin tools
- `GET /api/seo/admin/tools` — catalog
- `POST /api/seo/admin/tools/{tool_id}/key` — save key encrypted

### Targets (events/leagues/teams)
- `GET /api/seo/targets?type=event|league|team` — list paginata
- `GET /api/seo/targets/{type}/{id}` — entity con seo_meta merged
- `POST /api/seo/targets/{type}/{id}/generate` — avvia pipeline async (returns {job_id})
- `GET /api/seo/jobs/{job_id}` — polling status
- `POST /api/seo/targets/{type}/{id}/publish` — applica draft a campi reali
- `POST /api/seo/targets/bulk-generate-league` — batch per intera lega

### Hero image + Export
- `POST /api/seo/hero-image/{type}/{id}` — Nano Banana 2 hero 1200x630
- `GET /api/seo/uploads/{filename}` — serve hero PNG cached
- `GET /api/seo/export?format=json|csv|ndjson` — backup SEO data

## Setup in nuovo progetto

1. **Copia files** sopra in `/backend/routes/`, `/backend/services/`, `/frontend/src/pages/admin/seo/`, `/frontend/src/components/`.

2. **Backend**:
   ```python
   # server.py
   from routes import seo_admin, seo_targets, seo_tools
   app.include_router(seo_admin.router)
   app.include_router(seo_targets.router)
   app.include_router(seo_tools.router)
   ```

3. **Env**:
   ```
   EMERGENT_LLM_KEY=sk-emergent-...   # Universal key Claude/Gemini/Nano Banana
   ```
   API keys per DataForSEO, Perplexity, DeepL si salvano via UI `/admin/seo/api-tools` (cifrate con Fernet in `db.seo_api_keys`).

4. **MongoDB collections** create automaticamente:
   - `seo_api_keys` (encrypted)
   - `seo_jobs` (pipeline queue)
   - `seo_geo_cache`, `seo_entity_links` (Perplexity caches)

5. **Frontend routes**:
   ```jsx
   <Route path="/admin/seo" element={<SeoDashboard />} />
   <Route path="/admin/seo/api-tools" element={<SeoApiTools />} />
   <Route path="/admin/seo/pages" element={<SeoPagesList />} />
   <Route path="/admin/seo/targets/:type/:id" element={<SeoTargetEditor />} />
   <Route path="/admin/seo/bulk" element={<SeoBulkRunner />} />
   ```

6. **Public pages** integrate JSON-LD + content via:
   ```jsx
   <SeoContentBlock data={team} lang={lang} />
   <SeoSchemaInjector schema={team?.seo_meta_schema_jsonld} />
   ```

## Schema entity richiesto (events/teams/leagues)

I campi **richiesti** sull'entity:
- `slug` (string, unique)
- `name` (team/league) o `home_team`+`away_team` (event)
- `league` o `league_slug` (per scope)
- `stadium`, `city`, `country` (per event/team)

I campi SEO (popolati dal modulo):
- `seo_title`, `seo_description`, `seo_h1`, `seo_intro`, `seo_main_content`, `seo_cta` come `{it, en, es}`
- `seo_internal_links` come `{it: [{url, anchor}], en: [...], es: [...]}`
- `seo_image_alt_texts`, `seo_legal_disclosure` come `{it, en, es}`
- `faq_1_q`, `faq_1_a`, ..., `faq_3_q`, `faq_3_a` come `{it, en, es}`
- `seo_meta_schema_jsonld` (graph globale)
- `seo_hero_image_url` (Nano Banana)
- `seo_status` (Draft | Generated | Published)
- `seo_score` (0-100)

## Costi API approssimativi (per 1 entity)
- DataForSEO: $0.001 (cached)
- Claude Sonnet 4.5: $0.04
- Perplexity Sonar: $0.005
- DeepL: gratis fino 500k char/mese
- Gemini Pro: $0.02
- **Totale per entity: ~$0.07** (o gratis se usi solo Universal Key + DeepL Free)

## Schema.org coverage (per pagina)

Il modulo genera un grafo JSON-LD completo con:
- SportsEvent / SportsTeam / SportsOrganization
- AggregateOffer (price range)
- AggregateRating (★ stars in SERP)
- BreadcrumbList
- FAQPage (3 domande PAA)
- HowTo "Come acquistare biglietti" (5 step) — target AI Overviews
- Place + GeoCoordinates + PostalAddress (local pack)
- Speakable (voice search)
- subjectOf + sameAs (Wikipedia entity linking)
- eventStatus dinamico (compliance ticketing)
- Reseller disclosure DDL 145/2018 (italian compliance)

## Multilingua (IT / EN / ES)
- Master in **italiano** generato da Claude
- DeepL traduce automaticamente in EN + ES con glossario tecnico ticketing (Settore Ospiti, Curva Sud, ecc.)
- hreflang gestito a livello globale dal sito host

---

**NOTE**: il modulo Data Tools (`/admin/data-tools/*`) è **separato** e specifico per portali con dati sporchi/legacy. Non è incluso in questo modulo SEO portatile.
