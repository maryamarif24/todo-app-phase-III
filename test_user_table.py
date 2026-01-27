#!/usr/bin/env python3
"""
Test script to verify which user table is being used.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def test_user_tables():
    """Test which user table is being used."""
    print("[INFO] Testing User Tables...")

    # Change to backend directory to load .env
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    try:
        from backend.src.models.database import sync_engine
        from sqlalchemy import inspect, text

        # Check the database URL
        database_url = os.getenv("DATABASE_URL")
        print(f"  [INFO] Database URL: {database_url[:50]}..." if database_url else "  [INFO] Database URL: Not set")

        # Test connection and check both user tables
        with sync_engine.connect() as conn:
            # Check users table (plural)
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            users_count = result.scalar()
            print(f"  [INFO] Users table (plural) record count: {users_count}")

            # Check user table (singular)
            result = conn.execute(text("SELECT COUNT(*) FROM user"))
            user_count = result.scalar()
            print(f"  [INFO] User table (singular) record count: {user_count}")

            # If there are records in users table, get some sample data
            if users_count > 0:
                result = conn.execute(text("SELECT id, email FROM users LIMIT 1"))
                sample_user = result.fetchone()
                if sample_user:
                    print(f"  [INFO] Sample user from 'users' table: ID={sample_user[0]}, Email={sample_user[1]}")

            # If there are records in user table, get some sample data
            if user_count > 0:
                result = conn.execute(text("SELECT id, email FROM user LIMIT 1"))
                sample_user = result.fetchone()
                if sample_user:
                    print(f"  [INFO] Sample user from 'user' table: ID={sample_user[0]}, Email={sample_user[1]}")

        return True

    except Exception as e:
        print(f"  [ERROR] User table test failed: {str(e)}")
        import traceback
        print(f"  [DEBUG] Full traceback: {traceback.format_exc()}")
        return False

def test_create_user_and_todo():
    """Test creating a user and then a todo."""
    print("\n[INFO] Testing User Creation and Todo Association...")

    try:
        from backend.src.models.database import sync_engine
        from sqlalchemy import text
        import uuid

        with sync_engine.connect() as conn:
            # Begin a transaction
            trans = conn.begin()

            try:
                # Create a user in the users table (the one with __tablename__ = "users")
                user_id = str(uuid.uuid4())
                email = f"test_{uuid.uuid4().hex[:8]}@example.com"

                insert_user_sql = """
                INSERT INTO users (id, email, password_hash, created_at, updated_at)
                VALUES (%s, %s, %s, NOW(), NOW())
                """

                # Use a dummy password hash (this is just for testing)
                password_hash = "$2b$12$dummy_hash_for_testing_purposes_only"

                conn.execute(text(insert_user_sql), (user_id, email, password_hash))

                print(f"  [SUCCESS] User created in 'users' table: {email}")

                # Now try to create a todo for this user
                todo_id = str(uuid.uuid4())
                insert_todo_sql = """
                INSERT INTO todo (id, user_id, title, description, is_complete, created_at, updated_at, completed_at)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW(), NULL)
                """

                conn.execute(
                    text(insert_todo_sql),
                    (todo_id, user_id, "Test Todo", "This is a test todo", False)
                )

                print(f"  [SUCCESS] Todo created for user: {todo_id}")

                # Commit the transaction
                trans.commit()

                # Verify the todo exists
                result = conn.execute(text("SELECT id, user_id, title FROM todo WHERE id = %s"), (todo_id,))
                todo = result.fetchone()
                if todo:
                    print(f"  [SUCCESS] Verified todo exists: ID={todo[0]}, User_ID={todo[1]}, Title={todo[2]}")

                return True

            except Exception as e:
                # Rollback on error
                trans.rollback()
                raise e

    except Exception as e:
        print(f"  [ERROR] User and todo creation test failed: {str(e)}")
        import traceback
        print(f"  [DEBUG] Full traceback: {traceback.format_exc()}")
        return False

def main():
    """Run user table tests."""
    print("[INFO] Starting User Table Tests...\n")

    tests = [
        ("User Tables Check", test_user_tables),
        ("User and Todo Creation", test_create_user_and_todo),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  [CRASH] {test_name} crashed: {str(e)}")
            results.append((test_name, False))

    print(f"\n[SUMMARY] User Table Test Results:")
    all_passed = True
    for test_name, passed in results:
        status = "  [PASS]" if passed else "  [FAIL]"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False

    print(f"\n{'[SUCCESS] All tests passed!' if all_passed else '[WARNING] Some tests failed. Please check the output above for details.'}")

if __name__ == "__main__":
    main()