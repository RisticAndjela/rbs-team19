from oblak.db.session import Base, engine
from oblak.models import entities  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
