"""
Database connection and session management for SQLModel.

Optimized for Neon PostgreSQL with sync driver for stability.
"""

import os
from typing import Generator

from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

# Load environment variables from .env file
load_dotenv()

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@ep-xyz.region.neon.tech/dbname?sslmode=require"
)

# Create sync engine for SQLModel (optimized for Neon PostgreSQL)
sync_engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300,  # Reduced recycle time for Neon
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10,
        # Removed statement_timeout options as they're not supported by Neon
    }
)


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database sessions."""
    with Session(sync_engine) as session:
        try:
            yield session
        finally:
            session.close()


def init_db() -> None:
    """Initialize database tables."""
    # Create all tables defined in the SQLModel metadata
    SQLModel.metadata.create_all(sync_engine)

    # Verify that tables exist by attempting to reflect them
    from sqlalchemy import inspect
    inspector = inspect(sync_engine)
    tables = inspector.get_table_names()
    print(f"Database tables: {tables}")

    # Specifically check for users table
    if 'users' in tables:
        print("Users table exists in database")
    else:
        print("WARNING: Users table does not exist in database!")


def close_db() -> None:
    """Close database connections."""
    sync_engine.dispose()


class TimestampMixin:
    """Mixin for adding created_at and updated_at timestamps."""

    created_at: str = ""
    updated_at: str = ""
