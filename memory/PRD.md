# GOLEVENTS Clone - Product Requirements Document

## Original Problem Statement
Clone del sito web www.golevents.com - un portale per l'acquisto di biglietti per eventi sportivi (principalmente calcio).

## Core Features (Completed)

### Public Website
1. **Homepage** con griglia eventi e ricerca in tempo reale
2. **Pagine di dettaglio** per ogni evento
3. **Pagine per campionati/coppe** che elencano squadre o eventi
4. **Pagine per squadre** con tutti gli eventi della squadra
5. **Menu di navigazione** con tutte le categorie espandibili
6. **Ordinamento eventi** per data (dal più prossimo)
7. **Tag cliccabili** sugli eventi per navigare alle squadre

### Admin Panel (`/admin`)
1. **Autenticazione** semplice (admin/golevents2024)
2. **Dashboard** con statistiche sistema
3. **Gestione Eventi** con:
   - Supporto multilingua (IT, ES, EN)
   - Categorie biglietti con prezzi e note
   - Impostazioni SEO per ogni evento
4. **Gestione Categorie Menu** (campionati, coppe, squadre)
5. **Gestione Pagine & Testi** con editor rich text (React Quill)
6. **Gestione SEO** (meta tag, og:image, canonical)
7. **Gestione Traduzioni** per tutti i testi
8. **Impostazioni Sito** (logo, contatti, social, footer)

## Architecture

### Frontend (React + TailwindCSS + Shadcn UI)
```
/app/frontend/src/
├── components/
│   ├── admin/
│   │   └── AdminLayout.jsx
│   ├── Header.jsx
│   ├── Footer.jsx
│   └── ui/
├── contexts/
│   └── AdminAuthContext.jsx
├── pages/
│   ├── admin/
│   │   ├── AdminLogin.jsx
│   │   ├── AdminDashboard.jsx
│   │   ├── AdminEvents.jsx
│   │   ├── AdminCategories.jsx
│   │   ├── AdminPages.jsx
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
│   └── admin_content.py
├── models/
│   └── admin.py
├── database.py
├── seed_data.py
└── server.py
```

### Database Collections
- **events**: Eventi con supporto multilingua e categorie biglietti
- **categories**: Categorie/squadre esistenti
- **menu_categories**: Categorie per il menu (campionati, coppe)
- **page_content**: Contenuti pagine multilingua
- **seo_settings**: Impostazioni SEO per pagina
- **translations**: Traduzioni generali
- **site_settings**: Configurazioni sito
- **admin_logs**: Log azioni admin

## Key API Endpoints

### Public
- `GET /api/events` - Lista eventi
- `GET /api/events/:id` - Singolo evento
- `GET /api/categories` - Categorie
- `GET /api/search?q=` - Ricerca
- `GET /api/admin/public/content/:page` - Contenuti pagina
- `GET /api/admin/public/seo/:page` - SEO pagina
- `GET /api/admin/public/translations` - Traduzioni

### Admin (richiede token)
- `POST /api/admin/login` - Login
- `GET /api/admin/stats` - Statistiche
- `CRUD /api/admin/events` - Gestione eventi
- `CRUD /api/admin/menu-categories` - Categorie menu
- `CRUD /api/admin/page-content` - Contenuti
- `CRUD /api/admin/seo` - SEO
- `CRUD /api/admin/translations` - Traduzioni
- `PUT /api/admin/settings` - Impostazioni

## Admin Credentials
- **URL**: `/admin/login`
- **Username**: `admin`
- **Password**: `golevents2024`

## Data Content
- **7 Campionati**: Serie A, Premier League, La Liga, Bundesliga, Liga Portugal, Ligue 1, Super Lig
- **6 Coppe**: Champions League, Europa League, Coppa Italia, Copa del Rey, FA Cup, DFB Pokal
- **~170 partite** con date da Febbraio a Maggio 2026
- **91 squadre** con descrizioni

## Session Completed (Dec 2025)
- [x] Pannello admin completo con autenticazione
- [x] Gestione eventi multilingua (IT/ES/EN)
- [x] Categorie biglietti con prezzi e note
- [x] Editor rich text per contenuti
- [x] Gestione SEO (title, description, keywords, og:image)
- [x] Sistema traduzioni
- [x] Impostazioni sito globali

## Known Issues / TODO
- [ ] Integrare contenuti multilingua nel frontend pubblico
- [ ] Sitemap XML automatica
- [ ] Schema.org markup per eventi
- [ ] Upload immagini (attualmente solo URL)

## Future Enhancements
- Sistema di autenticazione utenti
- Carrello e checkout
- Integrazione pagamenti (Stripe)
- Notifiche email
