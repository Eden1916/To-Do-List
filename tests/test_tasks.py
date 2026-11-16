from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from todo_chat.config import Settings
from todo_chat.database import init_database
from todo_chat.main import create_app
from todo_chat.models import Task


@pytest.fixture
def setup(tmp_path):
    settings = Settings(_env_file=None, database_url=f"sqlite:///{(tmp_path / 'tasks.db').as_posix()}", jwt_secret='task-test-secret-with-at-least-32-characters')
    app = create_app(settings)
    with TestClient(app) as client:
        init_database(app.app.state.engine)
        accounts = []
        for email in ('first@example.com', 'second@example.com'):
            response = client.post('/auth/signup', json={'name': 'User', 'email': email, 'password': 'long test password'})
            assert response.status_code == 201
            data = response.json()
            accounts.append(({'Authorization': 'Bearer ' + data['token']}, data['user']['id']))
        yield client, accounts, settings


def add(client, headers, title='Buy milk', **fields):
    response = client.post('/tasks', json={'title': title, **fields}, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()['task']


def test_crud_and_statistics(setup):
    client, accounts, _ = setup
    headers, owner_id = accounts[0]
    assert client.get('/tasks', headers=headers).json() == {'tasks': []}
    assert client.get('/tasks/stats', headers=headers).json() == {'total': 0, 'completed': 0, 'pending': 0}
    task = add(client, headers, '  Buy milk  ', description='Two bottles')
    assert set(task) == {'id', 'title', 'description', 'status', 'createdAt', 'updatedAt', 'ownerUserId'}
    assert task['title'] == 'Buy milk'
    assert task['status'] == 'pending'
    assert task['ownerUserId'] == owner_id
    assert datetime.fromisoformat(task['createdAt'].replace('Z', '+00:00')).utcoffset().total_seconds() == 0
    path = f"/tasks/{task['id']}"
    assert client.get(path, headers=headers).json() == {'task': task}
    updated = client.patch(path, headers=headers, json={'title': 'Buy bread', 'status': 'completed', 'description': None}).json()['task']
    assert updated['description'] is None
    assert updated['title'] == 'Buy bread'
    assert updated['status'] == 'completed'
    assert updated['createdAt'] == task['createdAt']
    assert updated['updatedAt'] > task['updatedAt']
    assert client.get('/tasks/stats', headers=headers).json() == {'total': 1, 'completed': 1, 'pending': 0}
    assert client.delete(path, headers=headers).json() == {'message': 'Task deleted'}
    assert client.get(path, headers=headers).status_code == 404
    assert client.get('/tasks/stats', headers=headers).json() == {'total': 0, 'completed': 0, 'pending': 0}


def test_cross_user_isolation_for_every_operation(setup):
    client, accounts, _ = setup
    first, _ = accounts[0]
    second, _ = accounts[1]
    task = add(client, first)
    path = f"/tasks/{task['id']}"
    for method, payload in [('get', None), ('patch', {'title': 'stolen'}), ('delete', None)]:
        kwargs = {'headers': second}
        if payload is not None:
            kwargs['json'] = payload
        response = getattr(client, method)(path, **kwargs)
        assert response.status_code == 404
        assert response.json() == {'message': 'Task not found'}
    assert client.get('/tasks', headers=second).json() == {'tasks': []}
    assert client.get('/tasks/stats', headers=second).json() == {'total': 0, 'completed': 0, 'pending': 0}
    assert client.get(path, headers=first).json()['task'] == task
    assert client.get('/tasks/999999', headers=first).json() == {'message': 'Task not found'}


def test_order_filters_and_dashboard_limit(setup):
    client, accounts, _ = setup
    headers, _ = accounts[0]
    tasks = [add(client, headers, f'Task {i}') for i in range(5)]
    # Equal timestamps exercise deterministic ID tie breaking.
    with Session(client.app.app.state.engine) as session:
        for task in session.scalars(select(Task)):
            task.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
        session.commit()
    client.patch(f"/tasks/{tasks[1]['id']}", json={'status': 'completed'}, headers=headers)
    newest = client.get('/tasks?limit=3', headers=headers).json()['tasks']
    assert [task['id'] for task in newest] == [task['id'] for task in tasks[::-1][:3]]
    oldest = client.get('/tasks?sort=oldest', headers=headers).json()['tasks']
    assert [task['id'] for task in oldest] == [task['id'] for task in tasks]
    completed = client.get('/tasks?status=completed', headers=headers).json()['tasks']
    assert [task['id'] for task in completed] == [tasks[1]['id']]
    pending = client.get('/tasks?status=pending&limit=2&sort=oldest', headers=headers).json()['tasks']
    assert [task['id'] for task in pending] == [tasks[0]['id'], tasks[2]['id']]
    assert client.get('/tasks/stats', headers=headers).json() == {'total': 5, 'completed': 1, 'pending': 4}


@pytest.mark.parametrize('method,path,body', [
    ('get', '/tasks', None), ('get', '/tasks/stats', None), ('get', '/tasks/1', None),
    ('post', '/tasks', {'title': 'No auth'}), ('patch', '/tasks/1', {'status': 'completed'}),
    ('delete', '/tasks/1', None),
])
def test_all_routes_require_authentication(setup, method, path, body):
    client, _, _ = setup
    response = getattr(client, method)(path, **({'json': body} if body is not None else {}))
    assert response.status_code == 401
    assert response.json() == {'message': 'Not authenticated'}


@pytest.mark.parametrize('query', ['status=bad', 'limit=0', 'limit=-1', 'limit=101', 'limit=abc', 'sort=bad'])
def test_query_validation(setup, query):
    client, accounts, _ = setup
    response = client.get('/tasks?' + query, headers=accounts[0][0])
    assert response.status_code == 400
    assert response.json() == {'message': 'Invalid input'}


@pytest.mark.parametrize('payload', [{}, {'title': ''}, {'title': '  '}, {'title': 'x' * 201}, {'title': 'x', 'status': 'completed'}, {'title': 'x', 'ownerUserId': 2}, {'title': 'x', 'owner_user_id': 2}])
def test_create_validation_and_server_set_ownership(setup, payload):
    client, accounts, _ = setup
    response = client.post('/tasks', headers=accounts[0][0], json=payload)
    assert response.status_code == 400
    assert client.get('/tasks', headers=accounts[0][0]).json() == {'tasks': []}


@pytest.mark.parametrize('payload', [{}, {'title': None}, {'status': None}, {'title': ' '}, {'status': 'bad'}, {'ownerUserId': 2}, {'owner_user_id': 2}])
def test_update_validation_does_not_mutate_task(setup, payload):
    client, accounts, _ = setup
    headers = accounts[0][0]
    task = add(client, headers)
    response = client.patch(f"/tasks/{task['id']}", headers=headers, json=payload)
    assert response.status_code == 400
    assert client.get(f"/tasks/{task['id']}", headers=headers).json()['task'] == task


def test_tasks_persist_after_restart(tmp_path):
    settings = Settings(_env_file=None, database_url=f"sqlite:///{(tmp_path / 'restart.db').as_posix()}", jwt_secret='task-test-secret-with-at-least-32-characters')
    app = create_app(settings)
    with TestClient(app) as original:
        init_database(app.app.state.engine)
        data = original.post('/auth/signup', json={'name': 'User', 'email': 'restart@example.com', 'password': 'long test password'}).json()
        headers = {'Authorization': 'Bearer ' + data['token']}
        task = add(original, headers)
    with TestClient(create_app(settings)) as restarted:
        assert restarted.get(f"/tasks/{task['id']}", headers=headers).json()['task'] == task
        assert restarted.get('/tasks/stats', headers=headers).json()['total'] == 1
