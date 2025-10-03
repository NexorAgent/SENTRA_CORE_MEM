from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import get_settings


def _create_engine() -> Engine:
    settings = get_settings()
    url = settings.database_url
    engine_kwargs: dict[str, object] = {
        "echo": settings.database_echo,
        "future": True,
        "pool_pre_ping": True,
    }
    if url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
        engine_kwargs["poolclass"] = NullPool
    else:
        engine_kwargs["pool_size"] = settings.database_pool_size
        engine_kwargs["max_overflow"] = settings.database_max_overflow
    return create_engine(url, **engine_kwargs)


_engine: Engine | None = None
_session_factory: scoped_session | None = None


def get_engine() -> Engine:
    global _engine, _session_factory
    if _engine is None:
        _engine = _create_engine()
        _session_factory = scoped_session(
            sessionmaker(bind=_engine, autoflush=False, autocommit=False, expire_on_commit=False)
        )
    return _engine


def reset_engine() -> None:
    global _engine, _session_factory
    if _session_factory is not None:
        _session_factory.remove()
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None


def _get_session_factory() -> scoped_session:
    global _session_factory
    if _session_factory is None:
        get_engine()
    assert _session_factory is not None
    return _session_factory


@contextmanager
def get_session() -> Iterator[Session]:
    session_factory = _get_session_factory()
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
