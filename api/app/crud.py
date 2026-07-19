from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas


def create_task(db: Session, payload: schemas.TaskCreate) -> models.Task:
    """Stores a new task in the database.

    Input: A database session and a task payload.
    Output: Returns the committed task row.
    """
    task = models.Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_tasks(db: Session, status: schemas.TaskStatus | None = None) -> list[models.Task]:
    """Fetches tasks in newest-first order.

    Input: A database session and an optional status filter.
    Output: Returns a list of matching tasks.
    """
    stmt = select(models.Task).order_by(models.Task.created_at.desc())
    if status:
        stmt = stmt.where(models.Task.status == status)

    return list(db.scalars(stmt).all())


def get_task(db: Session, task_id: int) -> models.Task | None:
    """Looks up one task by id.

    Input: A database session and a task id.
    Output: Returns the matching task, or None.
    """
    return db.get(models.Task, task_id)


def update_task(db: Session, task: models.Task, payload: schemas.TaskUpdate) -> models.Task:
    """Applies partial changes to an existing task.

    Input: A database session, the task to change, and the update payload.
    Output: Returns the updated task.
    """
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(task, field, value)

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: models.Task) -> None:
    """Removes a task from the database.

    Input: A database session and the task to delete.
    Output: Returns nothing after the commit finishes.
    """
    db.delete(task)
    db.commit()
