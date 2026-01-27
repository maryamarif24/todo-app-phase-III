from typing import List, Optional
import uuid
from sqlmodel import Session, select
from ..models.conversation import Conversation, ConversationCreate
from ..models.message import Message, MessageCreate


class ConversationService:
    """
    Service for managing conversations and messages in the database.
    """

    @staticmethod
    def create_conversation(session: Session, conversation_data: ConversationCreate) -> Conversation:
        """
        Create a new conversation in the database.
        """
        conversation = Conversation.model_validate(conversation_data)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation

    @staticmethod
    def get_conversation_by_id(session: Session, conversation_id: str) -> Optional[Conversation]:
        """
        Retrieve a conversation by its ID.
        """
        return session.get(Conversation, conversation_id)

    @staticmethod
    def get_conversations_by_user(session: Session, user_id: uuid.UUID) -> List[Conversation]:
        """
        Retrieve all conversations for a specific user.
        """
        statement = select(Conversation).where(Conversation.user_id == user_id)
        return session.exec(statement).all()

    @staticmethod
    def add_message_to_conversation(
        session: Session,
        conversation_id: str,
        message_data: MessageCreate
    ) -> Message:
        """
        Add a message to a conversation.
        """
        # Message class is already imported at the top, so no need to import again
        message = Message.model_validate(message_data)
        session.add(message)
        session.commit()
        session.refresh(message)
        return message

    @staticmethod
    def get_messages_by_conversation(session: Session, conversation_id: str) -> List[Message]:
        """
        Retrieve all messages for a specific conversation.
        """
        statement = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.timestamp)
        return session.exec(statement).all()

    @staticmethod
    def get_latest_messages_by_user(
        session: Session,
        user_id: uuid.UUID,
        limit: int = 10
    ) -> List[Message]:
        """
        Retrieve the latest messages for a user across all their conversations.
        """
        # Join Conversation and Message tables to get messages for a specific user
        statement = (
            select(Message)
            .join(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Message.timestamp.desc())
            .limit(limit)
        )
        return session.exec(statement).all()
