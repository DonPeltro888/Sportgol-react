# CWV Automation Center — Next Steps (parcheggiato 2026-05-08)

## Contesto
Il modulo CWV oggi ha **1 vero auto-fix su 12** (CWV-5 cron). Gli altri 11 generano snippet ma richiedono il dev di ticketgol per applicarli (copia-incolla nel repo).

## Bilancio onesto dei 12 fix
| Fix | Tipo reale |
|-----|-----------|
| CWV-1 Hero WebP/AVIF | 🟡 SEMI-auto: converte i file ma serve `<picture>` lato frontend |
| CWV-2 Lazy admin | 🔴 Manual (snippet App.js) |
| CWV-3 img width/height | 🔴 Manual |
| CWV-4 Font preload | 🔴 Manual |
| CWV-5 PageSpeed cron | ✅ VERO auto (parte da solo dopo install) |
| CWV-6 SSR JSON-LD | 🟡 SEMI-auto: route già pronta ma serve config nginx |
| CWV-7 lazy below-fold | 🔴 Manual |
| CWV-8 Preconnect | 🔴 Manual |
| CWV-9 Defer scripts | 🔴 Manual |
| CWV-10 aspect-ratio | 🔴 Manual |
| CWV-11 Critical CSS | 🔴 FALSO auto (oggi mostra solo un messaggio — va integrato `critters`) |
| CWV-12 Service Worker | 🔴 Manual |

## Domanda dell'utente
"Quando esporto il modulo SEO su ticketgol, le azioni Core Web Vitals possono essere applicate dal tool stesso o serve sempre un dev?"

## 4 opzioni proposte (da scegliere quando si riprende)

### A) GitHub PR Bot (1 giornata) — CONSIGLIATA
Il tool apre un Pull Request automatico sul repo ticketgol con il fix applicato. Il dev fa solo Merge.
- ✅ Audit trail Git nativo, sicuro
- ⚠️ Richiede: GitHub token + repo name ticketgol

### B) SSH Direct Apply (1 giornata)
Il tool si connette via SSH al server ticketgol e modifica i file direttamente.
- ✅ Fix in 5 secondi, zero attriti
- ❌ Pericoloso senza staging
- ⚠️ Richiede: chiave SSH + path repo

### C) Build-time plugin (2 giornate) — PIÙ ELEGANTE
Webpack/Vite plugin custom che applica CWV-3/4/7/8/9/10 a ogni `npm run build`.
- ✅ Invisibile al dev dopo setup
- ⚠️ Stack-specific: variante React/Vite vs Laravel/Blade

### D) ZIP scaricabile + fix CWV-11 reale (mezza giornata) — QUICK WIN
Endpoint `POST /apply-patch-zip` che impacchetta tutti gli snippet in uno zip pronto per `unzip + git commit`. + integrare `critters` per CWV-11 vero.
- ✅ Veloce, no integrazione esterna
- ⚠️ Dev deve ancora committare manualmente

## Domanda aperta
Stack ticketgol.com: **React+Node** o **Laravel/Blade (PHP)**? (cambia opzione C)

## Quando riprendere
Dopo P1 SERP gap analysis vs SeatPick/StubHub. Priorità rivedibile in base a urgenza performance ticketgol.
