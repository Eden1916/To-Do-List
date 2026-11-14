from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from threading import Barrier

import jwt
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from todo_chat.config import Settings
from todo_chat.database import init_database
from todo_chat.main import create_app
from todo_chat.models import User
from todo_chat.security import AUDIENCE, ISSUER, password_hash

SECRET = 'authentication-test-secret-with-at-least-32-characters'
PASSWORD = 'a long test password'


def settings_for(tmp_path):
    return Settings(
        _env_file=None,
        database_url=f"sqlite:///{(tmp_path / 'auth.db').as_posix()}",
        jwt_secret=SECRET,
    )


@pytest.fixture
def client(tmp_path):
    app = create_app(settings_for(tmp_path))
    with TestClient(app) as client:
        init_database(app.app.state.engine)
        yield client


def register(client, **changes):
    return client.post('/auth/signup', json={
        'name': '  Ada Lovelace  ', 'email': 'Ada@Example.com',
        'password': PASSWORD, **changes,
    })


def test_signup_hashes_password_and_restores_user(client):
    response = register(client)
    assert response.status_code == 201
    data = response.json()
    assert set(data) == {'token', 'user'}
    assert data['user'] == {'id': 1, 'name': 'Ada Lovelace', 'email': 'ada@example.com'}
    assert PASSWORD not in response.text
    with Session(client.app.app.state.engine) as session:
        user = session.scalar(select(User))
        assert user.password_hash.startswith('$argon2id$')
        assert user.password_hash != PASSWORD
        assert password_hash.verify(PASSWORD, user.password_hash)
    current = client.get('/auth/me', headers={'Authorization': f"Bearer {data['token']}"})
    assert current.status_code == 200
    assert current.json() == {'user': data['user']}
    claims = jwt.decode(data['token'], SECRET, algorithms=['HS256'], issuer=ISSUER, audience=AUDIENCE)
    assert claims['exp'] - claims['iat'] == 60 * 60
    assert claims['sub'] == '1'
    assert 'password' not in claims


def test_login_normalizes_email_and_returns_safe_user(client):
    original = register(client).json()
    response = client.post('/auth/login', json={'email': 'ADA@EXAMPLE.COM', 'password': PASSWORD})
    assert response.status_code == 200
    assert set(response.json()) == {'token', 'user'}
    assert response.json()['user'] == original['user']


@pytest.mark.parametrize('email,password', [
    ('ada@example.com', 'wrong password'), ('nobody@example.com', PASSWORD),
])
def test_wrong_credentials_have_same_generic_401(client, email, password):
    register(client)
    response = client.post('/auth/login', json={'email': email, 'password': password})
    assert response.status_code == 401
    assert response.json() == {'message': 'Invalid email or password'}
    assert response.headers['www-authenticate'] == 'Bearer'


def test_duplicate_email_case_insensitive(client):
    assert register(client).status_code == 201
    response = register(client, email='ADA@example.com')
    assert response.status_code == 400
    assert response.json() == {'message': 'Email is already registered'}


def test_concurrent_duplicate_signup(client, monkeypatch):
    # Force both requests past the initial lookup before either can insert.
    barrier = Barrier(2)
    original_hash = password_hash.hash

    def simultaneous_hash(password):
        barrier.wait(timeout=10)
        return original_hash(password)

    monkeypatch.setattr(password_hash, 'hash', simultaneous_hash)
    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(lambda _: register(client), range(2)))
    assert sorted(response.status_code for response in responses) == [201, 400]
    with Session(client.app.app.state.engine) as session:
        assert len(session.scalars(select(User)).all()) == 1


@pytest.mark.parametrize('header', [None, '', 'Bearer', 'Basic abc', 'Bearer not-a-jwt'])
def test_missing_or_malformed_credentials(client, header):
    headers = {} if header is None else {'Authorization': header}
    response = client.get('/auth/me', headers=headers)
    assert response.status_code == 401
    assert response.json() == {'message': 'Not authenticated'}
    assert response.headers['www-authenticate'] == 'Bearer'


def token_with(**changes):
    now = datetime.now(timezone.utc)
    claims = {
        'sub': '1', 'iat': now - timedelta(minutes=1),
        'exp': now + timedelta(minutes=10), 'iss': ISSUER, 'aud': AUDIENCE,
    }
    claims.update(changes)
    return jwt.encode(claims, SECRET, algorithm='HS256')


@pytest.mark.parametrize('changes', [
    {'exp': 1}, {'sub': 'missing'}, {'sub': '-1'}, {'sub': str(2**100)},
    {'sub': '999'}, {'aud': 'other-api'}, {'iss': 'other-issuer'},
    {'iat': 9999999999}, {'exp': None}, {'sub': None},
])
def test_invalid_or_expired_claims(client, changes):
    register(client)
    response = client.get('/auth/me', headers={'Authorization': f'Bearer {token_with(**changes)}'})
    assert response.status_code == 401
    assert response.json() == {'message': 'Not authenticated'}


def test_tampered_and_missing_expiration_tokens(client):
    token = register(client).json()['token']
    tampered = token.split('.')
    tampered[1] = tampered[1][::-1]
    no_exp = jwt.encode({'sub': '1', 'iat': 1, 'iss': ISSUER, 'aud': AUDIENCE}, SECRET, algorithm='HS256')
    wrong_key = jwt.encode({'sub': '1', 'iat': 1, 'exp': 9999999999}, 'another-long-test-key-at-least-32-characters', algorithm='HS256')
    unsigned = jwt.encode({'sub': '1', 'iat': 1, 'exp': 9999999999}, None, algorithm='none')
    for invalid in ('.'.join(tampered), no_exp, wrong_key, unsigned):
        response = client.get('/auth/me', headers={'Authorization': f'Bearer {invalid}'})
        assert response.status_code == 401


def test_current_user_is_scoped_to_token_and_deleted_users_are_rejected(client):
    first = register(client).json()
    second = register(client, email='other@example.com', name='Other').json()
    for account in (first, second):
        response = client.get('/auth/me', headers={'Authorization': f"Bearer {account['token']}"})
        assert response.json() == {'user': account['user']}
    with Session(client.app.app.state.engine) as session:
        session.delete(session.get(User, first['user']['id']))
        session.commit()
    assert client.get('/auth/me', headers={'Authorization': f"Bearer {first['token']}"}).status_code == 401


def test_deleted_highest_id_token_is_rejected_after_id_reuse(client):
    original = register(client).json()
    with Session(client.app.app.state.engine) as session:
        session.delete(session.get(User, original['user']['id']))
        session.commit()

    replacement = register(client, email='replacement@example.com').json()
    assert replacement['user']['id'] == original['user']['id']
    response = client.get(
        '/auth/me', headers={'Authorization': 'Bearer ' + original['token']}
    )
    assert response.status_code == 401


@pytest.mark.parametrize('payload', [
    {'name': ' ', 'email': 'ada@example.com', 'password': PASSWORD},
    {'name': 'Ada', 'email': 'invalid', 'password': PASSWORD},
    {'name': 'Ada', 'email': 'ada@example.com', 'password': 'short'},
    {'name': 'Ada', 'email': 'ada@example.com', 'password': 'x' * 129},
    {'name': 'Ada', 'email': 'ada@example.com', 'password': PASSWORD, 'id': 4},
])
def test_signup_invalid_input(client, payload):
    response = client.post('/auth/signup', json=payload)
    assert response.status_code == 400
    assert response.json() == {'message': 'Invalid input'}


def test_user_and_token_survive_restart(tmp_path):
    settings = settings_for(tmp_path)
    app = create_app(settings)
    with TestClient(app) as client:
        init_database(app.app.state.engine)
        data = register(client).json()
    with TestClient(create_app(settings)) as client:
        response = client.get('/auth/me', headers={'Authorization': f"Bearer {data['token']}"})
        assert response.status_code == 200
        assert response.json() == {'user': data['user']}
        assert client.post('/auth/login', json={'email': 'ada@example.com', 'password': PASSWORD}).status_code == 200


def test_missing_secret_fails_startup(tmp_path, monkeypatch):
    monkeypatch.delenv('TODO_JWT_SECRET', raising=False)
    app = create_app(Settings(_env_file=None, database_url='sqlite://'))
    with pytest.raises(RuntimeError, match='TODO_JWT_SECRET'):
        with TestClient(app):
            pass


def test_secret_and_lifetime_validation():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, jwt_secret='short')
    with pytest.raises(ValidationError):
        Settings(_env_file=None, access_token_minutes=0)
