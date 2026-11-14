import os
import subprocess
import sys
from datetime import timedelta

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from todo_chat.config import Settings
from todo_chat.database import build_engine, init_database
from todo_chat.main import create_app
from todo_chat.models import Task, User
from todo_chat.schema import TaskCreate, TaskResponse, TaskStatus, TaskUpdate, UserResponse


@pytest.fixture
def client():
    app = create_app(Settings(
        _env_file=None, database_url="sqlite://", jwt_secret="foundation-test-secret-at-least-32-characters"
    ))
    # Test-only routes exercise handlers without exposing diagnostic routes.
    @app.app.post("/validate")
    def validate(payload: TaskCreate):
        return payload

    @app.app.get("/unauthorized")
    def unauthorized():
        raise HTTPException(401, "Not logged in", headers={"WWW-Authenticate": "Bearer"})

    @app.app.get("/failure")
    def failure():
        raise RuntimeError("private internal details")

    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


def test_health_and_not_found_are_json(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    response = client.get("/missing")
    assert response.status_code == 404
    assert response.json() == {"message": "Not Found"}


def test_invalid_json_and_validation_are_400(client):
    for kwargs in (
        {"json": {"title": "   "}},
        {"json": {"title": "x" * 201}},
        {"content": "{", "headers": {"Content-Type": "application/json"}},
    ):
        response = client.post("/validate", **kwargs)
        assert response.status_code == 400
        assert response.json() == {"message": "Invalid input"}
    assert client.post("/validate", json={"title": "  Buy milk  "}).json()["title"] == "Buy milk"


def test_http_error_preserves_auth_header(client):
    response = client.get("/unauthorized")
    assert response.status_code == 401
    assert response.json() == {"message": "Not logged in"}
    assert response.headers["www-authenticate"] == "Bearer"


def test_cors_preflight_and_unexpected_error(client):
    origin = {"Origin": "http://localhost:5173"}
    response = client.options("/health", headers={
        **origin,
        "Access-Control-Request-Method": "PATCH",
        "Access-Control-Request-Headers": "Authorization, Content-Type",
    })
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin["Origin"]
    response = client.get("/failure", headers=origin)
    assert response.status_code == 500
    assert response.json() == {"message": "Internal server error"}
    assert response.headers["access-control-allow-origin"] == origin["Origin"]
    response = client.get("/health", headers={"Origin": "https://untrusted.example"})
    assert "access-control-allow-origin" not in response.headers


def test_database_persists_defaults_aliases_and_updates(tmp_path):
    url = f"sqlite:///{(tmp_path / 'test.db').as_posix()}"
    engine = build_engine(url)
    init_database(engine)
    init_database(engine)  # Safe to repeat on an existing database.
    with Session(engine) as session:
        user = User(name="Ada", email="ada@example.com", password_hash="test-only-hash")
        task = Task(title="Buy milk", owner=user)
        session.add(user)
        session.commit()
        old_updated = task.updated_at
        assert task.status == TaskStatus.pending
        assert UserResponse.model_validate(user).model_dump() == {
            "id": user.id, "name": "Ada", "email": "ada@example.com",
        }
    engine.dispose()

    engine = build_engine(url)
    with Session(engine) as session:
        task = session.scalar(select(Task))
        payload = TaskResponse.model_validate(task).model_dump(mode="json", by_alias=True)
        assert set(payload) == {
            "id", "title", "description", "status", "createdAt", "updatedAt", "ownerUserId",
        }
        assert payload["status"] == "pending"
        assert task.created_at.utcoffset() == timedelta(0)
        task.title = "Buy bread"
        session.commit()
        assert task.updated_at >= old_updated
        assert session.execute(text("SELECT status FROM tasks")).scalar_one() == "pending"
    engine.dispose()


def test_database_enforces_unique_email_and_owner(tmp_path):
    engine = build_engine(f"sqlite:///{(tmp_path / 'constraints.db').as_posix()}")
    init_database(engine)
    with Session(engine) as session:
        session.add(User(name="Ada", email="ada@example.com", password_hash="test-only"))
        session.commit()
        session.add(User(
            name="Other", email="ada@example.com", password_hash="sensitive-hash-value"
        ))
        with pytest.raises(IntegrityError) as error:
            session.commit()
        assert "sensitive-hash-value" not in str(error.value)
        session.rollback()
        session.add(Task(title="Orphan", owner_user_id=999))
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
        with pytest.raises(IntegrityError):
            session.execute(text(
                "INSERT INTO tasks (title, status, owner_user_id, created_at, updated_at) "
                "VALUES ('Bad', 'unknown', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ))
            session.commit()
        session.rollback()
    engine.dispose()


@pytest.mark.parametrize("payload", [
    {}, {"title": None}, {"status": None}, {"status": "unknown"}, {"ownerUserId": 2},
])
def test_invalid_task_updates(payload):
    with pytest.raises(ValidationError):
        TaskUpdate.model_validate(payload)


def test_description_can_be_cleared_and_status_updated():
    assert TaskUpdate(description=None).model_fields_set == {"description"}
    assert TaskUpdate(status="completed").status == TaskStatus.completed


def test_environment_configuration(monkeypatch):
    monkeypatch.setenv("TODO_DATABASE_URL", "sqlite:///custom.db")
    monkeypatch.setenv("TODO_CORS_ORIGINS", '["https://todo.example"]')
    settings = Settings(_env_file=None)
    assert settings.database_url == "sqlite:///custom.db"
    assert settings.cors_origins == ["https://todo.example"]


def test_database_initialization_command(tmp_path):
    url = f"sqlite:///{(tmp_path / 'cli.db').as_posix()}"
    result = subprocess.run(
        [sys.executable, "-m", "todo_chat.init_db"],
        env={**os.environ, "TODO_DATABASE_URL": url},
        capture_output=True, text=True, check=True,
    )
    assert "Database initialized" in result.stdout
    engine = build_engine(url)
    assert set(inspect(engine).get_table_names()) == {"tasks", "users"}
    engine.dispose()


def test_database_initialization_migrates_existing_users(tmp_path):
    engine = build_engine(f"sqlite:///{(tmp_path / 'legacy.db').as_posix()}")
    with engine.begin() as connection:
        connection.execute(text(
            "CREATE TABLE users (id INTEGER PRIMARY KEY, name VARCHAR(100) NOT NULL, "
            "email VARCHAR(320) NOT NULL, password_hash VARCHAR(255) NOT NULL, "
            "created_at DATETIME NOT NULL)"
        ))
        connection.execute(text(
            "INSERT INTO users (id, name, email, password_hash, created_at) "
            "VALUES (9, 'Ada', 'ada@example.com', 'legacy-hash', CURRENT_TIMESTAMP)"
        ))

    init_database(engine)
    with Session(engine) as session:
        user = session.get(User, 9)
        assert user.account_id
        account_id = user.account_id
    init_database(engine)
    with Session(engine) as session:
        assert session.get(User, 9).account_id == account_id
    engine.dispose()
