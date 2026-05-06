"""
Symmetric encryption for SEO Admin API keys.
Uses Fernet (cryptography). Key from env SEO_ADMIN_FERNET_KEY.
NEVER returns decrypted values to frontend.
"""
import os
from cryptography.fernet import Fernet, InvalidToken


def _get_fernet() -> Fernet:
    key = os.environ.get("SEO_ADMIN_FERNET_KEY", "")
    if not key:
        raise RuntimeError("SEO_ADMIN_FERNET_KEY not configured")
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt(value: str) -> str:
    """Encrypt a string value. Returns base64-safe ciphertext."""
    if value is None or value == "":
        return ""
    f = _get_fernet()
    return f.encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt(token: str) -> str:
    """Decrypt a ciphertext. Returns plain string. '' if invalid/empty."""
    if not token:
        return ""
    f = _get_fernet()
    try:
        return f.decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        return ""


def mask_secret(value: str, visible: int = 4) -> str:
    """Show only last N chars of a secret for display purpose."""
    if not value:
        return ""
    if len(value) <= visible:
        return "•" * len(value)
    return "•" * (len(value) - visible) + value[-visible:]
