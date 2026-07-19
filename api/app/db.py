import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# This defaults to a local SQLite file, and Compose can override it.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")

# SQLite-specific connect args are added so request threads can share access safely.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Provides one database session per request.

    Input: No direct data; FastAPI calls it through dependency injection.
    Output: Yields a live session, then closes it after the request ends.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
