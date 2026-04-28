# GOLEVENTS Clone - Product Requirements Document

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
- [x] **+238 eventi inseriti** in DB tramite `seed_additional_events.py`:
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
