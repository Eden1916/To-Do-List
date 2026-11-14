"""Database connections and request-scoped sessions."""

from uuid import uuid4

from fastapi import Request
from sqlalchemy import create_engine, event, inspect, text
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
    _migrate_account_ids(engine)


def _migrate_account_ids(engine: Engine) -> None:
    if not inspect(engine).has_table("users"):
        return

    columns = {column["name"] for column in inspect(engine).get_columns("users")}
    with engine.begin() as connection:
        if "account_id" not in columns:
            connection.execute(text("ALTER TABLE users ADD COLUMN account_id VARCHAR(36)"))
        user_ids = connection.execute(
            text("SELECT id FROM users WHERE account_id IS NULL")
        ).scalars().all()
        for user_id in user_ids:
            connection.execute(
                text("UPDATE users SET account_id = :account_id WHERE id = :user_id"),
                {"account_id": str(uuid4()), "user_id": user_id},
            )
        indexes = {index["name"] for index in inspect(connection).get_indexes("users")}
        if "ix_users_account_id" not in indexes:
            connection.execute(text(
                "CREATE UNIQUE INDEX ix_users_account_id ON users (account_id)"
            ))


def get_session(request: Request):
    with Session(request.app.state.engine) as session:
        yield session
