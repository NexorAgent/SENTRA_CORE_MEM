from __future__ import annotations

from app.db import models  # noqa: F401  # ensures models are imported
from app.db.base import Base
from app.db.session import get_engine


def init_db() -> None:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
