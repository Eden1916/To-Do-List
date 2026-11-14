# To-Do List: end-to-end execution plan

Target: finish the required checklist today, November 14, 2026 (America/Los_Angeles).
Source: [Issue #3 — Backend requirments for the To Do List](https://github.com/Eden1916/To-Do-List/issues/3).

This document is the implementation plan. Checkboxes below track completed and remaining work. P1–P6 identify work packages; actual GitHub PR numbers and links are recorded when opened.

## Starting point

- Local `main` contains README.md and todo_chat/schema.py; there is no runnable API, database setup, dependency manifest, or test suite in that tree.
- The locally available `origin/backend` has the same two files. The locally available `origin/frontend` contains a React/Vite application, authentication screens, dashboard, and task pages. Remote-tracking refs must be refreshed before implementation; they may be stale.
- Existing schemas use `username`, boolean task status, and snake_case timestamps. Issue #3 requires user `name`, string task status, and camelCase task timestamps. Resolve these at the API boundary before integration.
- Frontend auth currently has an unquoted JSON content type, `JSON.stringigy`, incorrect request serialization, and a dependency on `data.success` that is absent from the issue's required response shape. Dashboard counts are hardcoded and task fetching is commented out.
- P1 implementation is on `feat/3-api-foundation`. P2 authentication is implemented on `feat/3-authentication`; verification and PR status are tracked below. P3-P6 have not started.

## Finish line and scope

Today is complete when a fresh checkout runs locally, two users can register and sign in, each can manage only their own tasks, dashboard counts and lists update from persisted data, the message input works, and required checks pass on merged `main`.

All required issue sections are in scope, including the frontend usage checklist. Page pagination is optional in the issue; implement it after mandatory list options if time permits. Due dates, priority, title search, and password reset are explicitly later work and do not block today's required scope. Do not mark those issue boxes complete.

Suggested budget: 9–11 focused hours including review and fixes, measured from implementation start. This is an estimate, not a guarantee. If the available day is shorter, reduce optional work first and report any required unfinished boxes honestly.

## Decisions to settle first (proposed defaults)

Use these as the implementation contract unless the issue owner requests a change. Record them in the README and issue before checking the agreement boxes.

| Concern | Proposed contract |
| --- | --- |
| Stack | FastAPI, Pydantic v2, SQLAlchemy, SQLite for today's local app; database URL configurable |
| Register | `POST /auth/signup`, JSON `{ name, email, password }`, 201 |
| Login | `POST /auth/login`, JSON `{ email, password }`, 200; do not require form encoding |
| Auth result | Exactly `{ token, user }`; user contains `{ id, name, email }`, never password/hash |
| Current user | `GET /auth/me`, returns `{ user }` |
| Tokens | Signed token with user ID and expiry; proposed 60-minute lifetime; secret from environment |
| Protected requests | `Authorization: Bearer <token>`; missing, invalid, or expired token gives 401 |
| Error | `{ "message": "readable explanation" }` for all API errors, including validation and unexpected errors |
| Tasks | `GET/POST /tasks`; `PATCH/DELETE /tasks/{id}` |
| Task shape | `{ id, title, description, status, createdAt, updatedAt, ownerUserId }`; status is `pending` or `completed`; timestamps UTC ISO 8601 |
| Task responses | List `{ tasks }`; create/update `{ task }`; delete 200 `{ message }` so success remains JSON |
| List options | `status=completed|pending`, `limit` positive and bounded, `sort=newest|oldest` with newest default; break timestamp ties by ID |
| Optional pagination | `page` starts at 1; if implemented, define page size and interaction with limit explicitly and return pagination metadata |
| Statistics | `GET /tasks/stats` returns `{ total, completed, pending }`; register static route before `/tasks/{id}` |
| Messages | `POST /messages` takes `{ text }`; returns `{ reply, task }` with task null when no task changed; optional `tasks` for listing replies |
| Bot behavior today | Simple mode: trimmed nonempty text becomes a pending task; reply confirms creation. This chooses one of the issue's alternatives, not both |
| CORS | Explicitly allow `http://localhost:5173` in development and required JSON/Bearer methods and headers; production origin configurable |
| Validation/status | 200/201 success; invalid input 400 (normalize FastAPI's default 422); auth 401; missing/other-user task 404; unexpected error 500 |

Use a maintained password-hashing library with bcrypt or an equivalent secure algorithm. Never commit secrets. Return a generic `Invalid email or password` for failed login. Return a safe message for 500s and log details on the server.

## Branch and PR sequence

Start every new branch from updated `main` after its predecessor merges. This keeps PR diffs focused and avoids a stack that is hard to finish today. Keep existing `backend` and `frontend` branch work intact. Every PR references `Refs #3`; only P6 uses `Closes #3`, after all required acceptance checks pass. Update the actual PR column as work progresses.

P1 (#4) has merged into `main`. P2 initially continued on top of P1 while it
was a draft; the authentication branch is now synced with `origin/main`,
and draft PR #5 targets `main` for review and eventual merge.

| Order | Branch | Proposed PR title | Dependency | What it must achieve | Actual PR |
| --- | --- | --- | --- | --- | --- |
| P1 | `feat/3-api-foundation` | Establish API contract and persistent data model | None | Runnable API, dependencies, config, database, models, schemas, CORS, consistent errors | [#4](https://github.com/Eden1916/To-Do-List/pull/4) — merged |
| P2 | `feat/3-authentication` | Implement registration, login, and current user | P1 | Hashed passwords, expiring tokens, reusable auth dependency | [#5](https://github.com/Eden1916/To-Do-List/pull/5) — draft, targets main |
| P3 | `feat/3-task-api` | Implement user-scoped tasks and dashboard statistics | P2 | Persistent CRUD, filters, ordering, counts, ownership | Pending |
| P4 | `feat/3-message-api` | Turn bot messages into persisted tasks | P3 | Protected simple-mode message endpoint and replies | Pending |
| P5 | `feat/3-frontend-integration` | Connect frontend authentication, tasks, statistics, and messages | P4 | Working browser journey using actual API data | Pending |
| P6 | `test/3-release-readiness` | Verify the complete to-do flow and document setup | P5 | Integration coverage, clean setup instructions, final issue evidence | Pending |

### P1 — foundation and contract (60–90 minutes)

- [x] Fetch origin, inspect current issue comments and branches, and confirm no newer implementation supersedes this baseline.
- [x] Record the proposed contract in README: exact auth response, query names, and simple-mode bot behavior. Acceptance remains reviewable in P1.
- [x] Add dependency manifest, application entry point, configuration, `.env.example`, and ignore rules for local secrets/database files.
- [x] Add SQLAlchemy User and Task models: unique email, owner relationship, timestamps, persisted string task status. Create schema through `python -m todo_chat.init_db` (creates missing tables; not a migration system).
- [x] Align Pydantic request/response schemas with the contract, including `name`, title validation (trimmed, 1–200 characters), optional description, and output aliases.
- [x] Configure CORS and normalize API errors, validation failures, not-found responses, and unexpected exceptions to `{ message }`.
- [x] Retain ChatSession schemas without adding a state machine or table; simple mode does not need persisted conversation context.
- [x] Verify fresh virtual-environment install, API startup, database initialization, CORS preflight, JSON responses, and representative 400/404/500 shapes: 14 tests pass; `pip check` passes; Uvicorn `/health` and `/docs` smoke check passes.

Suggested files: `todo_chat/main.py`, `config.py`, `database.py`, `models.py`, existing `schema.py`, dependency manifest, `.env.example`.

### P2 — authentication (75–90 minutes)

- [x] Implement signup using name/email/password; normalize emails consistently and enforce uniqueness in the database, including concurrent duplicate attempts.
- [x] Hash passwords with Argon2id and exclude plaintext and hash from all API responses and application log messages.
- [x] Implement login returning `{ token, user }`; wrong email and wrong password both give the required generic 401 message.
- [x] Add signed expiring tokens, shared authentication dependency, and protected `/auth/me`. Require an environment-configured signing secret at startup.
- [x] Test signup, concurrent duplicate email, valid login, wrong credentials, missing/malformed/tampered/unsigned/expired tokens, deleted users, and restoration after restart. All 45 combined foundation/auth tests pass; `pip check` and real-server signup/login/me smoke checks pass.

Exit: a new user authenticates successfully; protected requests fail with 401 for every invalid-token case.

### P3 — tasks and statistics (90–120 minutes)

- [ ] Add create/list/update/delete routes with the authenticated user as the only source of ownership. Reject or ignore client-supplied owner IDs consistently.
- [ ] Create pending tasks; allow title and/or status updates; update `updatedAt` on change and preserve `createdAt`.
- [ ] Scope every task query, update, delete, and count to the current user. Other-user IDs behave as not found.
- [ ] Implement all/completed/pending lists, bounded limit, and deterministic newest-first ordering; support the agreed sort values.
- [ ] Implement title/status/query validation and JSON delete success; retain optional descriptions throughout the task lifecycle.
- [ ] Return per-user counts from `/tasks/stats`; total must equal completed plus pending.
- [ ] Test two-user isolation for reads, mutation, deletion, and statistics; test latest-three order, empty lists, invalid titles/statuses/limits, missing IDs, and persistence across application restart.
- [ ] Optional: implement and test page pagination after required behaviors pass.

### P4 — message input (30–45 minutes)

- [ ] Implement protected `POST /messages` with trimmed, nonempty text and the same title length bound.
- [ ] Use the same task service as ordinary creation so ownership, validation, timestamps, and default status remain consistent.
- [ ] Return a readable confirmation and the created task; reject empty/oversized text with 400 and invalid auth with 401.
- [ ] Test message-to-task persistence and user isolation. Document that command phrases are treated as task titles in simple mode.

The issue lists simple and smarter bot behavior as alternatives. Check the chosen simple-mode box and the behavior-decision box; leave the unselected command-parser alternative unchecked with an explanatory note. If command parsing is requested, estimate it separately and add ownership tests for complete/delete/list commands.

### P5 — frontend integration (90–120 minutes)

- [ ] Inspect the refreshed `origin/frontend` diff. Bring its frontend files onto this branch through a reviewed merge or targeted restore; preserve existing work and resolve conflicts deliberately.
- [ ] Fix auth helper syntax, JSON headers, and body serialization; send `name` at signup and consume `{ token, user }` without assuming a `success` field.
- [ ] Centralize API base URL, Bearer header, response parsing, and readable error handling. Restore the user with `/auth/me` on refresh; clear invalid auth and provide logout.
- [ ] Protect dashboard/task routes and handle loading, empty, error, and submitting states.
- [ ] Replace hardcoded dashboard counts with stats; fetch latest tasks using `limit=3` and newest ordering.
- [ ] Connect Total, Completed, and Pending pages to their correct filters. Wire creation, editing, completion/status changes, and deletion to the API.
- [ ] Wire message submit and Enter behavior; show the reply and refresh affected lists/counts after success. Prevent duplicate submission while pending.
- [ ] Verify signup → dashboard → create → edit → complete → filter → delete → logout → login → refresh. Repeat with a second account to verify isolation.
- [ ] Run frontend lint and production build; fix blockers and verify both light/dark layouts remain usable.

### P6 — verification and completion (60–90 minutes)

- [ ] Add meaningful API integration tests using a disposable test database and deterministic token-expiry checks. Cover auth, isolation, CRUD, filters, latest-three order, statistics, bot creation, and error shape.
- [ ] Add CI for the API tests and frontend lint/build using the commands committed in dependency manifests.
- [ ] Document supported runtime versions, install, configuration, database initialization, API startup, frontend startup, and the agreed endpoints in README.
- [ ] From a fresh checkout/environment, execute those setup steps and run the automated checks. Capture exact commands and results in the PR.
- [ ] Run the browser acceptance script below against the merged implementation, including persistence after restart and invalid/expired authentication.
- [ ] Map required issue boxes to the merged PRs and verification evidence. Do not mark a box complete based only on this plan or an unmerged branch.
- [ ] Merge P6 only when all required checks pass; close #3 with evidence and note the selected bot alternative, optional pagination status, and deferred nice-to-haves.

## Same-day execution schedule

| Elapsed time | Work | Checkpoint |
| --- | --- | --- |
| 0:00–0:20 | Refresh source, inspect issue comments, settle contract | No unresolved API names or bot behavior |
| 0:20–1:30 | P1 | API boots and persists data |
| 1:30–3:00 | P2 | Signup/login/me and token failures verified |
| 3:00–5:00 | P3 | CRUD, isolation, counts, latest-three pass |
| 5:00–5:45 | P4 | Message creates a persisted task |
| 5:45–7:45 | P5 | Full browser journey works |
| 7:45–9:15 | P6 | Fresh setup, tests, lint/build, evidence |
| 9:15–11:00 | Buffer | Fix failures, review and merge remaining PRs |

Review each PR at its checkpoint and merge passing work before starting its dependent branch. At hour 5, prioritize frontend integration if core task/auth behavior already passes. Drop optional pagination and smarter commands before cutting required verification. If required work remains at the end of the day, keep #3 open and record the exact remaining boxes.

## Issue checklist coverage

| Issue section / requirement | Delivery | Evidence needed |
| --- | --- | --- |
| General: JSON, CORS, Bearer auth, status codes, message errors | P1 + P2 | Preflight, JSON success/error checks, auth tests |
| Login: input, token/user, safe user shape, generic 401 | P2 | Success and wrong-credential tests |
| Register: input, duplicates, same response | P2 | New/duplicate email tests |
| Current user, hashing, token expiry, missing/invalid/expired 401 | P2 | Database hash check and auth tests |
| Tasks: own-user access, list status/limit/sort | P3 | Two-user isolation and list tests |
| Tasks: optional page | P3 optional | Pagination tests or explicit deferral |
| Tasks: create/update/delete, consistent shape, title limit | P3 | CRUD, serialization, and validation tests |
| Dashboard statistics scoped to user | P3 | Count changes after create/complete/delete |
| Frontend: live cards, latest three, full filtered lists with edit/delete | P5 | Browser walkthrough and API requests |
| Bot: protected message/reply/changed task | P4 + P5 | Endpoint test and browser message flow |
| Bot: decide simple vs smarter | P1 + P4 | Document simple-mode choice; unselected alternative is not a missing feature |
| Agreement: auth response, query names, message behavior | P1 | Contract recorded in README/issue |
| Later: due dates, priority, search, password reset | Deferred | Leave unchecked; separate follow-up work |

## Final browser acceptance script

1. Start with an empty database using README instructions. Register account A; confirm a token and safe user response, then reload successfully.
2. Create four tasks with distinct titles. Confirm the dashboard shows the latest three and total/pending counts equal four.
3. Edit one title and mark one task completed. Confirm Total includes four, Completed includes one, Pending includes three, and dashboard counts agree.
4. Delete a task from a full list. Confirm it disappears and counts update without re-login.
5. Submit a message; confirm the reply, new pending task, latest-three list, and counts agree.
6. Logout; protected pages/API calls must require login. Try wrong credentials, then login correctly.
7. Register account B. Confirm B sees no A tasks or counts. Try A's task ID through B's API token: read/update/delete must fail without changing A's data.
8. Restart the API and sign in as A. Confirm all remaining tasks persist. Test missing/invalid/expired token behavior and readable invalid-input errors.
9. Confirm lint, production build, API tests, and CI pass. Record actual PR links below before closing #3.

## Completion record

- P1 PR: [#4](https://github.com/Eden1916/To-Do-List/pull/4), merged into `main` at `5fac074`
- P2 PR: [#5](https://github.com/Eden1916/To-Do-List/pull/5), draft targeting `main`; branch synced with `origin/main`
- P3 merged PR: pending
- P4 merged PR: pending
- P5 merged PR: pending
- P6 merged PR: pending
- Automated checks: P1 implementation commit `002d4f6` has 14 passing tests in a fresh Python 3.10 virtual environment; `pip check`, Uvicorn startup/health/docs smoke check, and `git diff --check` pass. The test stack emits one Starlette/httpx deprecation warning. P3-P6 verification remains pending; P2 results are recorded below.
- Browser acceptance evidence: pending
- P2 verification: implementation commit `7735a00` has 45 passing combined tests (31 authentication cases); dependency checks and real Uvicorn signup/login/me/missing-token checks pass. One existing Starlette/httpx test-client deprecation warning remains.
- Remaining required issue boxes: P1 merged; P2 authentication implemented and verified, with PR review/merge pending. Task/statistics endpoints, messages, and frontend integration remain in P3-P6.
- Optional/later work deferred: pagination if omitted; smarter command parser; due dates/priority; search; password reset
