"""Google API common: service account credentials loading."""
import json
import logging
import os
from functools import lru_cache
from typing import List, Optional

from google.oauth2 import service_account

logger = logging.getLogger(__name__)

GOOGLE_SA_FILE = os.environ.get("GOOGLE_SA_FILE", "/app/backend/credentials/google_sa.json")


@lru_cache(maxsize=8)
def load_credentials(scopes: tuple) -> Optional[service_account.Credentials]:
    """Load Google service account credentials with the given scopes (tuple for caching)."""
    if not os.path.exists(GOOGLE_SA_FILE):
        logger.warning(f"Google SA file not found: {GOOGLE_SA_FILE}")
        return None
    try:
        return service_account.Credentials.from_service_account_file(
            GOOGLE_SA_FILE, scopes=list(scopes)
        )
    except Exception as e:
        logger.error(f"Failed to load Google SA credentials: {e}")
        return None


def get_service_account_email() -> Optional[str]:
    """Return the email of the service account (for UI hints)."""
    if not os.path.exists(GOOGLE_SA_FILE):
        return None
    try:
        return json.load(open(GOOGLE_SA_FILE)).get("client_email")
    except Exception:
        return None


def is_configured() -> bool:
    return os.path.exists(GOOGLE_SA_FILE)
