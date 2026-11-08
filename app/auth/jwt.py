from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> str:
    payload = jwt.decode(
        token, settings.secret_key, algorithms=[settings.algorithm]
    )
    sub = payload.get("sub")
    if not sub:
        raise jwt.InvalidTokenError("Token has no subject")
    return sub