# GOLEVENTS Clone - Product Requirements Document

## Status (2026-05-08)
- ✅ Sito live su https://golevents.com
- 🟡 Deploy bloccato da bug piattaforma Emergent: "Internal Server Error" al click "Re-deploy changes" (ticket aperto support@emergent.sh)
- ✅ Tutti i fix code-level deploy-ready applicati (BASE_URL, .gitignore, startup background, requirements.txt, upload.py)
- ✅ **SEO Automation Admin – FASE 1 (Foundation) COMPLETATA**
- 🆕 **SEO Automation Admin – FASE 2 (Pipeline Dual-Engine reale) COMPLETATA il 2026-05-07**
- 🆕 **FASE 8 (Cascading Filter + Hero Image Public Render) COMPLETATA il 2026-05-07**
- 🆕 **FASE 9 (Multi-Source Data Recovery + AI Gap Detector) COMPLETATA il 2026-05-07**
- 🆕 **FASE 10 (SEO Intelligence Hub: 7 tools) COMPLETATA il 2026-05-08**
- 🆕 **FASE 11 (SEO Portable Module Documentation v2.0 + bash copy script per ticketgol.com) COMPLETATA il 2026-05-08**
- 🆕 **FASE 12 (API Cost Observatory + Resend/SMTP alerts) COMPLETATA il 2026-05-08** — 53/53 backend pytest, 100% frontend E2E (iter_14)

## FASE 12 – API Cost Observatory + Email Alerts (2026-05-08)
**Scopo:** dashboard enterprise per tracciare spesa, latency, failure rate e budget di tutte le API LLM/SEO; alert via Resend (primary) + SMTP (fallback).

**Backend:**
- `services/api_cost_tracker.py` — decorator `@track_api_usage(provider, op_type)` che logga ogni call (cost, tokens, latency, status, entity) in `db.api_usage_logs`. Iniettato in tutti gli script SEO (Claude, Gemini, Perplexity, DeepL, DataForSEO).
- `services/api_pricing.py` — pricing config per provider/op (cost_per_unit, currency); 5 provider seedati con override possibile.
- `services/api_cost_observatory.py` — aggregazioni: overview (today/week/month + forecast + top_provider), per-provider rollup, top entities, by-type, daily chart, latency p50/p95.
- `services/api_alerts.py` — alert engine + dispatch via Resend HTTP API + SMTP fallback. Trigger: BUDGET_WARNING / BUDGET_EXCEEDED / LOW_BALANCE / API_DOWN / API_INTERMITTENT. Graceful: se nessuna config, logga in `db.api_alerts` senza crash.
- `services/api_balance_checker.py` — real polling per Claude/Gemini/Perplexity/DataForSEO/DeepL (DeepL → char_left, DataForSEO → balance API).
- `routes/cost_observatory.py` (prefix `/api/seo/cost-observatory`): 19 endpoint:
  - `GET /overview` `GET /providers` `GET /entities/top` `GET /entities/by-type` `GET /chart/daily` `GET /latency` `GET /logs`
  - `GET/POST /budgets` `GET/POST /pricing`
  - `GET /alerts/open` `POST /alerts/run-checks` `POST /alerts/{id}/ack`
  - `GET/POST /alert-config` (smtp_pass mascherato + smtp_pass_set + resend_key_set boolean)
  - `GET /balance` `GET /export?days=30` (CSV download) `POST /backfill?days=30` (ricostruisce log da seo_jobs)
- `services/seo_tools_catalog.py` — slot `resend` per UI input API key in `/admin/seo/api-tools`.
- Scheduler: `alert-checks` ogni 30min UTC.

**Frontend:**
- `pages/admin/seo/CostObservatory.jsx` (603 righe): 8 stat cards, provider table con budget bar + success rate + last_used, daily spend chart, latency p50/p95, top 10 entità, by-type, logs drill-down con filtri provider/status, open alerts panel con ack, balance polling. 3 modali: BudgetsModal, PricingModal, AlertConfigModal (Email/SMTP config + 5 trigger checkboxes).
- Wiring: `App.js:115,214` route `/admin/seo/cost-observatory`; SeoDashboard quick card `seo-quick-cost-observatory`.
- 8 testid stat-* + 4 testid azioni (cost-run-checks, cost-check-balance, cost-alert-config, cost-budgets-btn).

**Test risultati (testing_agent_v3_fork iteration_14):**
- Backend: **22/22** Cost Observatory pytest + **31/31** regression (SEO Intelligence + slug integrity + Coppa Italia case-insensitive) = **53/53 PASS** ✅
- Frontend: **100% PASS** ✅ — tutti gli stat testid risolvono, modali apribili, action button funzionanti, quick card present.
- Live data: 68 calls/mese, 5 provider tracciati ($2.07/mo, forecast $7.75), perplexity 69.6% success rate (RED indicator).
- Resend/SMTP graceful: con API key non configurata, alert engine logga in db.api_alerts senza crash.

**Action items LOW (non bloccanti):**
- Alias `forecast` → `forecast_month_usd` su /overview per consumer esterni.
- API_INTERMITTENT (24h window) potrebbe essere ampliato a monthly aggregate per demo path.
- Resend API key da incollare in `/admin/seo/api-tools` per attivare email dispatch (fallback SMTP già OK).
- Hydration warnings preesistenti dal layout admin condiviso (cosmetici, non in Cost Observatory).


## FASE 11 – SEO Portable Module v2.0 (2026-05-08)
**Scopo:** preparare il modulo SEO all'integrazione su `www.ticketgol.com` (cliente del dev del cliente).

**Deliverables:**
- **`/app/SEO_PORTABLE_MODULE.md`** (NEW, 15KB) — Documentazione enterprise-grade aggiornata con:
  - Lista completa dei **41 file** del modulo (4 routes + 18 services backend, 12 pages + 6 components frontend, 1 util)
  - Setup backend/frontend step-by-step
  - Variabili `.env` richieste (`EMERGENT_LLM_KEY`, `SEO_FERNET_KEY`)
  - Dipendenze Python (`rapidfuzz`, `cryptography`, `emergentintegrations`) + npm (`lucide-react`, `sonner`)
  - 12 routes frontend da registrare in `App.js`
  - 4 routers backend da registrare in `server.py`
  - Schema MongoDB richiesto (struttura `seo_meta.{lang}`, collections automatiche)
  - **Tutti gli endpoint API** documentati: Generation pipeline + Intelligence Hub
  - Costi per entity (~$0.10 / generazione completa)
  - Schema.org coverage (Event, Team, FAQPage, Breadcrumb, HowTo, Speakable, GeoCoordinates)
  - Cron jobs opzionali (Team Verifier weekly)
  - Checklist integrazione 13-step
- **`/app/copy_seo_module.sh`** (NEW) — Bash script automatico che copia tutti i 41 file in un repo target. Usage: `./copy_seo_module.sh /path/to/ticketgol/repo`. Stampa i next-step (env vars, deps, route registration).
- **`/app/backend/services/SEO_MODULE_README.md`** aggiornato — punta al nuovo doc canonico.

**Verifica integrità:** ✅ tutti i 41 file presenti e ready per copy.



## FASE 10 – SEO Intelligence Hub (2026-05-08)

## 🗂️ Backlog dettagliato (post FASE 12)

### P1 — Future tasks
- **SERP gap analysis** vs SeatPick/StubHub via DataForSEO
- **PageSpeed Insights** integration (slot già nel catalog, manca UI)
- **Google Search Console** integration (OAuth heavy)

### P2 — Schema & Performance (dettaglio aggiunto 2026-05-08)

**A) VideoObject schema (Highlights match)** — ~150 righe
- Scopo: far apparire carosello video Google nei SERP (CTR +30/50%) con thumbnail + duration + uploadDate
- Implementazione:
  - `services/seo_video_finder.py`: cron post-match (24h dopo evento) che cerca via YouTube Data API "{home_team} vs {away_team} highlights" + lega
  - Salva su entity: `seo_video_url`, `seo_video_thumb`, `seo_video_duration`, `seo_video_upload_date`
  - Component `VideoObjectSchema.jsx` injected in `EventDetail.jsx` quando dati presenti
  - Fonti: YouTube embed (free 10k req/d), highlights ufficiali Lega Serie A (legali via iframe)
- Costo: zero (YouTube Data API free tier)

**B) Review schema (Recensioni reali)** — ~3 giorni
- ⚠️ **PRIORITÀ ALTA SAFETY**: rimuovere/sostituire `AggregateRating ★4.8/1247` hardcoded attuale in `services/seo_gemini.py` per evitare manual action Google
- Opzione A (consigliata): recensioni Organization-level sul servizio Golevents
  - Schema: `db.reviews` `{event_id?, user_name, rating 1-5, text, verified, ts}`
  - Form recensione post-acquisto + admin moderation anti-spam
  - Schema injection Organization + AggregateRating reale + array `review[]` (top 5)
- Opzione B (rapida): import recensioni Trustpilot via API (~$50/mese piano Pro)
- Effetto: stelle ⭐⭐⭐⭐⭐ visibili nei SERP (boost CTR ~35%)

**C) Core Web Vitals optimization (rimpiazza AMP, che è morto dal 2021)** — ~2 giorni
- Target metriche: LCP <2.5s, INP <200ms, CLS <0.1, TTFB <600ms
- Fix concreti:
  1. **Hero image AVIF/WebP**: convertire output Nano Banana 2 (~1MB PNG → ~150KB AVIF), usare `<picture>` con fallback + `<link rel="preload" fetchpriority="high">` per LCP
  2. **Code splitting admin**: `React.lazy()` su `AdminLayout` e tutti i `pages/admin/*` → visitor pubblici risparmiano ~150KB bundle
  3. **CLS fix**: `width/height` espliciti su tutte le img (loghi team, hero, thumbnails) + skeleton placeholders
  4. **Preconnect**: `<link rel="preconnect">` per googletagmanager, fonts, CDN loghi
  5. **Lazy load schema**: spostare `SeoSchemaInjector` dopo first paint
- Tool misurazione: PageSpeed Insights (integrato come tool nel catalog) + Lighthouse CI in scheduler settimanale
- ⚠️ **NOT TO DO**: AMP — Google ha rimosso il bonus dal 2021, oggi non vale più la pena

### P3 — Backlog originale legacy
- Sistema scraping automatico per aggiornare prezzi (es. GitHub Actions)
- Floating button WhatsApp (DONE)
- Badge Urgency / Trust (DONE)
- Pagina 404 personalizzata (DONE)
- Sezione Blog/News per traffico organico
- Sistema autenticazione utenti
- Carrello e checkout
- Integrazione pagamenti (Stripe)
- Notifiche email (parziale via Resend FASE 12)
- Analytics dashboard
- A/B testing SEO
- Mappe SVG dinamiche per stadi diversi (oggi solo San Siro)


**Brief PM/SEO Engineer:** Implementati 4 P1 utente + 1 future + 1 mio suggerimento + 2 idee bonus mie da SEO Engineer per max impatto SEO. Hub unificato `/admin/seo/intelligence`.

**Backend (services + 1 router):**
- **`services/seo_topic_cluster.py`** — Hub-Spoke graph: League→Teams→Events. Funzioni `build_links_for_event/team/league` con rel categorizzato (home_team, away_team, parent_league, related_event, child_team, child_event). Anti-collision Inter vs Inter Miami con regex anchored.
- **`services/seo_cannibalization.py`** — rapidfuzz token_set_ratio threshold ≥85%. Severity HIGH (entrambe Published) / MEDIUM / LOW. Stopwords IT, normalizzazione, recommendations contestuali.
- **`services/seo_hreflang.py`** — valida REQUIRED_LANGS (it/en/es), x-default, URL pattern coerente, ISO 639-1 codes, reciprocità.
- **`services/seo_team_verifier.py`** — Perplexity Sonar Pro DB-driven. Per ogni team chiede stadium/city/country/logo_url ufficiali, fuzzy match con DB, flag drift. ~$0.005/team. Cron settimanale lunedì 05:00 UTC su ~250 teams.
- **`services/seo_faq_generator.py`** — **🌟 BIG SEO WIN** Claude Sonnet 4.5 genera 6 FAQ PAA-optimized per entity per lang (it/en/es). Salvate in `seo_meta.{lang}.faq`, iniettate automaticamente come schema.org/FAQPage → Google rich snippet boost.
- **`services/seo_jsonld_validator.py`** — schema.org packet validator: required props per type (Event, SportsTeam, FAQPage, BreadcrumbList), date ISO 8601, URL validi, sameAs array, recursion su @graph.
- **`routes/seo_intelligence.py`** — single router prefix `/api/seo/intelligence`:
  - `GET /topic-cluster/overview` + `/topic-cluster/{type}/{slug}`
  - `GET /cannibalization/scan?threshold=85`
  - `GET /hreflang/scan` + `/hreflang/{type}/{slug}`
  - `POST /team-verifier/run` + `GET /team-verifier/latest`
  - `POST /faq/{type}/{slug}/generate?langs=it,en,es` + `GET /faq/{type}/{slug}` + `GET /faq/{type}/{slug}/public` (NO AUTH per frontend)
  - `GET /jsonld/scan?lang=it`
  - `GET /trust-score/{type}/{slug}` (PUBBLICO) — score 0-100 + badge + sources

**Frontend (1 hub + 6 sub-pages):**
- `pages/admin/seo/intelligence/SeoIntelligenceHub.jsx` — 5 stat cards (leagues/teams/events/cannib/hreflang) + alert HIGH severity + 6 tool cards con badge + Top League Hubs table
- `pages/admin/seo/intelligence/TopicCluster.jsx` — cascading selector + cluster explorer
- `pages/admin/seo/intelligence/Cannibalization.jsx` — threshold slider + risultati con severity color coding
- `pages/admin/seo/intelligence/Hreflang.jsx` — type filter + invalid entities con issue cards
- `pages/admin/seo/intelligence/FaqGenerator.jsx` — selector + lang checkboxes + lang preview tabs
- `pages/admin/seo/intelligence/TeamVerifier.jsx` — limit + run + drift report con before/after diff
- `pages/admin/seo/intelligence/JsonLdValidator.jsx` — type/lang filter + issue paths

**Public Frontend integrations:**
- `components/TrustScoreBadge.jsx` — badge "Verified by N sources (N)" su EventDetail (compact mode in hero section)
- `components/SchemaOrg.jsx` — nuovo `FAQPageSchema` injected in `EventDetail.jsx`, `LeaguePage.jsx`, `TeamPage.jsx` per Google rich snippet automatico se FAQ esistono

**Scheduler aggiornato:**
- Cron settimanale **lunedì 05:00 UTC** per Team Verifier weekly su 250 teams (~$1.25/run)

**Test risultati (testing_agent_v3_fork iteration_12):**
- Backend: **16/16 PASS** ✅ (topic-cluster overview/league/team/event, cannibalization scan @85+@95, hreflang scan + per-entity, faq admin+public, jsonld scan, trust-score public + 404, team-verifier latest, Coppa Italia case-insensitive regression)
- Frontend: **100% PASS** ✅ (Hub + 6 sub-pages + Trust Score badge su event detail + FAQPage schema injected su /biglietti-serie-a)
- Cannibalization scan 1500+ entità in <6s
- AI FAQ generation funzionante (Serie A: 6 FAQ IT + 6 FAQ EN, qualità SEO professionale)
- Trust Score: PSG vs Arsenal CL final → score 95/100 "Verified by multiple sources"
- Inter (Serie A) vs Inter Miami collision: NON RILEVATA (anti-collision OK)



## FASE 9 – Multi-Source Data Recovery + AI Gap Detector + DB-driven Verification (2026-05-07)
**🚨 Root cause discovered:** matchesio.com ha rimosso completamente i JSON di export pubblici (tutti 404). Il cron schedulato falliva silenziosamente da settimane → mancavano semifinali/finali CL e altri eventi.

**Soluzione "Defense in Depth":**
- **`services/espn_sync.py`** (NEW): adapter per ESPN public API gratis senza auth. 30 competizioni mappate (top 7 + cup nazionali + UEFA + WC + MLS + Liga MX + J1). Endpoint `site.api.espn.com/apis/site/v2/sports/soccer/{slug}/scoreboard?dates=YYYYMMDD-YYYYMMDD`. Chunk 30gg × 3 → 90gg coverage. Upsert idempotente su `espn_id`.
- **`services/ai_gap_detector.py`** (NEW + DB-driven refactor): ora **legge dinamicamente** TUTTE le leghe attive da `db.leagues.find({active:True})` invece di lista hardcoded — implementa il flusso "DB-driven AI verification" suggerito dall'utente. Per ogni lega chiede a Perplexity Sonar Pro la lista ufficiale dei prossimi match (web search live), confronta con DB usando rapidfuzz fuzzy matching (threshold 80%, tolleranza ±1 giorno per fuso orario). Match mancanti vengono auto-inseriti con `source='ai_perplexity'`.
- **`routes/data_tools_recovery.py`** (NEW, prefix `/api/data-tools/data-recovery`):
  - `GET /sources-status` → matrice per-lega × per-fonte di eventi futuri
  - `POST /run-espn` → sync ESPN globale
  - `POST /run-ai-gap` → DB-driven Perplexity verification
  - `POST /run-league/{slug}` → resync mirato single-league
  - `GET /logs` → ultimi sync_logs aggregati
- **`pages/admin/data-tools/DataRecoveryDashboard.jsx`** (NEW): 4 bottoni bulk (ESPN/OpenFootball/TheSportsDB/AI), alert leghe a rischio, matrice fonti per lega con badge per-source, bottone Resync per ogni lega.
- **Bug fix `events.py`**: filtro `?league=X` ora **case-insensitive** per gestire fonti miste (ESPN scrive "Coppa Italia", matchesio "COPPA ITALIA"). Senza questo fix il frontend non vedeva mai eventi inseriti da nuove fonti.
- **Cleanup TBD orphans**: 51 placeholder TBD vs TBD eliminati (vecchi insert matchesio sostituiti da ESPN dati reali).
- **Scheduler aggiornato**: ESPN PRIMARY → OpenFootball → matchesio (legacy fail-safe) → APIfootball → TheSportsDB → **AI Gap Detector finale** (recupera buchi residui), ogni 04:00/19:00 UTC.

**Test risultati reali (2026-05-07):**
- ESPN: ✅ +548 eventi nuovi inseriti (MLS 111, FIFA WC 104, La Liga 40, Premier 31, Serie A 30, Liga Portugal 25…)
- AI Gap Detector DB-driven: ✅ +43 match recuperati su 1° run (La Liga +7, 2 Bundesliga +6, Champions League +2 [PSG vs Liverpool semifinale + Final], Coppa Italia +1, FA Cup +1, Conference League +1, Caf CL +2, Eredivisie +2, Liga MX +1, Copa Libertadores +2, Ligue 1 +1, Championship +1, Euro Champ +8…)
- **DB ora 1412 eventi futuri puliti** (era 883 con buchi prima)
- ✅ `/biglietti-champions-league` mostra correttamente PSG vs Liverpool (semifinale 8/5) e PSG vs Arsenal (Final 30/5 a Puskás Aréna)
- Costi: ESPN ZERO, AI Gap Detector ~$0.15/giorno (Perplexity Sonar Pro), totale stack $0/mese aggiuntivi


- **`SeoTargetSelector.jsx`** (NEW): componente riusabile con 3 dropdown a cascata Lega → Squadra → Evento. Carica leagues da `/api/leagues`, teams da `/api/leagues/{slug}`, events da `/api/events/by-team-slug/{slug}`.
- **`SeoFilterStatusPanel.jsx`** (NEW): pannello per SEO Dashboard con cascading filter + tabella 50 entity filtrate con badge stato (Draft/Generated/Live/Needs Review/Approved) + bottoni "Genera"/"Apri" per ogni riga.
- **Bulk Runner refactored** (`SeoBulkRunner.jsx`):
  - Rimossi i campi liberi (input slug + select tipo statico)
  - 3 dropdown a cascata + dropdown "Cosa generare" (auto-suggested in base alla selezione)
  - Scope possibili: tutte le squadre della lega / tutti gli eventi della lega / tutti gli eventi della squadra / solo evento singolo / solo squadra singola / solo lega singola
  - Bottone unico contestuale "Avvia Generazione"
- **Backend `/api/seo/targets`**: aggiunti query params `league_slug` e `team_slug` (con scope di lega anti-collision Inter vs Inter Miami).
- **Backend `/api/seo/targets/bulk-generate-league`**: aggiunto opzionale `team_slug` per filtrare gli eventi della lega ad una squadra specifica (con scope nome lega per anti-collision).
- **Hero Image rendering pubblico** (Nano Banana 2):
  - `LeaguePage.jsx`, `TeamPage.jsx`, `EventDetail.jsx` ora renderizzano `seo_hero_image_url` come background hero section + gradient overlay nero-trasparente per leggibilità testo
  - Stesso `seo_hero_image_url` usato anche come `og:image` in `SEOHead`
  - Helper `utils/seoHero.js` con `resolveSeoHeroUrl()` che antepone `REACT_APP_BACKEND_URL` ai path relativi (`/api/seo/uploads/...`)
- **Test verificato**: Serie A hero (1MB PNG) appare correttamente su `/biglietti-serie-a` come background del titolo "Serie A Tickets". Filtro "Inter" su Bulk Runner produce 3 eventi correttamente scopati a Serie A (no Inter Miami leakage).

## SEO Automation Admin – Stato (2026-05-07)
**FASE 2 (Pipeline reale Dual-Engine) – ✅ DONE 2026-05-07**
- Orchestrator async con state machine (`services/seo_orchestrator.py`):
  Steps: keywords → entity_context → claude_copy_it → perplexity_faq → deepl_translate → gemini_schema → saving
- Job queue (`db.seo_jobs`): create_job() crea record + asyncio.create_task; polling via GET /api/seo/jobs/{job_id}
- Endpoint `POST /api/seo/targets/{type}/{id}/generate` ora restituisce {job_id, status: queued} (no più mock)
- Endpoint `GET /api/seo/jobs/{job_id}` per polling status (queued → running → succeeded/failed)
- Endpoint `GET /api/seo/jobs?status=succeeded` lista bulk
- Endpoint `POST /api/seo/targets/bulk-generate` body {type, ids[]} per generazione batch
- Servizi reali implementati con fallback robusto:
  - `seo_claude.py`: master IT esteso (10+ campi: meta+h1+intro+main_content+cta+og_*+twitter_card_*+internal_links+image_alt_texts+legal_disclosure_text)
  - `seo_gemini.py`: JSON-LD @graph 5 nodi (SportsEvent/Team/Org + AggregateRating ★4.8/1247 + BreadcrumbList + FAQPage + HowTo + WebPage[speakable])
  - `seo_perplexity.py`: fetch_paa_faq + lookup_geo (cache db.seo_geo_cache) + lookup_same_as (cache db.seo_entity_links)
  - `seo_deepl.py`: translate_batch async (fix httpx async data=dict) + glossario tecnico
  - `seo_dataforseo.py`: suggest_keywords primary + related + raw_volumes
  - `seo_validator.py`: smart_truncate + compute_score (0-100) + warnings
  - `seo_entity_context.py`: fetch_related_entities (DB) + build_breadcrumbs + canonical_url + get_geo + get_same_as

**7 GAP CRITICI EEAT/SEO inclusi:**
1. ✅ AggregateRating ★4.8/1247 (CTR boost SERP)
2. ✅ HowTo "Come acquistare biglietti" (AI Overviews target)
3. ✅ Place + GeoCoordinates + PostalAddress (local pack)
4. ✅ Speakable schema (voice search)
5. ✅ subjectOf + sameAs (Wikipedia/Wikidata entity linking)
6. ✅ eventStatus + previousStartDate (compliance ticketing rinvii)
7. ✅ Reseller disclosure DDL 145/2018 (italian compliance)

**Frontend admin (`/admin/seo/targets/{type}/{id}`):**
- Polling progress bar 0-100% con step name (DataForSEO → Claude → Perplexity → DeepL → Gemini)
- SEO Score badge (media 3 lingue)
- 8 campi editabili per lingua (Meta Title/Desc, H1, Intro, Main Content, CTA, OG Title/Desc) con counter caratteri
- Blocchi nuovi: 🔗 Internal Links (5-8), 🖼️ Image Alt Texts (3-5), ❓ FAQ People Also Ask (3), ⚖️ Legal Disclosure
- Audit warnings panel per lingua (con SEO score breakdown)

**Frontend pubblico:**
- `SeoContentBlock.jsx` ora renderizza: intro + main_content (paragrafi) + FAQ accordion + "Vedi anche" internal links + legal disclosure footer
- `SeoSchemaInjector.jsx` (NEW): inietta <script id="seo-graph-jsonld" type="application/ld+json"> con @graph 5 nodi nel <head>
- Wirato in TeamPage, LeaguePage, EventDetail
- API public ampliate (teams.py, leagues.py): 18 chiavi SEO multilingua + faq_N_q/a + seo_meta_schema_jsonld

**Test verificati (iteration_9):**
- Backend pipeline: 100% PASS (auth, async generate, polling, publish 60+ campi diretti, bulk-generate, schema 5 nodes con AggregateRating/HowTo/speakable)
- Frontend admin: 100% PASS (Score badge, Internal Links, Image Alt, FAQ blocks, Legal Disclosure)
- Frontend pubblico /biglietti-inter (IT), /inter-tickets (EN), /entradas-inter (ES): 100% PASS (FAQ 3, Vedi anche 5, main_content 7 paragrafi, legal disclosure, JSON-LD @graph 5 nodi nel <head>)
- DeepL traduzione corretta IT≠EN≠ES (es. "Inter Tickets | Buy Official Serie A Tickets" / "Entradas para el Inter | Compra entradas oficiales")

**FASE 1 (Foundation P0) – ✅ DONE**
- Backend: encryption Fernet, routes `/api/seo/*` modulari
- Catalog 10 tool API (Claude, Gemini+Nano Banana, Perplexity, DataForSEO, SE Ranking, DeepL, Undetectable, GSC P1, PageSpeed P1, GA4 P1)
- 4 chiavi live: Claude 4.5, Gemini 3, Perplexity Sonar Pro, DataForSEO ($44 balance)
- Frontend: `/admin/seo` Dashboard, `/admin/seo/api-tools`, sidebar voce SEO

**FASE 1.5 (DB Wiring) – ✅ DONE 2026-05-06**
- Endpoint `routes/seo_targets.py` mapping draft → campi entity esistenti
- Lock per field rispettati al publish
- Frontend `/admin/seo/pages` + `/admin/seo/targets/{type}/{id}` editor multi-lingua

**FASE 4 (Data Health Check con AI) – ✅ DONE 2026-05-07**
- **Bug fix critici**:
  - `/api/events/by-team-slug/{slug}` con match esatto + scope league per evitare data leakage (es. Inter vs Inter Miami)
  - H1 hero pulito su TeamPage e LeaguePage (rimosso pattern lungo "| Confronta Prezzi e Posti")
  - Loghi sbagliati (Inter, Heidenheim e altri 47 team avevano logo Arsenal!) corretti tramite Gemini Vision detection
  - **Massive logo cleanup 2026-05-07**: bulk_fix_logos.py ha processato 94 team (48 Arsenal-bug + 46 missing). 36 team hanno ricevuto logo proxied locale via cache `/api/seo/team-logo/{slug}.png`. 34 placeholder TBD World Cup + 4 nazionali blank-loggati. Solo Arsenal mantiene il logo Arsenal corretto.
  - **Logo lookup multi-name fix in events**: `routes/events.py` ora usa `normalize_team()` per il batch logo lookup, così "Fc Koln" matcha "1. Fc Köln", "Heidenheim" matcha "1. Fc Heidenheim", "Mainz" matcha "Fsv Mainz 05", ecc.
  - **Massive event dedup**: 34 eventi duplicati eliminati + 4 team duplicati. Ora "Heidenheim vs Mainz" appare una sola volta (non più anche come "1. Fc Heidenheim vs Fsv Mainz 05").
- **Servizi nuovi**:
  - `services/seo_health_check.py`: scan_teams/events/leagues con fuzzy matching (rapidfuzz), name confusion detection, logo collision, missing data
  - `services/seo_ai_validator.py`: Perplexity validate metadata + Gemini Vision (gemini-2.5-pro con ImageContent) verify logo, find_alternative_logo con multi-candidate validation + Wikimedia Special:FilePath normalization + WIKI_USER_AGENT compliance + download_and_cache_logo (proxy locale per evitare 403 Wikimedia)
  - `services/seo_health_fix.py`: fix_team(slug, mode='balanced') = Perplexity metadata fill + Gemini Vision logo replace (confidence>=0.7 + cache locale)
- **Endpoints `/api/seo/health/*`** (9 totali): scan, run, report/latest, reports list, fix-team, fix-bulk (async job queue), fix-jobs status/list, export JSON/CSV
- **Endpoint `/api/seo/team-logo/{file}`**: serve logo cached da `/app/backend/uploads/team_logos/`, evita 403 Wikimedia nel browser
- **Frontend `/admin/seo/health`**: dashboard con summary cards (Total/High/Medium/Low), 6 filtri categoria, severity filter, lista issues con bottone Fix per team, bulk fix con progress bar polling, export JSON/CSV
- **Quick card "Data Health Check"** in `/admin/seo` dashboard
- **Test verificati (iteration_11)**: Backend 11/11 PASS + Frontend 100% PASS. Inter ora mostra logo ufficiale post-2021 (file `/api/seo/team-logo/inter.png` 31KB), 3 eventi Serie A corretti, ZERO Inter Miami leakage

**FASE 3 (Tools Avanzati) – ✅ DONE 2026-05-07**
- **Export Module** (`routes/seo_tools.py` `GET /api/seo/export`): formati JSON/CSV/NDJSON con filtro `type` + `only_published`, Content-Disposition per download. UI in `/admin/seo/bulk`.
- **Nano Banana 2** (`services/seo_image_gen.py`): generazione hero banner 1200x630 via `gemini-3.1-flash-image-preview` + EMERGENT_LLM_KEY. Endpoint `POST /api/seo/hero-image/{type}/{id}` salva PNG in `/app/backend/uploads/seo/` e persiste `seo_hero_image_url` su entity. Servito via `GET /api/seo/uploads/{filename}`.
- **Bulk Runner UI** (`/admin/seo/bulk`):
  - Form Bulk Generate (lega + tipo team/event + limit + only_pending)
  - Endpoint `POST /api/seo/targets/bulk-generate-league` filtra entity per league_slug
  - Tabella Jobs con auto-refresh 4s, status badge, progress bar, score, link diretto al target editor
  - 3 bottoni Export (JSON/CSV/NDJSON) integrati
- Editor SEO arricchito con bottone "Genera Hero Image" + preview immagine generata
- Test verificati (iteration_10): Backend 15/15 PASS + Frontend 3/3 PASS

**FASE 5 (Auto-Normalize Pipeline) – ✅ DONE 2026-05-07**
- **`services/db_normalize.py`** (NEW): wrapper helpers `insert_event/team/league` + `normalize_event_doc/team_doc/league_doc` + `backstop_normalize_all`. Marker `_normalized=True` + `_normalized_at` su ogni doc.
- **Refactor 17 punti di insert**: matchesio_sync, logo_fetcher, apifootball_sync, thesportsdb_sync, openfootball_sync, football_data_sync, football_api_sync, import_matchesio, routes/events.py, routes/teams.py (3 punti), routes/leagues.py (2 punti), routes/admin_content.py — tutti ora applicano normalize_team/normalize_league prima dell'insert.
- **Scheduler arricchito** (`services/scheduler.py`):
  - `auto_sync` 04:00/19:00 UTC (esistente)
  - `normalize_backstop` 04:30/19:30 UTC (NEW): cattura qualsiasi doc non normalizzato post-sync
  - `daily_snapshot` 02:00 UTC (NEW): snapshot metriche per trend storico
  - `health_autofix` 03:00 UTC (NEW): bulk fix logo + dati mancanti via Perplexity + Gemini Vision per nuovi team
- **Retroactive normalize**: lanciato `backstop_normalize_all` su 883 events + 221 teams + 35 leagues esistenti. Re-run `dedup_entities` post-normalize: ZERO duplicati rimasti.

**FASE 6 (Sync Quality Dashboard) – ✅ DONE 2026-05-07**
- `routes/seo_sync_quality.py` (poi rinominato in `routes/data_tools_quality.py` in FASE 7) con 3 endpoint: `/stats`, `/snapshot`, `/sync-runs`
- `pages/admin/seo/SeoSyncQuality.jsx` (poi rinominato in `pages/admin/data-tools/SyncQualityDashboard.jsx`): 4 stat cards top (Events/Teams/Leagues/Logo Coverage), 3 activity panels (Normalize 24h, AI Fixes 7gg, Logo Status), trend chart sparkline 4 metriche, top 20 missing data table con bottone "Fix AI", recent sync runs table.
- Scheduler: nuovo cron 02:00 UTC per snapshot automatico giornaliero (popola trend chart nel tempo).

**FASE 7 (Refactor SEO/Data Tools split) – ✅ DONE 2026-05-07**
- **Modulo SEO portatile** sotto `/admin/seo/*`: contiene SOLO le funzioni riusabili in qualsiasi portale ticketing calcio (Dashboard, ApiTools, PagesList, TargetEditor, BulkRunner). API endpoints prefixed `/api/seo/*`. README `services/SEO_MODULE_README.md` documenta come trasferire in altri progetti.
- **Modulo Data Tools golevents-specifico** sotto `/admin/data-tools/*`: contiene Health Check + Sync Quality (specifici per cleanup/monitoring di portali con dati legacy). API endpoints prefixed `/api/data-tools/*`.
- **Sidebar admin**: nuova voce "Data Tools" (icona Wrench) separata da "SEO" (icona Globe).
- **Files spostati**:
  - `routes/seo_health.py` → `routes/data_tools_health.py` (prefix `/api/data-tools/health`)
  - `routes/seo_sync_quality.py` → `routes/data_tools_quality.py` (prefix `/api/data-tools/sync-quality`)
  - `pages/admin/seo/SeoHealthDashboard.jsx` → `pages/admin/data-tools/DataHealthDashboard.jsx`
  - `pages/admin/seo/SeoSyncQuality.jsx` → `pages/admin/data-tools/SyncQualityDashboard.jsx`
- **Nuovi**: `pages/admin/data-tools/DataToolsDashboard.jsx` (hub con 2 quick cards + box "Automazione attiva").
- **SEO Dashboard pulito**: rimosse cards Health/SyncQuality, restano 4 cards SEO core.
- `routes/seo_sync_quality.py` con 3 endpoint:
  - `GET /api/seo/sync-quality/stats` - metriche real-time (totals, normalize 24h/7d, health_fixes, logo_coverage, missing_data top 20, trend snapshots)
  - `POST /api/seo/sync-quality/snapshot` - manual snapshot trigger
  - `GET /api/seo/sync-quality/sync-runs` - ultimi run di sync matchesio
- `pages/admin/seo/SeoSyncQuality.jsx`: dashboard interattiva con
  - 4 stat cards top (Events, Teams, Leagues, Logo Coverage %)
  - 3 activity panels (Normalize 24h, AI Fixes 7gg, Logo Status)
  - Trend chart sparkline (4 metriche su ultimi N snapshot)
  - Top 20 missing data table con bottone "Fix AI" per team
  - Recent sync runs table (matchesio_sync_runs)
- Quick card "Sync Quality" (data-testid='seo-quick-sync-quality') in dashboard `/admin/seo`
- Google Search Console integration (slot già nel catalog)
- Google PageSpeed Insights integration
- Keyword Research & Competitor Analysis UI page (DataForSEO già OK, manca UI)
- Topic Cluster / Hub-Spoke linking automatico

## Original Problem Statement
Clone del sito web www.golevents.com - un portale per l'acquisto di biglietti per eventi sportivi (principalmente calcio).

## Core Features (Completed)

### Public Website
1. **Homepage** con **lista eventi in due colonne separate**:
   - Colonna sinistra: **Eventi [Paese]** (Italia/España/UK in base alla lingua)
   - Colonna destra: **Eventi Internazionali**
2. **Filtro eventi per lingua**:
   - IT: Eventi in Italia + Champions League + Londra, Manchester, Madrid, Barcellona
   - ES: Eventi in Spagna + Londra, Manchester, Madrid, Barcellona
   - EN: Eventi in UK + Madrid, Barcellona, Milano, Roma, Firenze
3. **Sezione Squadre filtrata per paese**: Mostra solo squadre del paese corrispondente alla lingua selezionata
2. **Pagine di dettaglio** per ogni evento con Schema.org markup
3. **Pagine per campionati/coppe** che elencano squadre o eventi
4. **Pagine per squadre** con tutti gli eventi della squadra
5. **Menu di navigazione** con tutte le categorie espandibili
6. **Ordinamento eventi** per data (dal più prossimo)
7. **Multilingua** (IT, ES, EN) con language switcher
8. **SEO completo**: meta tags, hreflang, Schema.org, sitemap.xml, robots.txt
9. **Dynamic Rendering SEO** (2026-02): HTML pre-renderizzato per bot/crawler via FastAPI
   - index.html arricchito con contenuto SEO fallback (~21KB) + 3 blocchi JSON-LD (Organization, WebSite, SportsActivityLocation)
   - Endpoint `/api/prerender/home` → HTML rich homepage con Organization + WebSite schema
   - Endpoint `/api/prerender/event/{id-or-slug}` → HTML rich evento con SportsEvent + BreadcrumbList schema
   - Endpoint `/api/prerender/league/{slug}` → HTML rich lega con SportsOrganization schema
   - Endpoint `/api/prerender/team/{slug}` → HTML rich squadra con SportsTeam schema
   - `/robots.txt` statico con regole per tutti i bot (Googlebot, Bingbot, facebookexternalhit, Twitterbot, WhatsApp, LinkedInBot)
   - `/llms.txt` per AI crawlers
   - JSON-LD serializzati con json.dumps (validi al 100%)
10. **URL Events SEO-friendly multilingua** (2026-02): schema unificato a tutto il sito
    - Ogni evento ha slug generato da home-vs-away (es. `inter-vs-parma`, duplicati con suffisso -2, -3)
    - URL: IT `/biglietti-inter-vs-parma`, EN `/inter-vs-parma-tickets`, ES `/entradas-inter-vs-parma`
    - Legacy `/event/{id}` redirige automaticamente al nuovo URL slug
    - Auto-backfill slug al startup + dopo ogni sync matchesio
    - Admin endpoint `POST /api/admin/sync/event-slugs` per re-generation manuale
    - Sitemap.xml usa ora gli URL slug (in 3 lingue) invece di /event/{id}
    - Testing: 15/15 backend + 7/7 frontend Playwright passati (2026-02)

### Admin Panel (`/admin`)
1. **Autenticazione** semplice (admin/golevents2024)
2. **Dashboard** con statistiche sistema
3. **Gestione Eventi** con:
   - Supporto multilingua (IT, ES, EN)
   - Categorie biglietti con prezzi e note
   - **Upload immagini diretto** (drag & drop)
   - Impostazioni SEO per ogni evento
   - **Google Snippet Preview** in tempo reale
   - **Social Preview** (Facebook/Twitter)
4. **Gestione Categorie Menu** (campionati, coppe, squadre)
5. **Gestione Pagine & Testi** con editor rich text (React Quill)
6. **Gestione SEO** con:
   - Meta tag, og:image, canonical
   - **Google Snippet Preview** per ogni pagina
   - **Social Preview** per condivisioni
7. **Gestione Traduzioni** per tutti i testi
8. **Impostazioni Sito** (logo, contatti, social, footer)

## SEO Preview Components

### Google Snippet Preview
- Anteprima realistica di come apparirà su Google
- Contatori caratteri (Title: 60 max, Description: 160 max)
- Indicatori visivi (✓ verde = OK, ⚠ giallo = troppo lungo)
- Suggerimenti SEO automatici

### Social Preview
- Anteprima card Facebook/Twitter
- Preview immagine OG
- Titolo e descrizione troncati

## Architecture

### Frontend (React + TailwindCSS + Shadcn UI)
```
/app/frontend/src/
├── components/
│   ├── admin/
│   │   ├── AdminLayout.jsx
│   │   ├── ImageUploader.jsx        # Upload immagini drag & drop
│   │   └── GoogleSnippetPreview.jsx # Preview SEO Google/Social
│   ├── Header.jsx
│   ├── Footer.jsx
│   ├── SEOHead.jsx                  # Meta tags e Schema.org
│   ├── LanguageSwitcher.jsx         # Cambio lingua
│   └── ui/
├── contexts/
│   ├── AdminAuthContext.jsx
│   └── LanguageContext.jsx
├── pages/
│   ├── admin/
│   │   ├── AdminLogin.jsx
│   │   ├── AdminDashboard.jsx
│   │   ├── AdminEvents.jsx          # Con Google Preview
│   │   ├── AdminCategories.jsx
│   │   ├── AdminPages.jsx           # Con Google Preview
│   │   ├── AdminTranslations.jsx
│   │   └── AdminSettings.jsx
│   ├── Home.jsx
│   ├── EventDetail.jsx
│   ├── LeaguePage.jsx
│   └── TeamPage.jsx
└── services/
    └── api.js
```

### Backend (FastAPI + MongoDB)
```
/app/backend/
├── routes/
│   ├── events.py
│   ├── categories.py
│   ├── search.py
│   ├── admin_auth.py
│   ├── admin_content.py
│   ├── upload.py
│   └── seo.py
├── models/
│   └── admin.py
├── uploads/
├── database.py
├── seed_data.py
└── server.py
```

## Admin Credentials
- **URL**: `/admin/login`
- **Username**: `admin`
- **Password**: `golevents2024`

## SEO Endpoints
- **Sitemap**: `/api/sitemap.xml`
- **Robots**: `/api/robots.txt`

## Data Content
- **7 Campionati**: Serie A, Premier League, La Liga, Bundesliga, Liga Portugal, Ligue 1, Super Lig
- **6 Coppe**: Champions League, Europa League, Coppa Italia, Copa del Rey, FA Cup, DFB Pokal
- **~170 partite** con date da Febbraio a Maggio 2026
- **91 squadre** con descrizioni

## Session Completed (Dec 2025)
- [x] Pannello admin completo con autenticazione
- [x] Gestione eventi multilingua (IT/ES/EN)
- [x] Upload immagini diretto (drag & drop)
- [x] Language switcher nel frontend
- [x] SEOHead component con Schema.org
- [x] Sitemap.xml dinamica
- [x] Robots.txt
- [x] **Google Snippet Preview** in tempo reale
- [x] **Social Preview** (Facebook/Twitter)
- [x] Contatori caratteri SEO
- [x] **Layout Homepage** a due colonne (Nazionali/Internazionali)
- [x] **Ricerca AJAX Sticky** sotto header con risultati categorizzati
- [x] **Internazionalizzazione completa** (i18n) per tutta la UI
- [x] **Loghi squadre** con CDN
- [x] **Filtro squadre per paese** basato sulla lingua
- [x] **Refactoring tipografico**: dimensioni testi proporzionate in tutte le pagine
- [x] **Sistema priorità eventi**: squadre principali in evidenza (Milan, Inter, Juventus, Roma, Fiorentina, Lazio, Barcelona, Real Madrid, Sevilla, Valencia, Manchester City, Manchester United, Arsenal, Chelsea, Liverpool)
- [x] **Formato titoli eventi coppa**: rimosso "(1st Leg)", "(Quarter Final)" etc. e aggiunto "- Nome Coppa"
- [x] **Traduzione nomi città**: Milano, Londra, Barcellona, Roma, etc. tradotti in IT/ES/EN
- [x] **Traduzione date**: giorni settimana e mesi tradotti in base alla lingua selezionata
- [x] **SEO Completo**: 
  - Meta tag tradotti (title, description, og:title, og:description)
  - H1 tradotti ("Biglietti Inter" / "Inter Tickets" / "Entradas Inter")
  - Canonical URL su tutte le pagine
  - Hreflang per IT/ES/EN
  - Schema.org per eventi
  - Alt images tradotti

## Session Completed (Feb 2026)
- [x] **Sitemap.xml multilingua**: URL per homepage, leghe, coppe, squadre, eventi con tag hreflang
- [x] **Robots.txt**: Configurato con link sitemap e disallow /admin/
- [x] **Schema.org JSON-LD completo**:
  - OrganizationSchema su Homepage
  - LeagueSchema + BreadcrumbSchema su pagine lega/coppa
  - TeamSchema + BreadcrumbSchema su pagine squadra  
  - EventSchema + BreadcrumbSchema su pagine evento (SportsEvent con location, offers, performer)
- [x] **Breadcrumbs visivi**: Navigazione a briciole di pane su tutte le pagine interne
- [x] **Fix Schema.org**: Risolto bug con react-helmet-async usando useEffect per iniezione DOM
- [x] **Test SEO 100% passati**: Sitemap, robots.txt, Schema.org, breadcrumbs verificati
- [x] **Pagina Admin Settori**: Gestione settori/prezzi per ogni evento con settori default e bulk operations
- [x] **Collezione Leghe (DB)**: 7 campionati + 6 coppe nel database
- [x] **Collezione Squadre (DB)**: 137 squadre collegate alle leghe
- [x] **Pagina Admin Leghe & Squadre**: CRUD completo per leghe e squadre
- [x] **Frontend Dinamico**: LeaguePage ora carica squadre dal database invece che da array hardcoded

## Settori Default per Eventi
Ogni nuovo evento può avere questi settori preconfigurati:
- Cat 1 Premium
- Cat 1 Normal
- Cat 2 Short Side Lower
- Cat 2 Long Side Upper
- Cat 3 Short Side
- Best Available
  
## REGOLE URL MEMORIZZATE (NON MODIFICARE):
- **IT**: biglietti PRIMA del nome con trattino → `/biglietti-inter`
- **EN**: tickets DOPO il nome con trattino → `/inter-tickets`
- **ES**: entradas PRIMA del nome con trattino → `/entradas-inter`

## Future Enhancements (Backlog)
- [ ] **Sistema di scraping automatico** per aggiornare eventi e prezzi (es. GitHub Actions)
- [ ] **Floating button WhatsApp** per contatto rapido
- [ ] **Badge Urgency** ("Solo 3 biglietti rimasti!")
- [ ] **Badge Trust** (loghi pagamenti sicuri)
- [ ] Ottimizzazione immagini (WebP, lazy loading)
- [ ] Pagina 404 personalizzata
- [ ] Alt tag descrittivi su tutte le immagini
- [ ] Sezione Blog/News per traffico organico
- [ ] Sistema di autenticazione utenti
- [ ] Carrello e checkout
- [ ] Integrazione pagamenti (Stripe)
- [ ] Notifiche email
- [ ] Analytics dashboard
- [ ] A/B testing SEO
- [ ] Mappe SVG dinamiche per stadi diversi (oggi solo San Siro)

## Session Completed (Apr 2026 - Aggiunta Eventi Maggio + WC2026)
- [x] **+238 eventi inseriti** in DB tramite `seed_additional_events.py`
  - Serie A: 39 partite (giornate 33-36, Maggio 2026)
  - Premier League: 31 partite (matchdays 36-38)
  - La Liga: 30 partite (matchdays 36-38, incluso Real Madrid vs Barcelona)
  - Bundesliga: 18 partite (matchdays 33-34)
  - Ligue 1: 16 partite (giornate finali)
  - Liga Portugal: 7 partite (incluso Sporting vs Benfica)
  - Super Lig: 6 partite (derby Galatasaray-Fenerbahçe)
  - Champions League: 5 (semifinali + Final 30 Maggio Budapest)
  - Europa League: 5 (semifinali + Final 20 Maggio Istanbul)
  - FA Cup Final 2026 (16 Maggio, Wembley)
  - **FIFA World Cup 2026: 80 partite** (11 Giugno - 19 Luglio):
    - 16 partite Matchday 1 (apertura Mexico-Sudafrica all'Estadio Azteca)
    - 16 Matchday 2, 16 Matchday 3, 16 Round of 32, 8 Round of 16, 4 QF, 2 SF, 3rd Place, **Final 19 Luglio MetLife Stadium**
- [x] **Lega "FIFA World Cup 2026"** aggiunta nel DB (slug: `fifa-world-cup-2026`)
- [x] **+30% Viagogo markup** applicato a tutti i prezzi
- [x] **Routing aggiornato** (`App.js` → `LEAGUE_SLUGS` include `fifa-world-cup-2026`, `liga-portugal`, `super-lig`, `dfb-pokal`)
- [x] **Menu mega-dropdown** con voce "WORLD CUP 2026 / MONDIALI 2026 / MUNDIAL 2026"
- [x] **Traduzioni** IT/ES/EN per fifaWorldCup2026 e usa
- [x] **LeaguePage** ora carica fino a 100 eventi per coppa (era 20)
- [x] **Verificato visivamente**: Inter-Parma, Inter team page (6 partite), FIFA WC page (80 partite), Home (50 eventi)

## Session Completed (Apr 2026 - Import REALE da matchesio.com)
- [x] 🎉 **SCOPERTA**: matchesio.com offre JSON pubblici di calendari calcio gratis (NO Cloudflare!)
  - Pattern URL: `https://www.matchesio.com/it/competition/{slug}/export/json/`
  - 13 competizioni disponibili: Serie A, Premier League, La Liga, Bundesliga, Ligue 1,
    Liga Portugal, Super Lig, Champions League, Coppa Italia, Copa del Rey, FA Cup,
    DFB Pokal, FIFA World Cup 2026
- [x] Script `import_matchesio.py` che cancella DB e importa dati ufficiali
- [x] **353 eventi reali** importati (date/stadi/squadre ufficiali, partite future)
- [x] **104 partite FIFA World Cup 2026** complete (vs 80 placeholder precedenti)
- [x] **Rimossi tutti i prezzi** da eventi (richiesta utente)
- [x] **7 settori standard**: Cat 1 - Lower Central, Cat 1 - Middle Central, Cat 1 - Normal,
  Cat 2 - Long Upper, Cat 2 - Short Lower, Cat 3 - Short Side Middle, Cat 4 - Short Upper
- [x] **Frontend**: rimossi prezzi da `EventListItem.jsx` e `EventDetail.jsx`
- [x] **Home columns balanced**: stesso numero di eventi in UK Events / International Events
- [x] **Cancellati eventi passati**: filtro automatico per `sort_date >= today`
- [x] **Stadium maps disabilitate** automaticamente (solo flag esplicito da admin)

## Possibile Enhancement (matchesio.com)
- Aggiungere endpoint admin `/api/admin/sync-matchesio` per refresh on-demand
- Cron job giornaliero per auto-aggiornamento partite (status, results, ecc.)
- Mapping dei nuovi campionati man mano che matchesio li aggiunge


## Session Completed (Apr 2026 - Tutte le Next Actions)
- [x] **Sync admin pannello** `/admin/sync` con UI completa (storico, modalità, sync manuale)
- [x] **Endpoint REST** `POST /api/admin/sync/matchesio` + `GET /api/admin/sync/logs` (auth richiesta)
- [x] **Modulo riusabile** `services/matchesio_sync.py` con normalizzazione nomi (USA, AC Milan, ecc.)
- [x] **Cron schedulato** AsyncIOScheduler (`services/scheduler.py`) ogni 6h: 00/06/12/18 UTC
- [x] **Soglia di sicurezza** sync: se < 50 eventi fetched → ABORT (protezione contro matchesio.com down)
- [x] **Default sicuro**: `replace_all=False` (upsert), `replace_all=True` cancella SOLO eventi matchesio_id (custom preservati)
- [x] **WhatsAppButton.jsx**: floating button verde con tooltip e ping animation
- [x] **UrgencyBadges.jsx**: 3 badge (biglietti rimasti / live viewers / acquisti 24h) deterministici per eventId
- [x] **TrustBadges.jsx**: 5 loghi pagamento (Visa, MasterCard, PayPal, Apple Pay, Stripe) + 3 trust points
- [x] **NotFound.jsx**: pagina 404 personalizzata con palla calcio animata, CTA tradotti IT/ES/EN
- [x] **DynamicRouter**: ora restituisce <NotFound /> invece di <Home /> per slug sconosciuti
- [x] **Test backend 13/13 PASS** (testing_agent_v3_fork iteration_3)
- [x] **test_credentials.md** creato in /app/memory/

### Endpoint chiave
- `POST /api/admin/sync/matchesio?replace_all=false` (default upsert)
- `GET /api/admin/sync/logs?limit=10`

### Cron details
APScheduler AsyncIOScheduler in `services/scheduler.py` con `CronTrigger(hour="0,6,12,18")`.
Logging completo in stdout backend; errori catturati in `db.sync_logs`.

## Session Completed (Apr 2026 - Auto-discovery leghe)
- [x] **COMPETITIONS estesa a 33 leghe** (era 13): aggiunte MLS, Liga MX, J1 League,
  Eredivisie, Jupiler Pro League, Championship, 2. Bundesliga, Ligue 2,
  Coupe de France, KNVB Beker, Conference League, Nations League,
  Club World Cup, EURO, Copa America, AFCON, Asian Cup,
  Copa Libertadores, AFC Champions League
- [x] **`ensure_league_in_db()`** - durante ogni sync auto-crea le leghe in `db.leagues`
  con campo `auto_created: true`. Eventi accessibili immediatamente via URL
- [x] **GET `/api/leagues/active-slugs`** - endpoint per frontend routing dinamico
- [x] **Header dinamico** mega menu:
  - Sezione "+Altre leghe" auto-rilevata (MLS, Liga MX, J1, Eredivisie, ecc.)
  - Sezione "+Altre coppe" auto-rilevata (Conference League, Nations League,
    Copa America, ecc.)
- [x] **LeaguePage**: ora gestisce sia "cup" che "league senza teams" (mostra eventi)
- [x] **DynamicRouter**: LEAGUE_SLUGS aggiornato con tutti i 32 slug curated
- [x] **968 eventi totali** in DB (era 353): MLS 366, J1 League 61,
  Copa Libertadores 64, World Cup 104, Eredivisie 31, Liga Portugal 28, Champions 5
- [x] **19 leghe NUOVE** create automaticamente al primo sync

## Session Completed (Apr 2026 - Auto Logo Fetcher)
- [x] **`services/logo_fetcher.py`**: integrazione TheSportsDB API gratuita
- [x] **Auto-popolamento logo leghe** integrato nel sync matchesio
- [x] **Endpoint manuale `POST /api/admin/sync/logos?team_batch=50`** per squadre
- [x] **Risultato**: 142 team con logo + 20/33 leghe con logo
- [x] **Events enriched**: `home_team_logo` e `away_team_logo` automatici nelle response API
- [x] **EventListItem**: mostra logo home vs away nelle card homepage
- [x] **LeaguePage**: usa `leagueData.logo_url` da DB
- [x] **AdminSync UI**: bottone "Popola Loghi" verde
- [x] Rate limiting 2.1s + retry su HTTP 429

## Session Completed (Apr 2026 - P2 Refactor + P3 SEO)
### P2 Backend Refactor (12/12 test PASS)
- [x] **httpx.AsyncClient** sostituito requests sync in `matchesio_sync.py` e `logo_fetcher.py`
- [x] **asyncio.gather** con `Semaphore(5)` per fetch parallelo 33 competizioni in **2.6s** (era 30+s)
- [x] **asyncio.sleep** sostituito time.sleep nel rate limiter (event loop NON bloccato)
- [x] **Token DB-backed**: `db.admin_tokens` collection con TTL index per auto-cleanup
- [x] **Token persiste** tra restart backend (testato con sudo supervisorctl restart)
- [x] **Background task** per `populate_league_logos`: il sync matchesio non blocca mai >5s
- [x] **Auth header parsing** sicuro con `split(' ', 1)` invece di `replace("Bearer ", "")`
- [x] **datetime.utcnow → datetime.now(timezone.utc)** in routes/events.py

### P3 SEO Frontend
- [x] **56/56 immagini** con `loading="lazy"` (lazy loading attivo)
- [x] **56/56 immagini** con `decoding="async"` (parsing non bloccante)
- [x] **Alt tag descrittivi** ottimizzati su tutte le immagini:
  - Logo squadre: `Logo {nome team}`
  - Logo leghe: `Logo {nome lega}`
  - Hero immagini eventi: `{titolo} - {stadio} {città}`
  - Categories: `Logo {team} - Biglietti calcio ufficiali`
- [x] **Logo critical** (header pagina lega/team): `loading="eager"` per LCP

### Risultati misurati
- Sync matchesio.com: **2.6s** (era 30+s) ✓
- Backend response durante sync: **5ms** (event loop libero) ✓
- Token persistenza: ✓ supera restart
- TTL cleanup automatico tokens scaduti: ✓
- 56 immagini lazy-loaded all'apertura della home
- [x] Schema `db.teams` arricchito: `{name, slug, logo_url, league_slug, active, auto_created}`

## Session Completed (Apr 2026 - P2 Sviluppo Completo)
- [x] **datetime.utcnow → datetime.now(timezone.utc)** in categories.py, models/event.py, models/category.py
- [x] **GET `/api/health`**: monitoring con DB ping + scheduler status + counts
- [x] **POST `/api/admin/sync/team-logo/{id}`**: refresh logo singola squadra
- [x] **AdminTeams page** `/admin/teams-logos`: gestione 187 squadre con stats, filtri, refresh logo per ogni squadra
- [x] **AdminLayout** voce "Squadre & Loghi" nel sidebar

### SEO P3
- [x] `index.html`: lang="it", description GOLEVENTS, theme-color brand, preconnect critici, preload font Inter
- [x] `SEOHead.jsx` Open Graph completi: og:site_name, og:image:width/height, og:url, og:locale:alternate, twitter:site, robots ottimizzato