# Test Credentials - Golevents Clone

## Admin Panel
- **URL Login**: https://sports-events-2.preview.emergentagent.com/admin/login
- **Username**: `admin`
- **Password**: `golevents2024`

## API Endpoints
- **Backend URL**: from `/app/frontend/.env` REACT_APP_BACKEND_URL
- **Login endpoint**: `POST /api/admin/login` con body `{"username":"admin","password":"golevents2024"}`
- **Token usage**: `Authorization: Bearer {token}` (24h TTL, in-memory)

## Source di Dati
- **matchesio.com**: JSON pubblici, no auth
  - Pattern URL: `https://www.matchesio.com/it/competition/{slug}/export/json/`
  - 13 competizioni disponibili
- **MongoDB**: locale, credenziali in `/app/backend/.env`

## Sync Manuale
- `POST {API}/api/admin/sync/matchesio?replace_all=true` (con auth)
- `GET {API}/api/admin/sync/logs?limit=10` (con auth)

## Cron Schedulato
- AsyncIOScheduler attivo, sync ogni 6h: 00:00, 06:00, 12:00, 18:00 UTC
