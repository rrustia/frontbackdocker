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

# Comma-separated CORS origins are normalized from env to keep deployment config simple.
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
    """Creates the database tables when the app starts.

    Input: No request data; it runs at startup.
    Output: Leaves the tables ready before the API handles traffic.
    """
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Reports that the API is alive.

    Input: No request data.
    Output: Returns a simple status payload.
    """
    return {"status": "ok"}


@app.post("/auth/login", response_model=schemas.TokenOut)
def login(payload: schemas.LoginRequest) -> schemas.TokenOut:
    """Checks login details and returns a token.

    Input: A username and password payload.
    Output: Returns a JWT when the credentials are valid.
    """
    if not authenticate_user(payload.username, payload.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=payload.username)
    return schemas.TokenOut(access_token=token)


@app.get("/auth/current-user", response_model=schemas.AuthUserOut)
def current_user(current_username: str = Depends(get_current_username)) -> schemas.AuthUserOut:
    """Returns the authenticated user's name.

    Input: A valid bearer token comes through the dependency.
    Output: Returns the current username.
    """
    return schemas.AuthUserOut(username=current_username)


@app.get("/tasks", response_model=list[schemas.TaskOut])
def list_tasks(
    status_filter: schemas.TaskStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_username),
) -> list[schemas.TaskOut]:
    """Lists tasks for the signed-in user.

    Input: An optional status filter and the active database session.
    Output: Returns a list of task records.
    """
    return crud.list_tasks(db, status=status_filter)


@app.post("/tasks", response_model=schemas.TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_username),
) -> schemas.TaskOut:
    """Creates a new task record.

    Input: Task details and a database session.
    Output: Returns the saved task.
    """
    return crud.create_task(db, payload)


@app.patch("/tasks/{task_id}", response_model=schemas.TaskOut)
def patch_task(
    task_id: int,
    payload: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_username),
) -> schemas.TaskOut:
    """Updates one task when it exists.

    Input: A task id, partial task data, and a database session.
    Output: Returns the updated task, or raises a 404 error if the task is missing.
    """
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
    """Deletes one task when it exists.

    Input: A task id and a database session.
    Output: Returns no content after the delete succeeds, or raises a 404 error if the task is missing.
    """
    task = crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    crud.delete_task(db, task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
