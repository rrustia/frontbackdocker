from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app

# I use one in-memory SQLite DB for the whole test process.
# I use StaticPool so every test session points to the same transient database.
TEST_DB_URL = "sqlite://"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def clean_database() -> Generator[None, None, None]:
    """I recreate schema per test so runs stay isolated and deterministic."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def override_get_db() -> Generator[Session, None, None]:
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def auth_headers() -> dict[str, str]:
    """I authenticate once and return bearer token headers for protected endpoints."""
    login_resp = client.post("/auth/login", json={"username": "admin", "password": "admin123"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_rejects_unauthorized_task_access() -> None:
    response = client.get("/tasks")
    assert response.status_code == 401


def test_task_crud_flow() -> None:
    headers = auth_headers()

    create_resp = client.post(
        "/tasks",
        headers=headers,
        json={
            "title": "Write release notes",
            "description": "Summarize user-facing features",
            "status": "todo",
            "priority": "high",
            "due_date": "2026-07-15",
        },
    )
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["title"] == "Write release notes"
    task_id = created["id"]

    list_resp = client.get("/tasks", headers=headers)
    assert list_resp.status_code == 200
    listed = list_resp.json()
    assert len(listed) == 1
    assert listed[0]["id"] == task_id

    patch_resp = client.patch(
        f"/tasks/{task_id}",
        headers=headers,
        json={
            "status": "in_progress",
            "priority": "medium",
        },
    )
    assert patch_resp.status_code == 200
    patched = patch_resp.json()
    assert patched["status"] == "in_progress"
    assert patched["priority"] == "medium"

    delete_resp = client.delete(f"/tasks/{task_id}", headers=headers)
    assert delete_resp.status_code == 204

    list_after_delete = client.get("/tasks", headers=headers)
    assert list_after_delete.status_code == 200
    assert list_after_delete.json() == []


def test_filter_by_status() -> None:
    headers = auth_headers()

    client.post(
        "/tasks",
        headers=headers,
        json={"title": "Task A", "status": "todo", "priority": "low"},
    )
    client.post(
        "/tasks",
        headers=headers,
        json={"title": "Task B", "status": "done", "priority": "high"},
    )

    response = client.get("/tasks", headers=headers, params={"status": "done"})
    assert response.status_code == 200
    filtered = response.json()
    assert len(filtered) == 1
    assert filtered[0]["title"] == "Task B"


def test_validation_rejects_short_title() -> None:
    headers = auth_headers()
    response = client.post("/tasks", headers=headers, json={"title": "no"})
    assert response.status_code == 422


def test_login_rejects_bad_password() -> None:
    response = client.post("/auth/login", json={"username": "admin", "password": "wrong-pass"})
    assert response.status_code == 401


def test_auth_me_returns_current_user() -> None:
    headers = auth_headers()
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"username": "admin"}


def test_auth_me_rejects_invalid_token() -> None:
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == 401
