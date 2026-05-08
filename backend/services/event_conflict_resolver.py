"""
Event Conflict Resolver — impedisce che lo stesso team giochi due partite nello stesso giorno.

Regola: nessun team (home o away) può apparire in più di un evento entro una window di ±12 ore.
Se conflitto rilevato, vince l'evento con la fonte più affidabile.

Trust hierarchy (descending):
  1. matchesio       — JSON ufficiale calendari (primario storico)
  2. apifootball     — API a pagamento, alta affidabilità
  3. espn            — API pubblica ESPN, copertura globale buona
  4. football_data   — football-data.org
  5. thesportsdb     — TheSportsDB (alcuni dati datati)
  6. openfootball    — OpenFootball GitHub (semi-statico)
  7. ai_perplexity   — AI gap detector (può allucinare → ULTIMO)
  8. unknown         — fonte non specificata

Usage:
    # Pre-insert check (per AI gap detector e tutti i sync)
    from services.event_conflict_resolver import is_safe_to_insert
    if not await is_safe_to_insert(event_doc):
        skip_insert()

    # Cleanup retroattivo
    from services.event_conflict_resolver import resolve_all_conflicts
    stats = await resolve_all_conflicts(dry_run=False)
"""
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from rapidfuzz import fuzz

from database import db

logger = logging.getLogger(__name__)

# ── Trust hierarchy (lower index = higher priority) ──────────────────────────
TRUST_ORDER: List[str] = [
    "matchesio",
    "apifootball",
    "espn",
    "football_data",
    "thesportsdb",
    "openfootball",
    "ai_perplexity",
    "unknown",
]


def _trust_index(source: Optional[str]) -> int:
    src = (source or "unknown").lower()
    if src in TRUST_ORDER:
        return TRUST_ORDER.index(src)
    return len(TRUST_ORDER)  # unknown sources go last


def _parse_iso_dt(s: Any) -> Optional[datetime]:
    if not s:
        return None
    if isinstance(s, datetime):
        return s if s.tzinfo else s.replace(tzinfo=timezone.utc)
    s = str(s)
    try:
        # accept "YYYY-MM-DDTHH:MM:SS" or with TZ
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        # try date-only
        try:
            return datetime.fromisoformat(s[:10]).replace(tzinfo=timezone.utc)
        except Exception:
            return None


def _team_eq(a: str, b: str, threshold: int = 88) -> bool:
    """Equality between two team names. Uses team_normalize canonical form first,
    then fuzzy ratio as fallback (handles 'Atl. Madrid' vs 'Atletico Madrid', 'Dortmund' vs 'Borussia Dortmund' etc)."""
    if not a or not b:
        return False
    a_s, b_s = a.strip().lower(), b.strip().lower()
    if a_s == b_s:
        return True
    try:
        from services.team_normalize import normalize_team as _norm
        na = (_norm(a) or "").strip().lower()
        nb = (_norm(b) or "").strip().lower()
        if na and nb and na == nb:
            return True
    except Exception:
        pass
    return fuzz.ratio(a_s, b_s) >= threshold


# ── Conflict detection ───────────────────────────────────────────────────────

async def find_team_conflicts(
    team_name: str,
    sort_date: str,
    *,
    exclude_event_id: Any = None,
    window_hours: int = 12,
) -> List[Dict[str, Any]]:
    """Trova eventi in DB dove `team_name` è impegnato entro ±window_hours da `sort_date`."""
    if not team_name or not sort_date:
        return []
    pivot = _parse_iso_dt(sort_date)
    if not pivot:
        return []
    lo = (pivot - timedelta(hours=window_hours)).isoformat().replace("+00:00", "")
    hi = (pivot + timedelta(hours=window_hours)).isoformat().replace("+00:00", "")
    # Compile exact-ish regex (anchored, escaped) for both home and away
    pat = f"^{re.escape(team_name.strip())}$"
    q: Dict[str, Any] = {
        "$or": [
            {"home_team": {"$regex": pat, "$options": "i"}},
            {"away_team": {"$regex": pat, "$options": "i"}},
        ],
        "sort_date": {"$gte": lo, "$lte": hi},
        "_dropped_conflict": {"$ne": True},
    }
    if exclude_event_id is not None:
        q["_id"] = {"$ne": exclude_event_id}
    docs = await db.events.find(
        q,
        {"_id": 1, "home_team": 1, "away_team": 1, "sort_date": 1, "league": 1, "source": 1, "slug": 1},
    ).to_list(20)
    # extra fuzzy filter (some teams have variant spellings stored)
    out: List[Dict[str, Any]] = []
    for d in docs:
        if _team_eq(d.get("home_team", ""), team_name) or _team_eq(d.get("away_team", ""), team_name):
            out.append(d)
    return out


async def is_safe_to_insert(event_doc: Dict[str, Any], *, window_hours: int = 12) -> Tuple[bool, str]:
    """
    Verifica che né home né away siano già impegnati nello stesso giorno (±window_hours).
    Se conflitto trovato, decide via trust hierarchy se questo evento può vincere.

    Ritorna (safe, reason). Se safe=False, l'evento NON va inserito.
    Se safe=True ma esiste un evento meno affidabile da rimuovere, viene MARCATO _dropped_conflict.
    """
    home = (event_doc.get("home_team") or "").strip()
    away = (event_doc.get("away_team") or "").strip()
    sd = event_doc.get("sort_date") or ""
    new_src = (event_doc.get("source") or "").lower()
    new_trust = _trust_index(new_src)

    if not home or not away or not sd:
        return True, "missing-fields-skip-check"

    # Check both home and away for conflicts
    conflicts: List[Dict[str, Any]] = []
    for t in (home, away):
        cs = await find_team_conflicts(t, sd, window_hours=window_hours)
        for c in cs:
            # ignore the exact same match (same teams + same date)
            if (_team_eq(c.get("home_team", ""), home) and _team_eq(c.get("away_team", ""), away)) or \
               (_team_eq(c.get("home_team", ""), away) and _team_eq(c.get("away_team", ""), home)):
                # same fixture from another sync — handled by upsert key, not a conflict
                continue
            conflicts.append(c)

    # dedupe by _id
    seen = set()
    unique: List[Dict[str, Any]] = []
    for c in conflicts:
        cid = c.get("_id")
        if cid and cid not in seen:
            seen.add(cid)
            unique.append(c)

    if not unique:
        return True, "no-conflict"

    # We have conflicts. Decide via trust.
    losers: List[Dict[str, Any]] = []
    blockers: List[Dict[str, Any]] = []
    for c in unique:
        c_trust = _trust_index((c.get("source") or "").lower())
        if c_trust > new_trust:
            losers.append(c)  # existing event is less trusted → drop it
        else:
            blockers.append(c)  # existing event is more trusted → block this insert

    if blockers:
        b = blockers[0]
        return False, (
            f"blocked-by-{(b.get('source') or 'unknown')}: "
            f"{b.get('home_team')} vs {b.get('away_team')} @ {b.get('sort_date','')[:16]}"
        )

    # All conflicts are losers → mark them as dropped
    if losers:
        loser_ids = [c["_id"] for c in losers]
        await db.events.update_many(
            {"_id": {"$in": loser_ids}},
            {"$set": {
                "_dropped_conflict": True,
                "_dropped_reason": f"conflict_with_{new_src or 'new'}_higher_trust",
                "_dropped_at": datetime.now(timezone.utc),
            }},
        )
        logger.info(
            f"ConflictResolver: dropped {len(loser_ids)} less-trusted events "
            f"to allow {new_src} {home} vs {away} @ {sd[:16]}"
        )
    return True, f"resolved-{len(losers)}-loser(s)"


# ── Retroactive cleanup ──────────────────────────────────────────────────────

async def resolve_all_conflicts(
    *, window_hours: int = 12, dry_run: bool = False, days_forward: int = 365
) -> Dict[str, Any]:
    """
    Scansiona TUTTI gli eventi futuri (entro days_forward), raggruppa per team+giorno,
    e per ogni gruppo con >1 evento applica trust hierarchy → marca i perdenti `_dropped_conflict`.
    Returns stats {scanned, conflicts_groups, dropped, kept, samples}.
    """
    today = datetime.now(timezone.utc)
    horizon = (today + timedelta(days=days_forward)).strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")

    # Index events by (team, day)
    cursor = db.events.find(
        {"sort_date": {"$gte": today_str, "$lte": f"{horizon}T23:59:59"},
         "_dropped_conflict": {"$ne": True}},
        {"_id": 1, "home_team": 1, "away_team": 1, "sort_date": 1, "league": 1,
         "source": 1, "slug": 1},
    )
    events: List[Dict[str, Any]] = await cursor.to_list(50000)

    by_team_day: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for ev in events:
        sd = ev.get("sort_date") or ""
        day = sd[:10]
        for role in ("home_team", "away_team"):
            t = (ev.get(role) or "").strip().lower()
            if not t or not day:
                continue
            by_team_day.setdefault((t, day), []).append(ev)

    dropped: List[Dict[str, Any]] = []
    kept: List[Dict[str, Any]] = []
    conflict_groups = 0
    samples: List[Dict[str, Any]] = []
    seen_dropped_ids = set()

    for (team, day), group in by_team_day.items():
        # dedupe events in group by _id
        unique = {ev["_id"]: ev for ev in group}.values()
        if len(unique) < 2:
            continue

        # Filter by window: only events truly within ±window_hours of each other
        sorted_evs = sorted(unique, key=lambda e: e.get("sort_date") or "")

        # find clusters that conflict (same team, ≤window_hours apart)
        clusters: List[List[Dict[str, Any]]] = []
        current: List[Dict[str, Any]] = []
        for ev in sorted_evs:
            if not current:
                current = [ev]
                continue
            t_prev = _parse_iso_dt(current[-1].get("sort_date"))
            t_curr = _parse_iso_dt(ev.get("sort_date"))
            if t_prev and t_curr and abs((t_curr - t_prev).total_seconds()) <= window_hours * 3600:
                current.append(ev)
            else:
                if len(current) > 1:
                    clusters.append(current)
                current = [ev]
        if len(current) > 1:
            clusters.append(current)

        for cluster in clusters:
            # Skip if all events are the SAME fixture (fuzzy-match home+away pair)
            def _same_fixture(a, b):
                ah, aa = (a.get("home_team") or "").strip(), (a.get("away_team") or "").strip()
                bh, ba = (b.get("home_team") or "").strip(), (b.get("away_team") or "").strip()
                # direct or swapped match
                if (_team_eq(ah, bh) and _team_eq(aa, ba)) or (_team_eq(ah, ba) and _team_eq(aa, bh)):
                    return True
                return False
            base = cluster[0]
            if all(_same_fixture(base, e) for e in cluster[1:]):
                # All same fixture across sources → keep best source, drop the rest as duplicates
                cluster_sorted = sorted(
                    cluster,
                    key=lambda e: (_trust_index((e.get("source") or "").lower()), e.get("sort_date") or "")
                )
                winner = cluster_sorted[0]
                losers_local = cluster_sorted[1:]
                if not losers_local:
                    continue
                conflict_groups += 1
                kept.append({"team": team, "day": day, "winner": _summary(winner), "kind": "duplicate"})
                if len(samples) < 20:
                    samples.append({
                        "team": team, "day": day, "kind": "duplicate-fixture",
                        "winner": _summary(winner),
                        "losers": [_summary(l) for l in losers_local],
                    })
                for l in losers_local:
                    if l["_id"] in seen_dropped_ids:
                        continue
                    seen_dropped_ids.add(l["_id"])
                    dropped.append({"team": team, "day": day, "loser": _summary(l), "winner_source": winner.get("source"), "kind": "duplicate"})
                    if not dry_run:
                        await db.events.update_one(
                            {"_id": l["_id"]},
                            {"$set": {
                                "_dropped_conflict": True,
                                "_dropped_reason": f"duplicate_fixture_winner_{winner.get('source','?')}",
                                "_dropped_at": datetime.now(timezone.utc),
                            }},
                        )
                continue

            conflict_groups += 1

            # Pick winner: lowest trust index (= highest priority)
            cluster_sorted = sorted(
                cluster,
                key=lambda e: (_trust_index((e.get("source") or "").lower()), e.get("sort_date") or "")
            )
            winner = cluster_sorted[0]
            losers_local = cluster_sorted[1:]
            kept.append({"team": team, "day": day, "winner": _summary(winner), "kind": "conflict"})
            if len(samples) < 20:
                samples.append({
                    "team": team,
                    "day": day,
                    "kind": "team-double-booking",
                    "winner": _summary(winner),
                    "losers": [_summary(l) for l in losers_local],
                })
            for l in losers_local:
                if l["_id"] in seen_dropped_ids:
                    continue
                seen_dropped_ids.add(l["_id"])
                dropped.append({
                    "team": team,
                    "day": day,
                    "loser": _summary(l),
                    "winner_source": winner.get("source"),
                    "kind": "conflict",
                })
                if not dry_run:
                    await db.events.update_one(
                        {"_id": l["_id"]},
                        {"$set": {
                            "_dropped_conflict": True,
                            "_dropped_reason": f"conflict_team_{team}_{day}_winner_{winner.get('source','?')}",
                            "_dropped_at": datetime.now(timezone.utc),
                        }},
                    )

    return {
        "scanned_events": len(events),
        "conflict_groups": conflict_groups,
        "dropped": len(dropped),
        "kept": len(kept),
        "samples": samples[:20],
        "dry_run": dry_run,
    }


def _summary(ev: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(ev.get("_id")),
        "fixture": f"{ev.get('home_team')} vs {ev.get('away_team')}",
        "sort_date": ev.get("sort_date"),
        "league": ev.get("league"),
        "source": ev.get("source"),
        "slug": ev.get("slug"),
    }


# ── League name canonicalization (fix "COPPA ITALIA" vs "Coppa Italia") ──────

async def canonicalize_league_names(*, dry_run: bool = False) -> Dict[str, int]:
    """
    Per ogni evento, riscrive `league` in title-case se è all-uppercase.
    Esempi: "COPPA ITALIA" → "Coppa Italia", "FA CUP" → "Fa Cup",
    "FIFA WORLD CUP 2026" → "Fifa World Cup 2026".
    Aggiorna il `league_slug` se mancante o disallineato.
    """
    import unicodedata
    def slugify(s: str) -> str:
        s = unicodedata.normalize("NFKD", s or "")
        s = "".join(c for c in s if not unicodedata.combining(c))
        s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
        return s[:80]

    updated = 0
    cursor = db.events.find({}, {"_id": 1, "league": 1, "league_slug": 1})
    async for ev in cursor:
        lg = (ev.get("league") or "").strip()
        if not lg:
            continue
        canonical = None
        if lg.isupper():
            canonical = lg.title()
        new_slug = slugify(canonical or lg)
        cur_slug = (ev.get("league_slug") or "").strip()
        upd: Dict[str, Any] = {}
        if canonical and canonical != lg:
            upd["league"] = canonical
        if new_slug and new_slug != cur_slug:
            upd["league_slug"] = new_slug
        if upd:
            if not dry_run:
                await db.events.update_one({"_id": ev["_id"]}, {"$set": upd})
            updated += 1
    return {"events_canonicalized": updated, "dry_run": dry_run}
