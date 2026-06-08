import hashlib
import secrets

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from oblak.db.session import get_db
from oblak.models.entities import User


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def create_api_key() -> str:
    return secrets.token_urlsafe(32)


def authenticate_api_key(api_key: str, db: Session) -> User | None:
    key_hash = hash_api_key(api_key)
    return db.query(User).filter(User.api_key_hash == key_hash).one_or_none()


def require_user(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> User:
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-API-Key")
    user = authenticate_api_key(x_api_key, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return user
