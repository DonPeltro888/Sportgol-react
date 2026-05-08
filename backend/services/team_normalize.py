"""
Normalizzazione nomi squadre + leghe per deduplica.
Combina suffisso/prefisso strip + mapping manuale per top club europei.
"""
import re
import unicodedata
from typing import Optional

# ─── Mapping manuale (nomi normalizzati canonici) ───────────────────────────
# Tutti i lookup sono in lowercase senza accenti.
MANUAL_TEAM_MAP = {
    # Serie A
    "ac milan": "milan",
    "internazionale": "inter",
    "inter milan": "inter",
    "fc internazionale milano": "inter",
    "ssc napoli": "napoli",
    "as roma": "roma",
    "ss lazio": "lazio",
    "atalanta bc": "atalanta",
    "udinese calcio": "udinese",
    "torino fc": "torino",
    "ac fiorentina": "fiorentina",
    "fiorentina ac": "fiorentina",
    "bologna fc 1909": "bologna",
    "bologna fc": "bologna",
    "us sassuolo": "sassuolo",
    "us lecce": "lecce",
    "us cremonese": "cremonese",
    "genoa cfc": "genoa",
    "como 1907": "como",
    "como calcio": "como",
    "venezia fc": "venezia",
    "ac monza": "monza",
    "hellas verona": "verona",
    "verona fc": "verona",
    "parma calcio": "parma",
    "parma calcio 1913": "parma",
    "cagliari calcio": "cagliari",
    "empoli fc": "empoli",
    "ac pisa 1909": "pisa",
    "pisa sc": "pisa",
    "juventus fc": "juventus",
    # Premier League
    "arsenal fc": "arsenal",
    "chelsea fc": "chelsea",
    "manchester united fc": "manchester united",
    "manchester united": "manchester united",
    "manchester utd": "manchester united",
    "man united": "manchester united",
    "man utd": "manchester united",
    "manchester city fc": "manchester city",
    "manchester city": "manchester city",
    "man city": "manchester city",
    "liverpool fc": "liverpool",
    "tottenham hotspur": "tottenham",
    "tottenham hotspur fc": "tottenham",
    "newcastle united fc": "newcastle united",
    "newcastle united": "newcastle united",
    "newcastle utd": "newcastle united",
    "newcastle": "newcastle united",
    "aston villa fc": "aston villa",
    "west ham united": "west ham",
    "west ham united fc": "west ham",
    "brighton & hove albion": "brighton",
    "brighton hove albion": "brighton",
    "brighton  hove albion fc": "brighton",
    "brighton  hove albion": "brighton",
    "wolverhampton wanderers": "wolverhampton",
    "wolverhampton wanderers fc": "wolverhampton",
    "wolves": "wolverhampton",
    "afc bournemouth": "bournemouth",
    "leicester city fc": "leicester city",
    "leicester city": "leicester city",
    "fulham fc": "fulham",
    "everton fc": "everton",
    "crystal palace fc": "crystal palace",
    "nottingham forest fc": "nottingham forest",
    "nottingham forest": "nottingham forest",
    "nottingham": "nottingham forest",
    "burnley fc": "burnley",
    "leeds united": "leeds",
    "leeds united fc": "leeds",
    "leeds": "leeds",
    "sunderland afc": "sunderland",
    "sheffield united": "sheffield united",
    "sheffield united fc": "sheffield united",
    "luton town": "luton",
    "luton town fc": "luton",
    "brentford fc": "brentford",
    # La Liga
    "real madrid cf": "real madrid",
    "fc barcelona": "barcelona",
    "atletico madrid": "atletico madrid",
    "atletico de madrid": "atletico madrid",
    "club atletico de madrid": "atletico madrid",
    "atl madrid": "atletico madrid",
    "atl. madrid": "atletico madrid",
    "atletico": "atletico madrid",
    "athletic club": "athletic bilbao",
    "athletic bilbao": "athletic bilbao",
    "ath bilbao": "athletic bilbao",
    "ath. bilbao": "athletic bilbao",
    "athletic": "athletic bilbao",
    "real sociedad de futbol": "real sociedad",
    "real betis balompie": "real betis",
    "real betis": "real betis",
    "betis": "real betis",
    "valencia cf": "valencia",
    "sevilla fc": "sevilla",
    "villarreal cf": "villarreal",
    "ca osasuna": "osasuna",
    "rcd mallorca": "mallorca",
    "rcd espanyol": "espanyol",
    "rcd espanyol de barcelona": "espanyol",
    "espanyol de barcelona": "espanyol",
    "ud las palmas": "las palmas",
    "deportivo alaves": "alaves",
    "deportivo alaves sad": "alaves",
    "rayo vallecano": "rayo vallecano",
    "rayo vallecano de madrid": "rayo vallecano",
    "girona fc": "girona",
    "celta de vigo": "celta vigo",
    "rc celta": "celta vigo",
    "rc celta de vigo": "celta vigo",
    "real oviedo": "oviedo",
    "oviedo": "oviedo",
    "elche cf": "elche",
    "levante ud": "levante",
    "real valladolid": "valladolid",
    "ud almeria": "almeria",
    "cadiz cf": "cadiz",
    # Bundesliga
    "fc bayern munchen": "bayern munich",
    "fc bayern muenchen": "bayern munich",
    "bayern muenchen": "bayern munich",
    "bayern munchen": "bayern munich",
    "borussia dortmund": "borussia dortmund",
    "bvb": "borussia dortmund",
    "dortmund": "borussia dortmund",
    "rb leipzig": "rb leipzig",
    "bayer 04 leverkusen": "leverkusen",
    "bayer leverkusen": "leverkusen",
    "1 fsv mainz 05": "mainz",
    "fsv mainz 05": "mainz",
    "mainz 05": "mainz",
    "borussia monchengladbach": "borussia monchengladbach",
    "borussia mgladbach": "borussia monchengladbach",
    "b. monchengladbach": "borussia monchengladbach",
    "b monchengladbach": "borussia monchengladbach",
    "monchengladbach": "borussia monchengladbach",
    "mgladbach": "borussia monchengladbach",
    "vfb stuttgart": "stuttgart",
    "tsg hoffenheim": "hoffenheim",
    "tsg 1899 hoffenheim": "hoffenheim",
    "1 fc heidenheim": "heidenheim",
    "1 fc heidenheim 1846": "heidenheim",
    "1 fc union berlin": "union berlin",
    "1 fc koln": "koln",
    "1 fc nurnberg": "nurnberg",
    "fc augsburg": "augsburg",
    "sc freiburg": "freiburg",
    "vfl wolfsburg": "wolfsburg",
    "eintracht frankfurt": "eintracht frankfurt",
    "werder bremen": "werder bremen",
    "sv werder bremen": "werder bremen",
    "fc st pauli": "st pauli",
    "st pauli": "st pauli",
    # Ligue 1
    "paris saint-germain": "paris saint-germain",
    "paris saint germain": "paris saint-germain",
    "psg": "paris saint-germain",
    "olympique lyonnais": "lyon",
    "lyon": "lyon",
    "olympique de marseille": "marseille",
    "olympique marseille": "marseille",
    "as monaco": "monaco",
    "lille osc": "lille",
    "stade rennais": "rennes",
    "ogc nice": "nice",
    "rc lens": "lens",
    "racing club de lens": "lens",
    "rc strasbourg alsace": "strasbourg",
    "fc nantes": "nantes",
    "stade brestois 29": "brest",
    "angers sco": "angers",
    "sco angers": "angers",
    "aj auxerre": "auxerre",
    "ac ajaccio": "ajaccio",
    "le havre ac": "le havre",
    "fc lorient": "lorient",
    "ea guingamp": "guingamp",
    "stade de reims": "reims",
    "fc metz": "metz",
    "montpellier hsc": "montpellier",
    "toulouse fc": "toulouse",
    "fc nantes football": "nantes",
    "paris fc": "paris fc",
    # Other top
    "ajax amsterdam": "ajax",
    "afc ajax": "ajax",
    "psv eindhoven": "psv",
    "feyenoord rotterdam": "feyenoord",
    "fc porto": "porto",
    "sl benfica": "benfica",
    "sporting cp": "sporting",
    "sc braga": "braga",
    "sporting braga": "braga",
    "braga": "braga",
    "sporting clube de portugal": "sporting",
    "celtic fc": "celtic",
    "rangers fc": "rangers",
    "galatasaray sk": "galatasaray",
    "fenerbahce sk": "fenerbahce",
    "besiktas jk": "besiktas",
    # Special: Milan teams - "Milan" alone refers to AC Milan
    "milan": "milan",
}

MANUAL_LEAGUE_MAP = {
    "italian serie a": "serie a",
    "campionato italiano": "serie a",
    "serie a tim": "serie a",
    "serie a italia": "serie a",
    "english premier league": "premier league",
    "premier league english": "premier league",
    "epl": "premier league",
    "primera division": "la liga",
    "laliga": "la liga",
    "la liga ea sports": "la liga",
    "la liga santander": "la liga",
    "german bundesliga": "bundesliga",
    "1 bundesliga": "bundesliga",
    "1. bundesliga": "bundesliga",
    "bundesliga 1": "bundesliga",
    "french ligue 1": "ligue 1",
    "ligue 1 uber eats": "ligue 1",
    "ligue 1 mcdonalds": "ligue 1",
    "uefa champions league": "champions league",
    "uefa europa league": "europa league",
    "uefa europa conference league": "conference league",
    "europa conference league": "conference league",
    "coppa italia frecciarossa": "coppa italia",
    "fa cup": "fa cup",
    "supercoppa italiana": "supercoppa italiana",
    "trofeo padre champagnat": "trofeo padre champagnat",
}

# Suffissi/prefissi da rimuovere (ordine importante: fuzzy match)
SUFFIX_TOKENS = [
    "football club", "futbol club", "calcio fc", "fussball club",
    "sport club", "athletic club",
    "fc", "ac", "sc", "ssc", "asd", "us", "ss", "as", "ud", "rc", "rcd",
    "cf", "ca", "fk", "bk", "fk", "sk", "sv", "vfl", "vfb", "tsg",
    "afc", "ogc", "psg", "rb", "calcio", "football", "fussball",
]
PREFIX_TOKENS = [
    "fc", "ac", "acf", "as", "us", "ss", "ssc", "ud", "rc", "rcd", "cf", "ca",
    "fk", "bk", "sk", "sv", "vfl", "vfb", "tsg", "afc", "ogc", "rb", "asd",
]


def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def _normalize_basic(name: str) -> str:
    if not name:
        return ""
    s = _strip_accents(name).lower().strip()
    # Replace special chars with space, collapse spaces
    s = re.sub(r"[\.\-_/]", " ", s)
    s = re.sub(r"[^\w\s&]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def normalize_team(name: str) -> str:
    """Restituisce nome canonico normalizzato per dedup."""
    if not name:
        return ""
    s = _normalize_basic(name)

    # 1. Lookup manuale completo prima
    if s in MANUAL_TEAM_MAP:
        return MANUAL_TEAM_MAP[s]

    # 2. Strip suffissi (loop fino a stabilità)
    tokens = s.split()
    changed = True
    while changed and len(tokens) > 1:
        changed = False
        for suffix in SUFFIX_TOKENS:
            sufx = suffix.split()
            if len(tokens) > len(sufx) and tokens[-len(sufx):] == sufx:
                tokens = tokens[:-len(sufx)]
                changed = True
                break
        # Strip trailing pure numeric (years) e.g. "1909", "1913"
        if tokens and re.match(r"^\d{4}$", tokens[-1]):
            tokens = tokens[:-1]
            changed = True

    # 3. Strip prefissi
    while tokens and len(tokens) > 1 and tokens[0] in PREFIX_TOKENS:
        tokens = tokens[1:]
    # Strip prefixed pure numeric "1 fc heidenheim"
    if tokens and re.match(r"^\d$", tokens[0]) and len(tokens) > 1:
        tokens = tokens[1:]

    s2 = " ".join(tokens).strip()
    if not s2:
        s2 = s
    # Re-lookup dopo normalizzazione
    if s2 in MANUAL_TEAM_MAP:
        return MANUAL_TEAM_MAP[s2]
    return s2


def normalize_league(name: str) -> str:
    if not name:
        return ""
    s = _normalize_basic(name)
    if s in MANUAL_LEAGUE_MAP:
        return MANUAL_LEAGUE_MAP[s]
    # Strip "italian/english/german/spanish/french" prefix
    tokens = s.split()
    nationality_prefix = {"italian", "english", "german", "spanish", "french", "portuguese", "dutch", "belgian"}
    if tokens and tokens[0] in nationality_prefix and len(tokens) > 1:
        tokens = tokens[1:]
    s2 = " ".join(tokens).strip()
    if s2 in MANUAL_LEAGUE_MAP:
        return MANUAL_LEAGUE_MAP[s2]
    return s2


def _parse_date_ymd(date_field) -> Optional[str]:
    """Estrae YYYY-MM-DD da sort_date (ISO), date string o objects."""
    if not date_field:
        return None
    if hasattr(date_field, "isoformat"):
        return date_field.isoformat()[:10]
    s = str(date_field)
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return None


def event_dedup_key(home: str, away: str, date_field) -> Optional[str]:
    """Chiave univoca per match: (home_norm, away_norm, yyyy-mm-dd)."""
    h = normalize_team(home)
    a = normalize_team(away)
    d = _parse_date_ymd(date_field)
    if not (h and a and d):
        return None
    return f"{h}|{a}|{d}"
