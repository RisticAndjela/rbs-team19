from sqlalchemy.orm import Session

from oblak.db.init_db import init_db
from oblak.db.session import SessionLocal
from oblak.models.entities import User
from oblak.security.auth import hash_api_key

DEV_USERNAME = "dev"
DEV_API_KEY = "oblak-dev-key"


def seed_user(db: Session) -> None:
    existing = db.query(User).filter(User.username == DEV_USERNAME).one_or_none()
    if existing:
        return
    db.add(User(username=DEV_USERNAME, api_key_hash=hash_api_key(DEV_API_KEY)))
    db.commit()


if __name__ == "__main__":
    init_db()
    with SessionLocal() as db:
        seed_user(db)
    print(f"Seeded user '{DEV_USERNAME}' with API key: {DEV_API_KEY}")
