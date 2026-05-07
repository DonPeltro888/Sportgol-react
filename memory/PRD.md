# GOLEVENTS Clone - Product Requirements Document

## Status (2026-05-07)
- ✅ Sito live su https://golevents.com
- 🟡 Deploy bloccato da bug piattaforma Emergent: "Internal Server Error" al click "Re-deploy changes" (ticket aperto support@emergent.sh)
- ✅ Tutti i fix code-level deploy-ready applicati (BASE_URL, .gitignore, startup background, requirements.txt, upload.py)
- ✅ **SEO Automation Admin – FASE 1 (Foundation) COMPLETATA**
- 🆕 **SEO Automation Admin – FASE 2 (Pipeline Dual-Engine reale) COMPLETATA il 2026-05-07**

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

**FASE 5 (P1) – Backlog**
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