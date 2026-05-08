"""
Tests for event_conflict_resolver: trust hierarchy + same-fixture detection.
"""
import pytest
from services.event_conflict_resolver import _trust_index, _team_eq, TRUST_ORDER


def test_trust_order_priorities():
    assert _trust_index("matchesio") < _trust_index("apifootball")
    assert _trust_index("apifootball") < _trust_index("espn")
    assert _trust_index("espn") < _trust_index("ai_perplexity")
    assert _trust_index("ai_perplexity") < _trust_index("unknown")
    assert _trust_index(None) >= _trust_index("ai_perplexity")
    assert _trust_index("") >= _trust_index("ai_perplexity")
    assert _trust_index("nonsense_source") == len(TRUST_ORDER)


def test_team_eq_basic():
    assert _team_eq("Inter", "Inter")
    assert _team_eq("inter", "INTER")
    assert _team_eq("Inter", "Inter Miami") is False  # explicit fuzzy threshold guard


def test_team_eq_normalize_aliases():
    # Aliases via team_normalize
    assert _team_eq("Atl. Madrid", "Atletico Madrid")
    assert _team_eq("Ath Bilbao", "Athletic Bilbao")
    assert _team_eq("Dortmund", "Borussia Dortmund")
    assert _team_eq("B. Monchengladbach", "Borussia Monchengladbach")
    assert _team_eq("Newcastle", "Newcastle United")
    assert _team_eq("Manchester Utd", "Manchester United")
    assert _team_eq("Sc Braga", "Braga")
    assert _team_eq("Nottingham", "Nottingham Forest")


def test_team_eq_negative():
    assert _team_eq("Inter", "AC Milan") is False
    assert _team_eq("Real Madrid", "Atletico Madrid") is False
