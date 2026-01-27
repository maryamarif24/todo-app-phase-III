#!/usr/bin/env python3
"""
Script to reset the database tables to match the current models.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def reset_database():
    """Reset the database tables to match current models."""
    print("[INFO] Resetting Database Tables...")

    # Change to backend directory to load .env
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    try:
        from backend.src.models.database import sync_engine
        from sqlalchemy import inspect, text

        # Get table information
        inspector = inspect(sync_engine)
        tables = inspector.get_table_names()

        print(f"  [INFO] Current tables: {tables}")

        # Drop tables in correct order (due to foreign key constraints)
        # Need to drop child tables first
        tables_to_drop = ['todo', 'todos', 'message', 'messages', 'conversation']  # Adjust as needed

        with sync_engine.connect() as conn:
            trans = conn.begin()

            for table_name in tables_to_drop:
                if table_name in tables:
                    try:
                        print(f"  [INFO] Dropping table: {table_name}")
                        conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE'))
                    except Exception as e:
                        print(f"  [INFO] Table {table_name} doesn't exist or couldn't be dropped: {e}")

            # Also drop user tables (be careful with this!)
            user_tables = ['user', 'users']
            for table_name in user_tables:
                if table_name in tables:
                    # Only drop if it's not the main user table we want to keep some data from
                    print(f"  [INFO] Found user table: {table_name}")

            trans.commit()

        print("  [INFO] Tables dropped successfully")

        # Now recreate tables using SQLModel metadata
        from backend.src.models import init_db
        print("  [INFO] Recreating tables based on models...")
        init_db()

        # Check the new table structure
        inspector = inspect(sync_engine)
        new_tables = inspector.get_table_names()
        print(f"  [INFO] New tables: {new_tables}")

        # Check the structure of the recreated tables
        if 'user' in new_tables:
            user_columns = inspector.get_columns('user')
            print(f"  [INFO] 'user' table columns: {[col['name'] for col in user_columns]}")

        if 'todo' in new_tables:
            todo_columns = inspector.get_columns('todo')
            print(f"  [INFO] 'todo' table columns: {[col['name'] for col in todo_columns]}")

            # Check foreign key constraints
            fk_constraints = inspector.get_foreign_keys('todo')
            print(f"  [INFO] 'todo' foreign keys: {[(fk['constrained_columns'], fk['referred_table'], fk['referred_columns']) for fk in fk_constraints]}")

        return True

    except Exception as e:
        print(f"  [ERROR] Database reset failed: {str(e)}")
        import traceback
        print(f"  [DEBUG] Full traceback: {traceback.format_exc()}")
        return False

def main():
    """Run database reset."""
    print("[INFO] Starting Database Reset...\n")

    success = reset_database()

    if success:
        print(f"\n[SUCCESS] Database reset completed!")
        print("Tables should now match the current models.")
    else:
        print(f"\n[ERROR] Database reset failed!")

if __name__ == "__main__":
    main()