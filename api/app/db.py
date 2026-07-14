import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# I default to a local SQLite file, and Compose can override me.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")

# I add SQLite-specific connect args so request threads can share access safely.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """I provide one DB session per request and always clean it up.

    FastAPI dependency injection calls me for each request that needs database
    access. My `finally` block makes sure I always close the connection.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
