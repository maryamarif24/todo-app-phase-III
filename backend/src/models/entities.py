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
    __tablename__ = "users"
    """
    User entity representing an authenticated user.

    Attributes:
        id: Unique user identifier (UUID)
        email: User's email address (unique, indexed)
        password_hash: Hashed password (bcrypt output, min 60 chars)
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    password_hash: str = Field(min_length=60)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to todos
    todos: List["Todo"] = Relationship(back_populates="user")


class Todo(SQLModel, table=True):
    """
    Todo entity representing a task owned by a user.

    Attributes:
        id: Unique todo identifier (UUID)
        user_id: Owning user identifier (FK to users.id)
        title: Todo title (required, 1-200 chars)
        description: Optional todo description (max 2000 chars)
        is_complete: Completion status (default false)
        created_at: Creation timestamp
        updated_at: Last update timestamp
        completed_at: Timestamp when the todo was marked as complete (nullable)
    """

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", ondelete="CASCADE")
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    is_complete: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)

    # Relationship to user
    user: "User" = Relationship(back_populates="todos")


# Re-export for convenience
__all__ = ["User", "Todo"]
