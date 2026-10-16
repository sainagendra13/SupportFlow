import hashlib
import hmac
import secrets
from fastapi import Depends, HTTPException, Request
from app.config import settings
from app.authorisation import get_token_payload


def create_csrf_token(session_id: str) -> str:
    nonce = secrets.token_hex(32)
    message = f"{session_id}:{nonce}".encode()
    signature = hmac.new(
        settings.jwt_secret.encode(),
        message,
        hashlib.sha256,
    ).hexdigest()
    return f"{nonce}.{signature}"


def verify_csrf_token(session_id: str, token: str) -> bool:
    try:
        nonce, signature = token.split(".", 1)
        bytes.fromhex(nonce)
        bytes.fromhex(signature)
    except (ValueError, AttributeError):
        return False

    if len(nonce) != 64 or len(signature) != 64:
        return False

    message = f"{session_id}:{nonce}".encode()
    expected = hmac.new(
        settings.jwt_secret.encode(),
        message,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(signature, expected)


async def require_csrf(request: Request, payload=Depends(get_token_payload)):
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return

    cookie_token = request.cookies.get("csrf_token")
    header_token = request.headers.get("X-CSRF-Token")

    if not cookie_token or not header_token:
        raise HTTPException(status_code=403, detail="CSRF token missing" )

    if not hmac.compare_digest(cookie_token, header_token):
        raise HTTPException(status_code=403,detail="CSRF token mismatch")

    if not verify_csrf_token(payload["jti"], header_token):
        raise HTTPException(status_code=403,detail="Invalid CSRF token")
