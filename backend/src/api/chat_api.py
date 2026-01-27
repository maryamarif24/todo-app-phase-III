from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any, Optional
from pydantic import BaseModel
from ..auth.middleware import get_current_user
from ..models.entities import User
from ..agents.todo_agent import TodoAgent
from ..services.conversation_service import ConversationService
from ..models.conversation import ConversationCreate
from ..models.message import MessageCreate
from sqlmodel import Session
from ..models.database import get_db
from datetime import datetime
from typing import Generator


router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None  # Allow specifying an existing conversation


@router.post("/chat", summary="Send a message to the AI and get a response")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process a user's natural language message and return an AI-generated response.
    This endpoint requires authentication.
    """
    try:
        # Create an instance of the TodoAgent
        agent = TodoAgent()

        # Create or get conversation for this user
        try:
            conversation_service = ConversationService()
        except Exception as e:
            print(f"Error initializing conversation service: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Service temporarily unavailable. Please try again later."
            )

        # Check if a specific conversation was requested, otherwise create a new one
        if request.conversation_id:
            try:
                # Try to get the existing conversation
                conversation = conversation_service.get_conversation_by_id(
                    db,
                    request.conversation_id
                )

                # Verify that the conversation belongs to the current user
                if not conversation or conversation.user_id != current_user.id:
                    raise HTTPException(
                        status_code=404,
                        detail="Conversation not found or does not belong to user"
                    )
            except HTTPException:
                raise
            except Exception as e:
                print(f"Error retrieving conversation: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail="Error retrieving conversation. Please try creating a new chat."
                )
        else:
            try:
                # Create a new conversation
                conversation_data = ConversationCreate(
                    user_id=current_user.id
                )
                conversation = conversation_service.create_conversation(db, conversation_data)
            except Exception as e:
                print(f"Error creating conversation: {str(e)}")
                import traceback
                print(f"Full traceback: {traceback.format_exc()}")
                raise HTTPException(
                    status_code=500,
                    detail="Error creating conversation. Please try again."
                )

        # Add user's message to the conversation
        try:
            user_message_data = MessageCreate(
                conversation_id=conversation.id,
                role="user",
                content=request.message
            )
            user_message = conversation_service.add_message_to_conversation(
                db,
                conversation.id,
                user_message_data
            )
        except Exception as e:
            print(f"Error adding user message to conversation: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error saving your message. Please try again."
            )

        # Process the message with the agent
        try:
            ai_response = agent.process_message(
                user_id=current_user.id,
                message=request.message,
                conversation_id=conversation.id
            )
        except Exception as e:
            print(f"Error processing message with AI agent: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error processing your message with the AI assistant. Please try again."
            )

        # Add AI's response to the conversation
        try:
            ai_message_data = MessageCreate(
                conversation_id=conversation.id,
                role="assistant",
                content=ai_response
            )
            ai_message = conversation_service.add_message_to_conversation(
                db,
                conversation.id,
                ai_message_data
            )
        except Exception as e:
            print(f"Error adding AI response to conversation: {str(e)}")
            # Still return the response even if we can't save it to the conversation
            # This prevents the user from thinking the request failed
            return {
                "response": ai_response,
                "conversation_id": conversation.id,
                "timestamp": datetime.utcnow().isoformat(),
                "warning": "Response generated but could not be saved to conversation history"
            }

        # Return the AI's response
        return {
            "response": ai_response,
            "conversation_id": conversation.id,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        # Re-raise HTTP exceptions (like auth errors)
        raise
    except Exception as e:
        # Log the detailed error for debugging
        import traceback
        error_details = traceback.format_exc()
        print(f"Detailed error processing chat message: {error_details}")

        # Determine the specific type of error to provide better feedback
        error_msg = str(e)
        status_code = 500

        if "OPENROUTER_API_KEY" in error_msg or "environment variable" in error_msg:
            status_code = 500
            error_msg = "Configuration error: AI service is not properly configured. Please contact the administrator."
        elif "database" in error_msg.lower() or "connection" in error_msg.lower():
            status_code = 500
            error_msg = "Database connection error. Please try again later."
        elif "authentication" in error_msg.lower() or "401" in error_msg:
            status_code = 401
            error_msg = "Authentication failed. Please sign in again."
        elif "conversation" in error_msg.lower():
            status_code = 404
            error_msg = "Conversation not found or access denied."
        else:
            status_code = 500
            error_msg = "An error occurred while processing your request. Please try again."

        raise HTTPException(
            status_code=status_code,
            detail=error_msg
        )


# Additional endpoint to get conversation history (useful for frontend)
@router.get("/conversations", summary="Get user's conversation history")
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve the user's conversation history.
    This endpoint requires authentication.
    """
    try:
        try:
            conversation_service = ConversationService()
        except Exception as e:
            print(f"Error initializing conversation service: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Service temporarily unavailable. Please try again later."
            )

        # Get conversations for this user
        try:
            conversations = conversation_service.get_conversations_by_user(
                db,
                current_user.id
            )
        except Exception as e:
            print(f"Error retrieving conversations from database: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error retrieving conversation history. Please try again."
            )

        return {
            "conversations": [
                {
                    "id": conv.id,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat()
                }
                for conv in conversations
            ],
            "count": len(conversations)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error retrieving conversations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving conversations"
        )