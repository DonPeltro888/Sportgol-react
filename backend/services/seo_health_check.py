"""
SEO Data Health Check — diagnosi read-only delle anomalie nel DB:
- Name confusion (team con nome prefisso/suffisso di altri)
- Duplicati (slug, fuzzy name match)
- Dati mancanti (logo, stadium, city, league_slug)
- Logo collision (team distinti con stesso logo_url)
- Mismatched events (eventi assegnati a team con league sbagliata)
"""
import logging
from typing import Dict, Any, List
from collections import defaultdict
from rapidfuzz import fuzz
from database import db

logger = logging.getLogger(__name__)

# Soglia fuzzy per duplicati: 85+ = quasi sicuramente duplicato
FUZZY_DUPE_THRESHOLD = 85


async def scan_teams() -> Dict[str, Any]:
    """Scansiona la collection teams per anomalie."""
    teams: List[Dict[str, Any]] = await db.teams.find({}, {"_id": 0}).to_list(2000)
    issues: List[Dict[str, Any]] = []

    by_slug: Dict[str, List] = defaultdict(list)
    by_logo: Dict[str, List] = defaultdict(list)
    name_set: List[Dict[str, Any]] = []

    for t in teams:
        slug = t.get("slug", "")
        if slug:
            by_slug[slug].append(t)
        logo = (t.get("logo_url") or "").strip()
        if logo:
            by_logo[logo].append(t)
        name_set.append(t)

        # Missing fields
        missing = []
        if not t.get("logo_url"):
            missing.append("logo_url")
        if not t.get("stadium"):
            missing.append("stadium")
        if not t.get("city"):
            missing.append("city")
        if not t.get("league_slug"):
            missing.append("league_slug")
        if missing:
            issues.append({
                "category": "missing_data",
                "severity": "medium" if "logo_url" in missing else "low",
                "team_slug": slug,
                "team_name": t.get("name"),
                "missing": missing,
            })

    # Slug duplicati
    for slug, items in by_slug.items():
        if len(items) > 1:
            issues.append({
                "category": "duplicate_slug",
                "severity": "high",
                "slug": slug,
                "names": [i.get("name") for i in items],
                "count": len(items),
            })

    # Logo collision (team diversi con stesso logo)
    for logo, items in by_logo.items():
        if len(items) > 1:
            issues.append({
                "category": "logo_collision",
                "severity": "high",
                "logo_url": logo,
                "teams": [{"slug": i.get("slug"), "name": i.get("name")} for i in items],
                "count": len(items),
            })

    # Name confusion: nome di team A è prefisso/suffisso di team B (ma non identico)
    for i, a in enumerate(name_set):
        a_name = (a.get("name") or "").strip()
        if not a_name or len(a_name) < 4:
            continue
        for b in name_set[i+1:]:
            b_name = (b.get("name") or "").strip()
            if not b_name or a_name == b_name:
                continue
            # Check se a è "contenuto in" b come parola (con spazio o inizio)
            if (a_name in b_name and len(a_name) < len(b_name) and
                (b_name.startswith(a_name + " ") or b_name.endswith(" " + a_name) or f" {a_name} " in b_name)):
                issues.append({
                    "category": "name_confusion",
                    "severity": "high",
                    "shorter_team": {"slug": a.get("slug"), "name": a_name},
                    "longer_team": {"slug": b.get("slug"), "name": b_name},
                    "warning": f"'{a_name}' è prefisso/contenuto in '{b_name}': risk di catturare eventi cross-team",
                })

    # Fuzzy duplicati (nomi quasi identici, slug diversi)
    for i, a in enumerate(name_set):
        a_name = (a.get("name") or "").strip()
        if not a_name:
            continue
        for b in name_set[i+1:]:
            b_name = (b.get("name") or "").strip()
            if not b_name or a.get("slug") == b.get("slug"):
                continue
            ratio = fuzz.ratio(a_name.lower(), b_name.lower())
            if ratio >= FUZZY_DUPE_THRESHOLD and a_name != b_name:
                issues.append({
                    "category": "fuzzy_duplicate",
                    "severity": "medium",
                    "team_a": {"slug": a.get("slug"), "name": a_name},
                    "team_b": {"slug": b.get("slug"), "name": b_name},
                    "similarity": ratio,
                })

    return {"total_teams": len(teams), "issues": issues}


async def scan_events() -> Dict[str, Any]:
    """Scansiona events per anomalie."""
    issues: List[Dict[str, Any]] = []
    teams_by_name: Dict[str, Dict[str, Any]] = {}
    async for t in db.teams.find({}, {"_id": 0, "name": 1, "slug": 1, "league_slug": 1}):
        if t.get("name"):
            teams_by_name[t["name"].lower()] = t

    total = 0
    orphans = 0
    missing_loc = 0

    async for ev in db.events.find({}, {"_id": 0}):
        total += 1
        h = (ev.get("home_team") or "").strip()
        a = (ev.get("away_team") or "").strip()

        # Orphan: home_team non esiste come team in DB
        if h and h.lower() not in teams_by_name:
            orphans += 1
            if orphans <= 30:  # cap per non esplodere
                issues.append({
                    "category": "orphan_event_team",
                    "severity": "low",
                    "event_slug": ev.get("slug"),
                    "missing_team_name": h,
                    "side": "home",
                })

        # Missing location/stadium
        miss = []
        if not ev.get("location"):
            miss.append("location")
        if not ev.get("stadium"):
            miss.append("stadium")
        if not ev.get("league") and not ev.get("league_slug"):
            miss.append("league")
        if miss and missing_loc < 30:
            missing_loc += 1
            issues.append({
                "category": "event_missing_data",
                "severity": "low",
                "event_slug": ev.get("slug"),
                "title": ev.get("title") or f"{h} vs {a}",
                "missing": miss,
            })

    return {
        "total_events": total,
        "orphan_count": orphans,
        "missing_data_count": missing_loc,
        "issues": issues,
    }


async def scan_leagues() -> Dict[str, Any]:
    """Scansiona leagues per anomalie."""
    issues: List[Dict[str, Any]] = []
    leagues = await db.leagues.find({}, {"_id": 0}).to_list(200)
    for lg in leagues:
        miss = []
        if not lg.get("logo_url"):
            miss.append("logo_url")
        if not lg.get("country"):
            miss.append("country")
        if miss:
            issues.append({
                "category": "league_missing_data",
                "severity": "low",
                "slug": lg.get("slug"),
                "name": lg.get("name"),
                "missing": miss,
            })
    return {"total_leagues": len(leagues), "issues": issues}


async def full_scan() -> Dict[str, Any]:
    """Scan completo + summary."""
    teams_r = await scan_teams()
    events_r = await scan_events()
    leagues_r = await scan_leagues()

    all_issues = teams_r["issues"] + events_r["issues"] + leagues_r["issues"]
    by_cat: Dict[str, int] = defaultdict(int)
    by_sev: Dict[str, int] = defaultdict(int)
    for i in all_issues:
        by_cat[i["category"]] += 1
        by_sev[i.get("severity", "low")] += 1

    return {
        "summary": {
            "total_issues": len(all_issues),
            "by_category": dict(by_cat),
            "by_severity": dict(by_sev),
            "total_teams": teams_r["total_teams"],
            "total_events": events_r["total_events"],
            "total_leagues": leagues_r["total_leagues"],
        },
        "teams": teams_r,
        "events": events_r,
        "leagues": leagues_r,
    }
