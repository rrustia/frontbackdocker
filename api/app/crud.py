from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas


def create_task(db: Session, payload: schemas.TaskCreate) -> models.Task:
    """I insert a new task and return the freshly committed row."""
    task = models.Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_tasks(db: Session, status: schemas.TaskStatus | None = None) -> list[models.Task]:
    """I return tasks ordered by creation time, newest first.

    I support optional status filtering for simple board-like UI views.
    """
    stmt = select(models.Task).order_by(models.Task.created_at.desc())
    if status:
        stmt = stmt.where(models.Task.status == status)

    return list(db.scalars(stmt).all())


def get_task(db: Session, task_id: int) -> models.Task | None:
    return db.get(models.Task, task_id)


def update_task(db: Session, task: models.Task, payload: schemas.TaskUpdate) -> models.Task:
    """I apply partial updates only for fields present in the request body."""
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(task, field, value)

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: models.Task) -> None:
    db.delete(task)
    db.commit()
