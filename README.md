# TaskBoard (Docker + API + Tests + Web UI)

I am a small but practical project you can use to learn a modern backend + frontend + Docker workflow.

What I include:
- FastAPI backend
- JWT login/auth
- PostgreSQL database
- Web interface (Nginx + vanilla JS)
- Automated tests (pytest)
- GitHub Actions CI workflow

## 1) Technologies Used

I use the following technologies in this project:

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

- Username: `admin`
- Password: `admin123`

You can change these values in `docker-compose.yml`:
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`

## 4) Fast Start (Docker)

From the project root, run:

```bash
docker compose up --build
```

Then open:
- API docs: http://localhost:8000/docs
- Web app: http://localhost:8080

If Docker daemon is not running, start Docker Desktop (or Colima) first.

## 5) Beginner-Friendly Test Checklist (All Functionalities)

I recommend using this checklist to test every major feature.

### A) Health Check

```bash
curl http://localhost:8000/health
```

Expected:
- HTTP 200
- Body: `{"status":"ok"}`

### B) Login (JWT)

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

Expected:
- HTTP 200
- JSON includes `access_token`

Save token to a shell variable:

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r .access_token)
```

### C) Current User Endpoint

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/auth/me
```

Expected:
- HTTP 200
- Body includes your username (`admin`)

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
- Response has task id and your task data

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

Replace `1` with your task id.

```bash
curl -X PATCH http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"status":"in_progress"}'
```

Expected:
- HTTP 200
- `status` changed to `in_progress`

### I) Delete Task

Replace `1` with your task id.

```bash
curl -X DELETE http://localhost:8000/tasks/1 \
  -H "Authorization: Bearer $TOKEN"
```

Expected:
- HTTP 204

### J) Web UI Test

1. Open http://localhost:8080
2. Log in with `admin` / `admin123`
3. Create a task in the form
4. Change status from dropdown
5. Filter by status
6. Delete a task

Expected:
- Data updates immediately in the page
- API actions succeed without page reload errors

## 6) Run Automated Tests

### Option A: In Docker

```bash
docker compose run --rm api pytest -q
```

### Option B: Local venv (if Docker is unavailable)

```bash
python3 -m venv .venv
./.venv/bin/pip install -r api/requirements.txt
./.venv/bin/pytest -q api/tests
```

Current test coverage includes:
- health endpoint
- auth login success/failure
- auth me success/failure
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
