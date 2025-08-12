from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager

from ..core.config import settings

try:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={
            "check_same_thread": False
        },  # SQLite-specific: allows multi-threaded access
    )
except Exception as e:
    raise Exception(f"Failed to create database engine: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency for FastAPI or similar frameworks
def get_db():
    """
    Provide a database session for dependency injection (e.g., FastAPI).
    Yields a session and ensures it is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Context manager for standalone scripts (e.g., scraping, ML)
@contextmanager
def get_session():
    """
    Provide a database session for standalone scripts.
    Usage: with get_session() as session: ...
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_tables():
    """
    Create all tables defined in models based on Base metadata.
    """
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        raise Exception(f"Failed to create tables: {e}")
