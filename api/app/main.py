import os

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .auth import authenticate_user, create_access_token, get_current_username
from .db import Base, engine, get_db

app = FastAPI(
    title="TaskBoard API",
    description="A compact task-tracking API meant for Docker-first local development.",
    version="1.0.0",
)

# I normalize comma-separated CORS origins from env to keep deployment config simple.
cors_origins_raw = os.getenv("CORS_ORIGINS", "http://localhost:8080")
cors_origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """I create tables automatically for local and Docker convenience.

    In production, I would usually replace this with migrations.
    """
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/auth/login", response_model=schemas.TokenOut)
def login(payload: schemas.LoginRequest) -> schemas.TokenOut:
    """I issue a JWT after validating username/password credentials."""
    if not authenticate_user(payload.username, payload.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=payload.username)
    return schemas.TokenOut(access_token=token)


@app.get("/auth/me", response_model=schemas.AuthUserOut)
def me(current_username: str = Depends(get_current_username)) -> schemas.AuthUserOut:
    return schemas.AuthUserOut(username=current_username)


@app.get("/tasks", response_model=list[schemas.TaskOut])
def list_tasks(
    status_filter: schemas.TaskStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_username),
) -> list[schemas.TaskOut]:
    return crud.list_tasks(db, status=status_filter)


@app.post("/tasks", response_model=schemas.TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_username),
) -> schemas.TaskOut:
    return crud.create_task(db, payload)


@app.patch("/tasks/{task_id}", response_model=schemas.TaskOut)
def patch_task(
    task_id: int,
    payload: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_username),
) -> schemas.TaskOut:
    task = crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return crud.update_task(db, task, payload)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_username),
) -> Response:
    task = crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    crud.delete_task(db, task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
