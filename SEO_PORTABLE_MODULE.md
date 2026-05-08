# SEO Automation Module — Portable v3.0

> **Versione**: 3.0 (2026-05-08)
> **Modulo SEO portabile completo**. Riusabile in qualsiasi progetto FastAPI + React + MongoDB.
> Specificamente progettato per portali di **ticketing sportivo** (calcio, eventi live).

Questo modulo è stato **architetturalmente isolato** dal codebase host. Tutto ciò che riguarda DB hygiene specifica di GoLevents (`/admin/data-tools/*`, `/api/data-tools/*`) è **fuori** dal modulo. Questo README descrive **solo** ciò che serve per integrare il modulo SEO in un nuovo progetto come `ticketgol.com`.

> **CHANGELOG v3.0 (2026-05-08)**:
> - ➕ Aggiunto **API Cost Observatory** (FASE 12) — track spese, latency, budget, alert email Resend/SMTP
> - ➖ Rimosso **Team Verifier** dal modulo SEO → spostato in Data Tools (è data hygiene, non SEO)
> - 🆕 v3.0 file count: **47 file** (5 routes + 22 services backend + 12 pages + 6 components frontend + 1 util + 1 README)

---

## 🎯 Cosa contiene questo modulo

### 🤖 SEO Pipeline Generation (FASE 1-3)
- **Dual-Engine async**: DataForSEO → Claude → Perplexity → DeepL → Gemini → Validator → Nano Banana 2
- **Job queue** con polling, status, progress, score 0-100
- **Bulk Generate** by lega/squadra/evento con cascading filter
- **Hero image generation** (Gemini Nano Banana 2) — banner 1200×630 cached
- **Export JSON/CSV/NDJSON**

### 🧠 SEO Intelligence Hub (FASE 10)
- **Topic Cluster** — Hub-Spoke graph + auto internal linking
- **Cannibalization Detector** — rapidfuzz token_set_ratio, severity tiers
- **Hreflang Validator** — required langs, x-default, ISO 639-1, URL pattern
- **AI FAQ Generator** — Claude genera 6 FAQ PAA-optimized per lang → **FAQPage rich snippet**
- **JSON-LD Validator** — schema.org packet validator
- **Trust Score** — endpoint pubblico per badge "Verified by N sources"

### 💰 API Cost Observatory (FASE 12)
- **Decorator `@track_api_usage(provider, op_type)`** loggante cost/tokens/latency/status su ogni call
- **Dashboard 17 metriche enterprise**: today/week/month, forecast, top provider, success rate, avg latency
- **Per-provider rollup**: budget bar + last_used + success rate
- **Top 10 entità più costose**, by-type, daily chart, latency p50/p95
- **Logs drill-down** con filtri provider/status
- **Alert engine**: BUDGET_WARNING / BUDGET_EXCEEDED / LOW_BALANCE / API_DOWN / API_INTERMITTENT
- **Email dispatch**: Resend (primary) + SMTP (fallback) graceful
- **Real polling** balance: Claude/Gemini/Perplexity/DataForSEO/DeepL
- **Backfill**: ricostruisce log da seo_jobs storici
- **Scheduler**: alert checks ogni 30min UTC

### 🌐 Public Frontend Components
- `SeoSchemaInjector` — JSON-LD nel `<head>`
- `FAQPageSchema` — auto-injection FAQPage schema
- `TrustScoreBadge` — badge social proof
- `SeoContentBlock` — rendering SEO content (h1, intro, main, cta)

---

## 📁 File da copiare nel nuovo progetto (ticketgol.com)

### Backend `/backend/`

#### Routes (5 file in `routes/`)
```
routes/seo_admin.py          # Catalog 11 tool API (incl. Resend) + key encrypted (Fernet)
routes/seo_targets.py        # List/edit/generate/publish entity SEO
routes/seo_tools.py          # Hero Image + Export + Bulk Generate by League
routes/seo_intelligence.py   # Topic Cluster + Cannibalization + Hreflang + FAQ + JSON-LD Validator + Trust Score
routes/cost_observatory.py   # 🆕 API Cost Observatory (overview/providers/logs/alerts/budgets/pricing/balance/export/backfill)
```

#### Services (17 file in `services/`)
```
services/seo_keys.py              # Encrypted storage Fernet
services/seo_crypto.py            # Fernet helper
services/seo_tools_catalog.py     # Catalog tool API (incl. Resend slot per email alerts)
services/seo_orchestrator.py      # Pipeline state machine async
services/seo_claude.py            # Master IT copywriting
services/seo_gemini.py            # JSON-LD schema graph
services/seo_perplexity.py        # FAQ PAA + GeoCoordinates + sameAs
services/seo_deepl.py             # Translation IT→EN/ES
services/seo_dataforseo.py        # Keyword research
services/seo_validator.py         # Max-length + density + score 0-100
services/seo_entity_context.py    # DB lookup related entities
services/seo_image_gen.py         # Nano Banana 2 hero
services/seo_topic_cluster.py     # Hub-Spoke graph builder
services/seo_cannibalization.py   # rapidfuzz keyword overlap
services/seo_hreflang.py          # Hreflang validator
services/seo_faq_generator.py     # Claude FAQ 6× lang
services/seo_jsonld_validator.py  # schema.org packet validator
services/api_cost_tracker.py      # 🆕 @track_api_usage decorator + log persistence
services/api_cost_observatory.py  # 🆕 Aggregations (overview/providers/entities/chart/latency)
services/api_pricing.py           # 🆕 cost_per_unit per provider/op_type
services/api_alerts.py            # 🆕 Alert engine + Resend HTTP + SMTP fallback
services/api_balance_checker.py   # 🆕 Real polling balance per provider
```

> **Nota**: `seo_team_verifier.py` è stato **rimosso** dal modulo SEO in v3.0 (spostato in Data Tools nel progetto host). Non includerlo in `ticketgol.com` — la verifica metadati team è una funzione di DB hygiene, non SEO.

### Frontend `/frontend/src/`

#### Pages (11 file in `pages/admin/seo/`)
```
pages/admin/seo/SeoDashboard.jsx
pages/admin/seo/SeoApiTools.jsx
pages/admin/seo/SeoPagesList.jsx
pages/admin/seo/SeoTargetEditor.jsx
pages/admin/seo/SeoBulkRunner.jsx              # cascading filter Lega → Squadra → Evento
pages/admin/seo/CostObservatory.jsx            # 🆕 v3.0 (FASE 12)
pages/admin/seo/intelligence/SeoIntelligenceHub.jsx
pages/admin/seo/intelligence/TopicCluster.jsx
pages/admin/seo/intelligence/Cannibalization.jsx
pages/admin/seo/intelligence/Hreflang.jsx
pages/admin/seo/intelligence/FaqGenerator.jsx
pages/admin/seo/intelligence/JsonLdValidator.jsx
```

> **Rimosso in v3.0**: `pages/admin/seo/intelligence/TeamVerifier.jsx` (spostato in `pages/admin/data-tools/TeamVerifier.jsx` perché è data hygiene, non SEO).

#### Components (5 file in `components/`)
```
components/SeoContentBlock.jsx          # rendering pubblico SEO content
components/SeoSchemaInjector.jsx        # JSON-LD <script> injection
components/SchemaOrg.jsx                # 🆕 EventSchema + LeagueSchema + TeamSchema + FAQPageSchema + BreadcrumbSchema
components/TrustScoreBadge.jsx          # 🆕 badge "Verified by N sources"
components/admin/SeoTargetSelector.jsx  # 🆕 cascading dropdown Lega → Squadra → Evento
components/admin/SeoFilterStatusPanel.jsx # 🆕 panel con tabella stato entity
```

#### Utils (1 file in `utils/`)
```
utils/seoHero.js                  # 🆕 helper resolveSeoHeroUrl(raw)
```

---

## 🔧 Setup nel nuovo progetto

### 1. Backend setup

```python
# server.py
from routes import seo_admin, seo_targets, seo_tools, seo_intelligence, cost_observatory

app.include_router(seo_admin.router)
app.include_router(seo_targets.router)
app.include_router(seo_tools.router)
app.include_router(seo_intelligence.router)
app.include_router(cost_observatory.router)
```

#### Variabili `.env` richieste
```bash
MONGO_URL=mongodb://...           # esistente
DB_NAME=...                       # esistente
EMERGENT_LLM_KEY=sk-emergent-...  # Universal key per Claude/Gemini/Nano Banana
SEO_FERNET_KEY=...                # base64 32-byte key per encrypted storage chiavi 3rd party
```

Genera `SEO_FERNET_KEY`:
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

#### Dipendenze Python
```bash
pip install httpx motor pydantic apscheduler rapidfuzz cryptography emergentintegrations
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
```

### 2. Frontend setup

```jsx
// App.js
import SeoDashboard from './pages/admin/seo/SeoDashboard';
import SeoApiTools from './pages/admin/seo/SeoApiTools';
import SeoPagesList from './pages/admin/seo/SeoPagesList';
import SeoTargetEditor from './pages/admin/seo/SeoTargetEditor';
import SeoBulkRunner from './pages/admin/seo/SeoBulkRunner';
import CostObservatory from './pages/admin/seo/CostObservatory';
import SeoIntelligenceHub from './pages/admin/seo/intelligence/SeoIntelligenceHub';
import SeoIntTopicCluster from './pages/admin/seo/intelligence/TopicCluster';
import SeoIntCannibalization from './pages/admin/seo/intelligence/Cannibalization';
import SeoIntHreflang from './pages/admin/seo/intelligence/Hreflang';
import SeoIntFaqGenerator from './pages/admin/seo/intelligence/FaqGenerator';
import SeoIntJsonLdValidator from './pages/admin/seo/intelligence/JsonLdValidator';

// SEO Routes
<Route path="/admin/seo" element={<SeoDashboard />} />
<Route path="/admin/seo/api-tools" element={<SeoApiTools />} />
<Route path="/admin/seo/pages" element={<SeoPagesList />} />
<Route path="/admin/seo/targets/:type/:id" element={<SeoTargetEditor />} />
<Route path="/admin/seo/bulk" element={<SeoBulkRunner />} />
<Route path="/admin/seo/cost-observatory" element={<CostObservatory />} />
<Route path="/admin/seo/intelligence" element={<SeoIntelligenceHub />} />
<Route path="/admin/seo/intelligence/topic-cluster" element={<SeoIntTopicCluster />} />
<Route path="/admin/seo/intelligence/cannibalization" element={<SeoIntCannibalization />} />
<Route path="/admin/seo/intelligence/hreflang" element={<SeoIntHreflang />} />
<Route path="/admin/seo/intelligence/faq" element={<SeoIntFaqGenerator />} />
<Route path="/admin/seo/intelligence/jsonld-validator" element={<SeoIntJsonLdValidator />} />
```

#### Dipendenze npm
```bash
yarn add lucide-react sonner react-router-dom
```

### 3. Public pages integration

Per ogni pagina pubblica (`EventDetail`, `LeaguePage`, `TeamPage`):

```jsx
import { EventSchema, BreadcrumbSchema, FAQPageSchema } from '../components/SchemaOrg';
import TrustScoreBadge from '../components/TrustScoreBadge';
import { resolveSeoHeroUrl } from '../utils/seoHero';

// Hero image background da SEO module
const heroImageUrl = resolveSeoHeroUrl(event.seo_hero_image_url);

return (
  <>
    <EventSchema event={event} lang={lang} />
    <BreadcrumbSchema items={breadcrumbs} />
    <FAQPageSchema entityType="event" slug={event.slug} lang={lang} />

    <div style={heroImageUrl ? { backgroundImage: `url(${heroImageUrl})` } : {}}>
      ...
      <TrustScoreBadge entityType="event" slug={event.slug} compact />
    </div>
  </>
);
```

---

## 📊 Schema MongoDB richiesto (entity host)

Il modulo SEO popola questi campi sulle entity esistenti del progetto host (`events`, `teams`, `leagues`):

```javascript
{
  slug: "string (unique, required)",
  name: "string (team/league)",         // OR
  home_team: "string", away_team: "string",  // (event)
  league: "string", league_slug: "string",
  stadium: "string", city: "string", country: "string",

  // Popolati dal modulo SEO (multi-lang: it/en/es)
  seo_meta: {
    it: {
      title: "string (max 60)",
      description: "string (max 160)",
      h1: "string",
      intro_text: "string",
      main_content: "string (HTML)",
      cta_text: "string",
      open_graph_title: "string",
      open_graph_description: "string",
      twitter_card_title: "string",
      twitter_card_description: "string",
      legal_disclosure_text: "string",
      internal_links: [{ url, anchor, rel }],
      image_alt_texts: { hero, og, twitter },
      faq: [{ q, a }, ...],              // FAQ AI generator output
      json_ld_packet: { /* @graph */ },  // Gemini schema output
      canonical_url: "string"
    },
    en: { /* same structure */ },
    es: { /* same structure */ }
  },
  seo_hero_image_url: "/api/seo/uploads/...",
  seo_status: "Draft | Generated | Approved | Published",
  seo_score: 0-100,
  seo_draft: { /* working copy pre-publish */ }
}
```

### Collections create automaticamente
```
seo_api_keys          # encrypted Fernet
seo_jobs              # async pipeline queue
seo_geo_cache         # Perplexity geocoding cache
seo_entity_links      # sameAs Wikipedia links cache
api_usage_logs        # 🆕 v3.0 — log di ogni call tracciata (provider, op, cost, tokens, lat, status)
api_alerts            # 🆕 v3.0 — alert generati (BUDGET/LOW_BALANCE/API_DOWN/INTERMITTENT)
api_budgets           # 🆕 v3.0 — budget per provider (monthly limit + warning %)
api_pricing           # 🆕 v3.0 — overrides custom su pricing default
```

---

## 🌍 API Endpoints (prefix `/api/seo` + `/api/seo/intelligence` + `/api/seo/cost-observatory`)

### Generation pipeline
```
GET  /api/seo/admin/tools                         # Catalog
POST /api/seo/admin/tools/{tool_id}/key           # Save key encrypted
GET  /api/seo/targets?type=event&league_slug=...  # Cascading filter
GET  /api/seo/targets/{type}/{id}                 # Entity con seo_meta
POST /api/seo/targets/{type}/{id}/generate        # Avvia pipeline (returns job_id)
GET  /api/seo/jobs/{job_id}                       # Polling status
POST /api/seo/targets/{type}/{id}/publish         # Apply draft
POST /api/seo/targets/bulk-generate-league        # Batch by league/team
POST /api/seo/hero-image/{type}/{id}              # Nano Banana 2
GET  /api/seo/uploads/{filename}                  # Hero image cached
GET  /api/seo/export?format=json|csv|ndjson       # Backup data
```

### Intelligence Hub
```
GET  /api/seo/intelligence/topic-cluster/overview
GET  /api/seo/intelligence/topic-cluster/{type}/{slug}
GET  /api/seo/intelligence/cannibalization/scan?threshold=85
GET  /api/seo/intelligence/hreflang/scan
GET  /api/seo/intelligence/hreflang/{type}/{slug}
POST /api/seo/intelligence/faq/{type}/{slug}/generate?langs=it,en,es
GET  /api/seo/intelligence/faq/{type}/{slug}
GET  /api/seo/intelligence/faq/{type}/{slug}/public  # 🌍 NO AUTH (per frontend)
GET  /api/seo/intelligence/jsonld/scan
GET  /api/seo/intelligence/trust-score/{type}/{slug} # 🌍 NO AUTH (per frontend)
```

### Cost Observatory (FASE 12)
```
GET  /api/seo/cost-observatory/overview              # Today/Week/Month + forecast + top provider
GET  /api/seo/cost-observatory/providers             # Per-provider rollup mese corrente
GET  /api/seo/cost-observatory/entities/top          # Top 10 entità più costose
GET  /api/seo/cost-observatory/entities/by-type      # Aggregato per tipo entità
GET  /api/seo/cost-observatory/chart/daily           # Spesa giornaliera (grafico 30g)
GET  /api/seo/cost-observatory/latency               # Latency p50/p95 per provider
GET  /api/seo/cost-observatory/logs                  # Drill-down log con filtri
GET  /api/seo/cost-observatory/alerts/open           # Alert aperti
POST /api/seo/cost-observatory/alerts/run-checks     # Trigger manuale alert engine
POST /api/seo/cost-observatory/alerts/{id}/ack       # Ack alert
GET  /api/seo/cost-observatory/budgets               # Budget per provider
POST /api/seo/cost-observatory/budgets/{provider}    # Set/update budget
GET  /api/seo/cost-observatory/pricing               # Pricing config
GET  /api/seo/cost-observatory/alert-config          # Email/SMTP/Resend config
POST /api/seo/cost-observatory/alert-config          # Save config
GET  /api/seo/cost-observatory/balance               # Real polling balance per provider
GET  /api/seo/cost-observatory/export?days=30        # CSV download
POST /api/seo/cost-observatory/backfill?days=30      # Ricostruisce log da seo_jobs
```

---

## 💰 Costi per entity (1 generation completa)
- DataForSEO: $0.001 (cached)
- Claude Sonnet 4.5: $0.04
- Perplexity Sonar Pro: $0.005
- DeepL: gratis fino 500k char/mese
- Gemini 3 Pro: $0.02
- Nano Banana 2: $0.04 (1024×1024 PNG)
- **Totale per entity: ~$0.10** (o $0 se usi solo Emergent Universal Key + DeepL Free)

---

## 🎨 Schema.org coverage

Il modulo genera un grafo JSON-LD completo:
- **SportsEvent / SportsTeam / SportsOrganization**
- **AggregateOffer** (price range)
- **AggregateRating** (★ stars in SERP)
- **BreadcrumbList**
- **FAQPage** (6 domande PAA, AI-generated) → 🌟 **rich snippet**
- **HowTo** "Come acquistare biglietti" (5 step) → AI Overviews target
- **Place + GeoCoordinates + PostalAddress** (local pack)
- **Speakable** (voice search)
- **subjectOf + sameAs** (Wikipedia entity linking)
- **eventStatus dinamico** (compliance ticketing)
- **Reseller disclosure** DDL 145/2018 (italian compliance)

---

## 🔄 Cron jobs schedulati (opzionale)

Aggiungi a `services/scheduler.py` del progetto host:

```python
# Alert checks ogni 30 minuti (budget warning/exceeded, low balance, API down)
async def _api_alert_checks():
    from services.api_alerts import run_all_alert_checks
    await run_all_alert_checks()

scheduler.add_job(
    _api_alert_checks,
    CronTrigger(minute="*/30"),
    id="alert_checks_30min",
)
```

> **Rimosso in v3.0**: il cron `team_verifier_weekly` non è più parte del modulo SEO portabile — appartiene al modulo Data Tools nel progetto host (è DB hygiene, non SEO). Se ti serve, implementalo separatamente al di fuori di questo modulo.

---

## 🌐 Multilingua (IT / EN / ES)

- Master content in **italiano** (Claude Sonnet 4.5)
- DeepL traduce automaticamente in EN + ES con glossario tecnico ticketing (Settore Ospiti, Curva Sud, ecc.)
- AI FAQ Generator produce **6 FAQ × 3 lingue** = 18 FAQ totali per entity
- hreflang gestito a livello globale dal sito host
- Hreflang Validator built-in flagga inconsistenze (lingue mancanti, x-default, URL mismatch)

---

## 🛡️ Sicurezza

- API keys 3rd party **encrypted at rest** con Fernet (`SEO_FERNET_KEY` env)
- Tutti gli endpoint admin richiedono `verify_admin_token` Bearer
- Endpoint pubblici (`/api/seo/intelligence/faq/.../public`, `/api/seo/intelligence/trust-score/...`) — solo lettura, no PII
- Hero images servite con cache headers, no auth (URL pubblici)

---

## 📞 Supporto integrazione

Per domande sull'integrazione del modulo, riferirsi a:
- File `seo_orchestrator.py` per la pipeline state machine
- File `seo_intelligence.py` per gli endpoint Intelligence Hub
- Test suite di riferimento: `/app/backend/tests/test_seo_intelligence.py`

---

## 📋 Checklist integrazione ticketgol.com

- [ ] Copia 5 routes + 22 services backend (incl. Cost Observatory)
- [ ] Copia 12 pages (6 SEO + 6 Intelligence) + 6 components + 1 util frontend
- [ ] Aggiungi `EMERGENT_LLM_KEY` e `SEO_FERNET_KEY` in `.env`
- [ ] Installa dipendenze Python (`rapidfuzz`, `cryptography`, `emergentintegrations`)
- [ ] Installa dipendenze npm (`lucide-react`, `sonner`)
- [ ] Registra 12 routes in `App.js` (incl. `/admin/seo/cost-observatory`)
- [ ] Registra 5 routers in `server.py` (incl. `cost_observatory.router`)
- [ ] Verifica entity host abbiano campi richiesti (`slug`, `name`/`home_team`+`away_team`, `league`, `stadium`, `city`, `country`)
- [ ] Apri `/admin/seo/api-tools` e configura API keys 3rd party (DataForSEO, Perplexity, DeepL, **Resend** per email alerts — opzionali se solo Universal Key)
- [ ] Lancia primo Bulk Generate via `/admin/seo/bulk` su una lega di test
- [ ] Verifica `/admin/seo/intelligence` mostra metriche (5 stat cards)
- [ ] Verifica `/admin/seo/cost-observatory` mostra spesa real-time
- [ ] Aggiungi `<EventSchema>`, `<FAQPageSchema>`, `<TrustScoreBadge>` in pagine pubbliche
- [ ] Setup cron `alert-checks` ogni 30min (Cost Observatory)

---

**Versione**: 3.0 — last update 2026-05-08
**License**: proprietary GoLevents (uso interno e progetti affiliati)
