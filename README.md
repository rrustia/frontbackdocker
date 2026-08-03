# TaskBoard (Docker + API + Tests + Web UI)

The project is a small but practical task board for learning a modern backend, frontend, and Docker workflow.

Project note:
- Purpose: It shows how the API, web UI, database, and tests fit together.
- Input: Docker Compose, API requests, and local test commands.
- Output: A running task board app, test results, and a clear setup path.

What it includes:
- FastAPI backend
- JWT login/auth
- PostgreSQL database
- Web interface (Nginx + vanilla JS)
- Automated tests (pytest)
- GitHub Actions CI workflow

## 1) Technologies Used

The project uses the following technologies:

### Backend
- Python 3.12+ (app runtime in Docker image)
- FastAPI 0.116.1 (REST API framework)
- Uvicorn 0.35.0 (ASGI server)
- SQLAlchemy 2.0.42 (ORM/database access)
- Pydantic 2.11.7 (request/response validation)

### Authentication and Security
- JWT (JSON Web Tokens) for API authentication
- python-jose 3.3.0 for token encoding/decoding
- passlib 1.7.4 (pbkdf2_sha256) for password hashing

### Database
- PostgreSQL 16 (Docker service)
- psycopg 3.2.9 (+ binary package) PostgreSQL driver
- SQLite in-memory database for automated tests

### Frontend
- HTML5
- CSS3
- Vanilla JavaScript (ES modules + Fetch API)
- Nginx 1.27 (static file serving + reverse proxy)
- Google Fonts (Space Grotesk and IBM Plex Mono)

### Testing and Quality
- pytest 8.4.1 (automated backend tests)
- fastapi.testclient / httpx (API test client stack)

### DevOps and Tooling
- Docker and Docker Compose (multi-service local development)
- GitHub Actions (CI test workflow)

## 2) Project Layout

- `api/`: FastAPI app, auth, DB models, API tests
- `web/`: frontend files + Nginx config
- `docker-compose.yml`: runs Postgres + API + Web together
- `.github/workflows/api-ci.yml`: CI that runs tests

## 3) Default Login (Development)

- Username: `rrustia`
- Password: `password123`

The default values can be changed in `docker-compose.yml`:
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`

## 4) Fast Start (Docker)

From the project root, this command starts the stack:

```bash
docker compose up --build
```

Then open the following:
- API docs: http://localhost:8000/docs
- Web app: http://localhost:8080

If the Docker daemon is not running, Docker Desktop (or Colima) should be started first.

## 5) Beginner-Friendly Test Checklist (All Functionalities)

The checklist below covers every major feature.

### A) Health Check

```bash
curl http://localhost:8000/health
```

Expected output:
- HTTP 200
- Body: `{"status":"ok"}`

### B) Login (JWT)

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"rrustia","password":"password123"}'
```

Expected:
- HTTP 200
- JSON includes `access_token`

The token can be saved to a shell variable:

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"rrustia","password":"password123"}' | jq -r .access_token)
```

### C) Current User Endpoint

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/auth/current-user
```

Expected output:
- HTTP 200
- Body includes the username (`rrustia`)

### D) Unauthorized Access Should Fail

```bash
curl http://localhost:8000/tasks
```

Expected:
- HTTP 401

### E) Create Task

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Prepare sprint demo",
    "description": "Capture before/after screenshots and metrics",
    "priority": "high",
    "due_date": "2026-07-20"
  }'
```

Expected:
- HTTP 201
- Response includes the task id and submitted task data

### F) List Tasks

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/tasks
```

Expected:
- HTTP 200
- Array with at least one task

### G) Filter Tasks by Status

```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/tasks?status=todo"
```

Expected:
- HTTP 200
- Array of tasks in `todo` status

### H) Update Task Status

Replace `1` with the task id for the task.

```bash
curl -X PATCH http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"status":"in_progress"}'
```

Expected output:
- HTTP 200
- `status` changed to `in_progress`

### I) Delete Task

Replace `1` with the task id for the task.

```bash
curl -X DELETE http://localhost:8000/tasks/1 \
  -H "Authorization: Bearer $TOKEN"
```

Expected:
- HTTP 204

### J) Web UI Test

1. Open http://localhost:8080
2. Log in with `rrustia` / `password123`
3. Create a task in the form
4. Change the status from the dropdown
5. Filter by status
6. Delete a task

Expected output:
- The page updates immediately
- API actions succeed without page reload errors

## 6) Run Automated Tests

### Option A: In Docker

```bash
docker compose run --rm api pytest -q
```

### Option B: Local venv (if Docker is unavailable)

macOS/Linux:

```bash
python3 -m venv .venv
./.venv/bin/pip install -r api/requirements.txt
./.venv/bin/pytest -q api/tests
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\pip install -r api\requirements.txt
.\.venv\Scripts\pytest -q api\tests
```

Current test coverage includes:
- health endpoint
- auth login success/failure
- auth current-user success/failure
- unauthorized access protection
- task create/list/filter/update/delete
- request validation

## 7) CI (GitHub Actions)

Workflow file:
- `.github/workflows/api-ci.yml`

It runs tests on:
- Push
- Pull request

## 8) Troubleshooting

- `docker.sock` missing error:
  Start Docker daemon (Docker Desktop or Colima), then rerun `docker compose up --build`.
- `ModuleNotFoundError: app` in local pytest:
  Run tests from project root and keep `api/pytest.ini` in place.
- Wrong login credentials:
  Check `ADMIN_USERNAME` and `ADMIN_PASSWORD` values in `docker-compose.yml`.
