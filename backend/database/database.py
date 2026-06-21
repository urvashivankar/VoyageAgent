import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trippilot.db")

Base = declarative_base()
engine = None
SessionLocal = None


def _sqlite_path() -> str | None:
    if not DATABASE_URL.startswith("sqlite"):
        return None
    db_path = DATABASE_URL.replace("sqlite:///", "")
    if db_path.startswith("./"):
        db_path = os.path.join(os.path.dirname(__file__), db_path[2:])
    return db_path


def _build_engine():
    kwargs = {}
    if DATABASE_URL.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(DATABASE_URL, **kwargs)


def _configure_session():
    global engine, SessionLocal
    engine = _build_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


_configure_session()


def _sync_trip_columns():
    """Add AI result columns to an existing trips table (dev schema drift)."""
    inspector = inspect(engine)
    if "trips" not in inspector.get_table_names():
        return

    existing = {col["name"] for col in inspector.get_columns("trips")}
    dialect = engine.dialect.name
    additions = {
        "budget_allocation": "JSONB" if dialect == "postgresql" else "JSON",
        "hotel_recommendations": "JSONB" if dialect == "postgresql" else "JSON",
        "travel_tips": "JSONB" if dialect == "postgresql" else "JSON",
        "total_estimated_cost": "FLOAT",
    }

    with engine.begin() as conn:
        for column, col_type in additions.items():
            if column not in existing:
                conn.execute(text(f"ALTER TABLE trips ADD COLUMN {column} {col_type}"))


def init_db():
    """Create all tables and sync schema in development."""
    from database import models  # noqa: F401

    if os.getenv("ENVIRONMENT") == "development":
        db_path = _sqlite_path()
        if db_path and os.path.exists(db_path):
            inspector = inspect(engine)
            if "trips" in inspector.get_table_names():
                existing = {col["name"] for col in inspector.get_columns("trips")}
                if "budget_allocation" not in existing:
                    engine.dispose()
                    os.remove(db_path)
                    _configure_session()

    Base.metadata.create_all(bind=engine)

    if os.getenv("ENVIRONMENT") == "development":
        _sync_trip_columns()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
