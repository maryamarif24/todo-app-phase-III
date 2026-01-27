from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy import JSON


class ConversationBase(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True, ondelete="CASCADE")  # Foreign key to users table
    metadata_json: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)


class Conversation(ConversationBase, table=True):
    """
    Represents a user's conversation with the AI, including message history and context.
    """
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship with messages
    messages: List["Message"] = Relationship(back_populates="conversation")


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation."""
    pass


class ConversationRead(ConversationBase):
    """Schema for reading conversation data."""
    id: str
    created_at: datetime
    updated_at: datetime