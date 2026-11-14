# Chat-Based To-Do List API

FastAPI, SQLAlchemy, and Pydantic backend for a conversational to-do list.
The implementation sequence is in [execution.md](execution.md), based on
[issue #3](https://github.com/Eden1916/To-Do-List/issues/3).

## Run locally

Requires Python 3.10 or newer. From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -c "import secrets; print('TODO_JWT_SECRET=' + secrets.token_urlsafe(48))" | Add-Content .env
.\.venv\Scripts\python.exe -m todo_chat.init_db
.\.venv\Scripts\python.exe -m uvicorn todo_chat.main:app --reload
```

The API is at http://localhost:8000; interactive documentation is at
http://localhost:8000/docs. `GET /health` returns `{"status":"ok"}`.

P1 provides the application foundation and database models. P2 adds signup,
login, and current-user authentication. Task routes, statistics, and message
handling remain planned in subsequent PRs.

## Configuration and database

Settings load from environment variables or a local `.env`; environment
variables take precedence. Never commit `.env` or a local database.

| Variable | Default | Format |
| --- | --- | --- |
| `TODO_DATABASE_URL` | `sqlite:///./todo.db` | SQLAlchemy database URL; relative paths resolve from the working directory |
| `TODO_CORS_ORIGINS` | `["http://localhost:5173"]` | JSON array of allowed frontend origins |
| `TODO_JWT_SECRET` | Required for API startup | Random signing secret, at least 32 characters; generate once and keep private |
| `TODO_ACCESS_TOKEN_MINUTES` | `60` | Token lifetime in minutes, 1–10080 |

Keep the same signing secret across restarts and application workers so tokens
remain valid until expiry. Changing the secret invalidates existing tokens.
There is no built-in signing secret; API startup fails if it is missing. The
database initialization command does not require a signing secret. Generate
the secret once during setup; do not append another value on every restart.

SQLite is the supported local setup. Other SQLAlchemy database URLs require
their database driver and separate verification before deployment.

The initialization command creates missing tables, preserves existing data,
and adds unique account identifiers to existing users. The API does not create
tables on startup. Users have
unique emails and a password-hash column; tasks have an owner foreign key,
pending/completed status constraint, and UTC creation/update timestamps.
SQLite foreign keys are enabled on every connection.

The existing ChatSession schema is retained for compatibility. Simple message
mode does not need a conversation state machine or a session table.

## API contract for issue #3

Requests and application responses use JSON. Protected routes read
`Authorization: Bearer <token>`. Errors use `{"message":"readable explanation"}`.
Invalid request input returns 400 (including malformed JSON); missing routes
return 404; unexpected failures return 500 with a safe message. Authentication
failures will return 401. Creation succeeds with 201, other successful
operations with 200. Development CORS allows the frontend at
`http://localhost:5173`, JSON content type, and the Authorization header.

| Route (planned unless noted) | Request | Response |
| --- | --- | --- |
| `GET /health` (implemented) | None | `{ status: "ok" }` |
| `POST /auth/signup` (implemented) | `{ name, email, password }` | 201 `{ token, user }` |
| `POST /auth/login` (implemented) | `{ email, password }` | 200 `{ token, user }` |
| `GET /auth/me` (implemented) | Bearer token | `{ user }` |
| `GET /tasks` | Optional query options below | `{ tasks }` |
| `POST /tasks` | `{ title, description? }` | 201 `{ task }` |
| `PATCH /tasks/{id}` | Title, description, and/or status | `{ task }` |
| `DELETE /tasks/{id}` | Bearer token | 200 `{ message }` |
| `GET /tasks/stats` | Bearer token | `{ total, completed, pending }` |
| `POST /messages` | `{ text }` | `{ reply, task }` |

User responses contain `id`, `name`, and `email`, never passwords or hashes.
Passwords use Argon2id hashes through pwdlib; signup requires 8–128 characters.
Emails are normalized to lowercase for signup and login, and duplicate emails
return 400 even when concurrent signups race. Names are trimmed (1–100 characters).
Tokens are signed with HS256 using PyJWT and include user ID, a unique account
identifier, and expiration. Validation checks the algorithm, issuer, audience,
required claims, and account identity. Missing, invalid, expired tokens and
tokens for deleted users return 401. Wrong email/password
responses use `Invalid email or password`. Responses never include hashes.

These choices follow the [FastAPI security guidance](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
and [PyJWT usage documentation](https://pyjwt.readthedocs.io/en/stable/usage.html).

Task responses contain `id`, `title`, `description`, `status`, `createdAt`,
`updatedAt`, and `ownerUserId`. Status is `pending` or `completed`, with pending
the creation default. Titles are trimmed and must have 1–200 characters.
Timestamps are UTC ISO 8601. Partial updates allow clearing description with
null, but reject null title/status and empty updates. Ownership is server-set.

List options are `status=completed|pending` (omitted means all),
`limit` (positive, bounded; dashboard uses 3), and `sort=newest|oldest`
(default newest, creation time then ID). Optional `page` pagination remains
deferred until its page-size/limit interaction is specified.

Bot behavior chosen for today's scope: simple mode. Trimmed nonempty message
text becomes a pending task, with a confirmation reply and the created task.
Command parsing, due dates/priority, title search, and password reset are later
work. All task, statistics, and message operations will be scoped to the
authenticated user.

## Verify

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Foundation tests cover JSON success/errors, invalid JSON and validation, CORS
(including server errors), persistent database defaults/constraints, UTC
timestamps, task response aliases, and configuration. Test-only diagnostic
routes are not present in the application.
Authentication tests also cover credential failures, normalization, concurrent
duplicates, stored password hashes, invalid/expired tokens, and persistence
of users and tokens across application restarts.
