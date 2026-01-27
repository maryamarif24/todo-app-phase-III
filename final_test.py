#!/usr/bin/env python3
"""
Final test to verify the todo creation functionality.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def test_with_models():
    """Test using the actual application models."""
    print("Testing with application models...")

    # Change to backend directory to load .env
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    try:
        # Import the database session and models
        from backend.src.models.database import get_db
        from backend.src.models.entities import User, Todo
        from backend.src.services.todo_service import create_todo
        from sqlmodel import Session
        import uuid

        # Get the sync engine directly
        from backend.src.models.database import sync_engine

        with Session(sync_engine) as session:
            # Create a test user in the users table
            test_user_id = uuid.uuid4()
            test_user = User(
                id=test_user_id,
                email=f"test_{uuid.uuid4().hex[:8]}@example.com",
                password_hash="$2b$12$dummy_hash_for_testing_purposes_only_that_meets_min_length_requirement"
            )

            session.add(test_user)
            session.commit()
            session.refresh(test_user)

            print(f"Created test user: {test_user.email}")

            # Now try to create a todo for this user using the service
            todo = create_todo(
                session,
                test_user.id,
                "Test todo using models",
                "This is a test todo created using the proper models"
            )

            # Add to session and commit
            session.add(todo)
            session.commit()
            session.refresh(todo)

            print(f"SUCCESS: Created todo using models: {todo.title}")
            print(f"  Todo ID: {todo.id}")
            print(f"  User ID: {todo.user_id}")
            return True

    except Exception as e:
        print(f"FAILED: Error using models: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

def main():
    print("Starting final test with models...\n")

    success = test_with_models()

    if success:
        print("\nSUCCESS: Models are working correctly!")
        print("The foreign key relationship between Todo and User is properly configured.")
    else:
        print("\nFAILED: There are still issues with the models.")

if __name__ == "__main__":
    main()