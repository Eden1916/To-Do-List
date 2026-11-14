"""Database connections and request-scoped sessions."""

from fastapi import Request
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


def build_engine(database_url: str) -> Engine:
    url = make_url(database_url)
    options = {"hide_parameters": True}
    if url.get_backend_name() == "sqlite":
        options["connect_args"] = {"check_same_thread": False}
        if url.database in (None, "", ":memory:"):
            options["poolclass"] = StaticPool
    engine = create_engine(url, **options)
    if url.get_backend_name() == "sqlite":
        @event.listens_for(engine, "connect")
        def enable_foreign_keys(connection, _record):
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    return engine


def init_database(engine: Engine) -> None:
    from todo_chat import models  # noqa: F401 -- register metadata

    Base.metadata.create_all(engine)


def get_session(request: Request):
    with Session(request.app.state.engine) as session:
        yield session
