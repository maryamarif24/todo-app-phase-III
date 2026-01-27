#!/usr/bin/env python3
"""
Test script to verify database connection and table existence.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def test_database_connection():
    """Test database connection and table existence."""
    print("[INFO] Testing Database Connection and Tables...")

    # Change to backend directory to load .env
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    try:
        from backend.src.models.database import sync_engine, init_db
        from sqlalchemy import inspect

        # Check the database URL
        database_url = os.getenv("DATABASE_URL")
        print(f"  [INFO] Database URL: {database_url[:50]}..." if database_url else "  [INFO] Database URL: Not set")

        # Test connection
        conn = sync_engine.connect()
        print("  [SUCCESS] Database connection successful")
        conn.close()

        # Initialize database (creates tables)
        print("  [INFO] Initializing database...")
        init_db()

        # Check tables
        inspector = inspect(sync_engine)
        tables = inspector.get_table_names()
        print(f"  [INFO] Available tables: {tables}")

        expected_tables = ['users', 'todos']
        missing_tables = [table for table in expected_tables if table not in tables]

        if missing_tables:
            print(f"  [ERROR] Missing expected tables: {missing_tables}")
            return False
        else:
            print("  [SUCCESS] All expected tables exist")

        # Test table structure
        from sqlalchemy import text

        # Check users table structure
        if 'users' in tables:
            user_columns = inspector.get_columns('users')
            user_column_names = [col['name'] for col in user_columns]
            print(f"  [INFO] Users table columns: {user_column_names}")

        # Check todos table structure
        if 'todos' in tables:
            todo_columns = inspector.get_columns('todos')
            todo_column_names = [col['name'] for col in todo_columns]
            print(f"  [INFO] Todos table columns: {todo_column_names}")

        return True

    except Exception as e:
        print(f"  [ERROR] Database test failed: {str(e)}")
        import traceback
        print(f"  [DEBUG] Full traceback: {traceback.format_exc()}")
        return False

def test_todo_creation_directly():
    """Test todo creation directly using the service layer."""
    print("\n[INFO] Testing Todo Creation Directly...")

    try:
        from backend.src.models.database import get_db
        from backend.src.services.todo_service import create_todo
        import uuid

        # Create a database session
        from backend.src.models.database import sync_engine
        from sqlmodel import Session

        with Session(sync_engine) as session:
            # Create a fake user ID for testing
            fake_user_id = uuid.uuid4()

            print(f"  [INFO] Attempting to create todo for user: {fake_user_id}")

            # Try to create a todo
            todo = create_todo(
                session,
                fake_user_id,
                "Test Todo",
                "This is a test todo"
            )

            print(f"  [SUCCESS] Todo object created in memory: {todo.title}")

            # Try to add to session and commit
            session.add(todo)
            session.commit()
            session.refresh(todo)

            print(f"  [SUCCESS] Todo saved to database with ID: {todo.id}")
            return True

    except Exception as e:
        print(f"  [ERROR] Direct todo creation failed: {str(e)}")
        import traceback
        print(f"  [DEBUG] Full traceback: {traceback.format_exc()}")
        return False

def main():
    """Run database tests."""
    print("[INFO] Starting Database Tests...\n")

    tests = [
        ("Database Connection and Tables", test_database_connection),
        ("Direct Todo Creation", test_todo_creation_directly),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  [CRASH] {test_name} crashed: {str(e)}")
            results.append((test_name, False))

    print(f"\n[SUMMARY] Database Test Results:")
    all_passed = True
    for test_name, passed in results:
        status = "  [PASS]" if passed else "  [FAIL]"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False

    print(f"\n{'[SUCCESS] All tests passed!' if all_passed else '[WARNING] Some tests failed. Please check the output above for details.'}")

if __name__ == "__main__":
    main()