from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy import JSON


class MessageBase(SQLModel):
    conversation_id: str = Field(foreign_key="conversation.id", index=True, ondelete="CASCADE")  # Foreign key to conversation
    role: str = Field(regex="^(user|assistant)$")  # Either "user" or "assistant"
    content: str
    metadata_json: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)


class Message(MessageBase, table=True):
    """
    An individual message in a conversation, either from the user or the AI response.
    """
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Relationship with conversation
    conversation: "Conversation" = Relationship(back_populates="messages")


class MessageCreate(MessageBase):
    """Schema for creating a new message."""
    pass


class MessageRead(MessageBase):
    """Schema for reading message data."""
    id: str
    timestamp: datetime