"""
SQLModel entities for the Todo application.

This module exports User and Todo models with proper relationships
for user-specific todo data isolation.
"""

from datetime import datetime
from typing import List, Optional
import uuid

from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    """
    User entity representing an authenticated user.

    Attributes:
        id: Unique user identifier (UUID)
        email: User's email address (unique, indexed)
        password_hash: Hashed password (bcrypt output, min 60 chars)
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = 'users'

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    password_hash: str = Field(min_length=60)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to todos (will be resolved after Todo is defined)
    todos: List["Todo"] = Relationship(back_populates="user")


# Re-export for convenience
__all__ = ["User"]
