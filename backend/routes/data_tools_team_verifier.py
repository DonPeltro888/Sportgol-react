"""
Data Tools Team Verifier routes — DB hygiene check sui team.
Spostato da seo_intelligence per coerenza architetturale: questa funzione
verifica metadata reali (stadium/city/country/logo) → Data Tools, non SEO.

Endpoints:
- POST /api/data-tools/team-verifier/run?limit=50&only_with_drift=false
- GET  /api/data-tools/team-verifier/latest
"""
import logging
from fastapi import APIRouter, Depends, Query

from routes.admin_auth import verify_admin_token
from services import data_tools_team_verifier

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/data-tools/team-verifier", tags=["data-tools-team-verifier"])


@router.post("/run")
async def team_verifier_run(
    limit: int = Query(50, ge=1, le=300),
    only_with_drift: bool = Query(False),
    _=Depends(verify_admin_token),
):
    """Lancia verifica AI Perplexity su tutti i team. Default 50 (controllato per costi)."""
    return await data_tools_team_verifier.verify_all_teams(limit=limit, only_with_drift=only_with_drift)


@router.get("/latest")
async def team_verifier_latest(_=Depends(verify_admin_token)):
    return await data_tools_team_verifier.latest_report()
