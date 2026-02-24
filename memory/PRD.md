# GOLEVENTS Clone - Product Requirements Document

## Original Problem Statement
Clone del sito web www.golevents.com - un portale per l'acquisto di biglietti per eventi sportivi (principalmente calcio).

## Core Requirements (Completed)
1. **Homepage** con griglia di eventi e ricerca in tempo reale
2. **Pagine di dettaglio** per ogni evento
3. **Pagine per campionati/coppe** che elencano squadre o eventi
4. **Pagine per squadre** con tutti gli eventi della squadra
5. **Menu di navigazione** con tutte le categorie espandibili
6. **Ordinamento eventi** per data (dal più prossimo)
7. **Tag cliccabili** sugli eventi per navigare alle squadre
8. **Prefisso "Biglietti"** nei titoli delle pagine squadra

## Architecture

### Frontend (React + TailwindCSS + Shadcn UI)
```
/app/frontend/src/
├── components/
│   ├── Header.jsx        # Menu desktop/mobile espandibile
│   ├── Footer.jsx
│   ├── EventCard.jsx
│   ├── EventsGrid.jsx
│   ├── HeroSearch.jsx
│   └── CategoriesSection.jsx
├── pages/
│   ├── Home.jsx          # Homepage con ricerca
│   ├── EventDetail.jsx   # Dettaglio evento
│   ├── LeaguePage.jsx    # Pagina campionato/coppa
│   └── TeamPage.jsx      # Pagina squadra
└── services/
    └── api.js            # API client
```

### Backend (FastAPI + MongoDB)
```
/app/backend/
├── routes/
│   ├── events.py         # CRUD eventi + ordinamento
│   ├── categories.py     # Categorie con eventi
│   └── search.py         # Ricerca in tempo reale
├── models/
├── database.py
├── seed_data.py          # ~170 partite reali
└── server.py
```

### Database Schema
- **events**: `{ title, categories[], date, sort_date, location, stadium, price_range, league, imageUrl, featured }`
- **categories**: `{ name, slug, description, event_count }`

## Key API Endpoints
- `GET /api/events` - Lista eventi (paginata, ordinata per sort_date)
- `GET /api/events/:id` - Singolo evento
- `GET /api/categories` - Tutte le categorie
- `GET /api/categories/:slug` - Categoria con eventi
- `GET /api/search?q=` - Ricerca in tempo reale

## Data Content
- **7 Campionati**: Serie A, Premier League, La Liga, Bundesliga, Liga Portugal, Ligue 1, Super Lig
- **6 Coppe**: Champions League, Europa League, Coppa Italia, Copa del Rey, FA Cup, DFB Pokal
- **~170 partite** con date da Febbraio a Maggio 2026
- **91 squadre** con descrizioni

## Completed Features (Session Date: Dec 2025)
- [x] Clone full-stack funzionante di golevents.com
- [x] Menu desktop espandibile con LEAGUES e CUPS
- [x] Squadre visualizzate sotto ogni campionato nel menu
- [x] Menu mobile con stessa struttura
- [x] Ordinamento eventi per data su tutte le pagine (sort_date field)
- [x] Ricerca in tempo reale
- [x] Tag squadre cliccabili
- [x] Pagine dinamiche per eventi, squadre e campionati/coppe
- [x] Design moderno con gradient e animazioni

## Known Issues / Placeholders
- Le sezioni "Details" e "FAQ" nella pagina EventDetail.jsx contengono testo placeholder

## Future Enhancements (Backlog)
- [ ] Popolare le sezioni Details/FAQ con contenuti reali
- [ ] Sistema di autenticazione utente
- [ ] Carrello e checkout per acquisto biglietti
- [ ] Filtri avanzati per data/prezzo/categoria
- [ ] Notifiche per nuovi eventi
