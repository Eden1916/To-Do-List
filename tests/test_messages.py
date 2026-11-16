import jwt
import pytest
from fastapi.testclient import TestClient

from todo_chat.config import Settings
from todo_chat.database import init_database
from todo_chat.main import create_app

SECRET = "message-test-secret-with-at-least-32-characters"


def settings_for(tmp_path):
    return Settings(
        _env_file=None, jwt_secret=SECRET,
        database_url=f"sqlite:///{(tmp_path / 'messages.db').as_posix()}",
    )


def register(client, email="first@example.com"):
    response = client.post("/auth/signup", json={
        "name": "User", "email": email, "password": "long test password",
    })
    assert response.status_code == 201
    data = response.json()
    return {"Authorization": "Bearer " + data["token"]}, data["user"]


@pytest.fixture
def setup(tmp_path):
    app = create_app(settings_for(tmp_path))
    with TestClient(app) as client:
        init_database(app.app.state.engine)
        headers, user = register(client)
        yield client, headers, user


def test_message_creates_task_with_consistent_shape_and_updates_counts(setup):
    client, headers, user = setup
    response = client.post("/messages", headers=headers, json={"text": "  Buy milk \n"})
    assert response.status_code == 200
    data = response.json()
    assert set(data) == {"reply", "task"}
    assert data["reply"] == "Added task: Buy milk"
    task = data["task"]
    assert task["title"] == "Buy milk"
    assert task["status"] == "pending"
    assert task["description"] is None
    assert task["ownerUserId"] == user["id"]
    assert set(task) == {"id", "title", "description", "status", "createdAt", "updatedAt", "ownerUserId"}
    assert client.get(f"/tasks/{task['id']}", headers=headers).json() == {"task": task}
    assert client.get("/tasks?limit=3", headers=headers).json() == {"tasks": [task]}
    assert client.get("/tasks/stats", headers=headers).json() == {"total": 1, "pending": 1, "completed": 0}


@pytest.mark.parametrize("payload", [
    {}, {"text": ""}, {"text": " \t\n"}, {"text": "x" * 201},
    {"text": None}, {"text": 12}, {"text": "Task", "ownerUserId": 2},
    {"text": "Task", "status": "completed"},
])
def test_invalid_message_does_not_create_task(setup, payload):
    client, headers, _ = setup
    response = client.post("/messages", headers=headers, json=payload)
    assert response.status_code == 400
    assert response.json() == {"message": "Invalid input"}
    assert client.get("/tasks", headers=headers).json() == {"tasks": []}


def test_message_accepts_maximum_title_length_after_trimming(setup):
    client, headers, _ = setup
    response = client.post("/messages", headers=headers, json={"text": "  " + "x" * 200 + "  "})
    assert response.status_code == 200
    assert response.json()["task"]["title"] == "x" * 200


@pytest.mark.parametrize("auth", ["missing", "invalid", "expired"])
def test_message_requires_valid_authentication_without_side_effects(setup, auth):
    client, headers, _ = setup
    request_headers = {}
    if auth == "invalid":
        request_headers = {"Authorization": "Bearer invalid"}
    elif auth == "expired":
        token = headers["Authorization"].split()[1]
        claims = jwt.decode(token, options={"verify_signature": False})
        claims["exp"] = 1
        request_headers = {"Authorization": "Bearer " + jwt.encode(claims, SECRET, algorithm="HS256")}
    response = client.post("/messages", headers=request_headers, json={"text": "Buy milk"})
    assert response.status_code == 401
    assert response.json() == {"message": "Not authenticated"}
    assert response.headers["www-authenticate"] == "Bearer"
    assert client.get("/tasks", headers=headers).json() == {"tasks": []}


def test_message_task_is_private_to_its_owner(setup):
    client, first_headers, user = setup
    other_headers, _ = register(client, "other@example.com")
    task = client.post("/messages", headers=first_headers, json={"text": "Private task"}).json()["task"]
    assert task["ownerUserId"] == user["id"]
    assert client.get("/tasks", headers=other_headers).json() == {"tasks": []}
    assert client.get("/tasks/stats", headers=other_headers).json() == {"total": 0, "pending": 0, "completed": 0}
    assert client.get(f"/tasks/{task['id']}", headers=other_headers).status_code == 404


@pytest.mark.parametrize("command", ["complete task 1", "delete task 1", "what's pending?"])
def test_simple_mode_treats_commands_as_titles(setup, command):
    client, headers, _ = setup
    original = client.post("/tasks", headers=headers, json={"title": "Original task"}).json()["task"]
    response = client.post("/messages", headers=headers, json={"text": command})
    assert response.status_code == 200
    assert response.json()["task"]["title"] == command
    assert response.json()["task"]["status"] == "pending"
    assert client.get(f"/tasks/{original['id']}", headers=headers).json() == {"task": original}


def test_message_task_persists_after_shutdown_restart(tmp_path):
    settings = settings_for(tmp_path)
    app = create_app(settings)
    with TestClient(app) as client:
        init_database(app.app.state.engine)
        headers, _ = register(client)
        task = client.post("/messages", headers=headers, json={"text": "Persist me"}).json()["task"]
    with TestClient(create_app(settings)) as restarted:
        assert restarted.get(f"/tasks/{task['id']}", headers=headers).json() == {"task": task}
