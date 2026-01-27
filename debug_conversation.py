import os
import sys
import uuid
from datetime import datetime

# Add backend to Python path
sys.path.insert(0, './backend')

# Set environment variables to avoid warnings
os.environ.setdefault('FRONTEND_URL', 'http://localhost:3000')
os.environ.setdefault('DATABASE_URL', os.getenv('DATABASE_URL', 'postgresql://user:password@ep-xyz.region.neon.tech/dbname?sslmode=require'))

from backend.src.models.database import get_db
from backend.src.models.conversation import Conversation, ConversationCreate
from backend.src.services.conversation_service import ConversationService

def test_conversation_creation():
    print("Testing conversation creation...")

    # Get a database session
    db_gen = get_db()
    db = next(db_gen)

    try:
        # Find an existing user in the database
        from backend.src.models.entities import User
        from sqlalchemy import select

        # Query for any existing user
        statement = select(User).limit(1)
        user = db.exec(statement).first()

        if not user:
            print("No users found in database. Creating a test user...")
            # Create a test user
            from backend.src.services.user_service import create_user

            # Create a temporary user for testing
            test_user = create_user(db, "test_chat@example.com", "TestPass123!")
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            user_id = test_user.id
            print(f"Created test user with ID: {user_id}")
        else:
            user_id = user.id
            print(f"Found existing user with ID: {user_id}")

        # Create conversation data
        conversation_data = ConversationCreate(
            user_id=user_id
        )

        print("Attempting to create conversation...")

        # Try to create the conversation
        conversation = ConversationService.create_conversation(db, conversation_data)
        print(f"Success! Created conversation with ID: {conversation.id}")
        return True
    except Exception as e:
        print(f"Error creating conversation: {str(e)}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_conversation_creation()
    if success:
        print("\\nTest PASSED: Conversation creation works!")
    else:
        print("\\nTest FAILED: Conversation creation failed!")