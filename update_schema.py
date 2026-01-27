#!/usr/bin/env python3
"""
Script to update the database schema to match the current models.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def update_schema():
    """Update the database schema to match current models."""
    print("[INFO] Updating Database Schema...")

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

        # Since we can't easily modify foreign key constraints in SQLite/PostgreSQL,
        # we'll need to recreate the todo table with the correct foreign key
        # But first, let's back up the existing todo data

        with sync_engine.connect() as conn:
            trans = conn.begin()

            # Check if we have todo data to preserve
            if 'todo' in tables:
                result = conn.execute(text("SELECT COUNT(*) FROM todo")).scalar()
                print(f"  [INFO] Found {result} todo records to preserve")

                if result > 0:
                    # Create a temporary table to hold todo data
                    conn.execute(text("""
                        CREATE TEMPORARY TABLE temp_todos_backup AS
                        SELECT * FROM todo
                    """))

                    print("  [INFO] Backed up todo data to temporary table")

            # Drop the todo table
            if 'todo' in tables:
                conn.execute(text("DROP TABLE IF EXISTS todo CASCADE"))
                print("  [INFO] Dropped todo table")

            # Now recreate all tables using SQLModel metadata
            from backend.src.models import init_db
            init_db()

            # Check if todo table was recreated
            new_inspector = inspect(sync_engine)
            new_tables = new_inspector.get_table_names()

            if 'todo' in new_tables:
                print("  [INFO] Todo table recreated")

                # Check the foreign key constraint
                fk_constraints = new_inspector.get_foreign_keys('todo')
                print(f"  [INFO] New foreign key constraints: {[(fk['constrained_columns'], fk['referred_table'], fk['referred_columns']) for fk in fk_constraints]}")

                # If we had backed up data, restore it (but map user_id correctly)
                if 'temp_todos_backup' in [row[0] for row in conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'pg_temp'"))]:
                    # Get the data from the temporary table
                    result = conn.execute(text("SELECT * FROM temp_todos_backup"))
                    columns = result.keys()
                    todo_data = result.fetchall()

                    if todo_data:
                        print(f"  [INFO] Restoring {len(todo_data)} todo records")

                        # Insert the data back, but we need to make sure user_id references exist in 'users' table
                        for row in todo_data:
                            # Convert row to dict-like structure
                            row_dict = dict(zip(columns, row))

                            # Check if user_id exists in 'users' table
                            user_check = conn.execute(text("SELECT id FROM users WHERE id = %s"), (row_dict['user_id'],)).fetchone()

                            if user_check:
                                # User exists, insert the todo
                                conn.execute(text("""
                                    INSERT INTO todo (id, user_id, title, description, is_complete, created_at, updated_at, completed_at, due_date)
                                    VALUES (%(id)s, %(user_id)s, %(title)s, %(description)s, %(is_complete)s, %(created_at)s, %(updated_at)s, %(completed_at)s, %(due_date)s)
                                """), row_dict)
                            else:
                                print(f"  [WARN] User {row_dict['user_id']} not found in 'users' table, skipping todo")

            trans.commit()

        print("  [SUCCESS] Schema updated successfully")

        # Verify the new structure
        final_inspector = inspect(sync_engine)
        final_tables = final_inspector.get_table_names()
        print(f"  [INFO] Final tables: {final_tables}")

        if 'todo' in final_tables:
            fk_constraints = final_inspector.get_foreign_keys('todo')
            print(f"  [INFO] Final todo FK constraints: {[(fk['constrained_columns'], fk['referred_table'], fk['referred_columns']) for fk in fk_constraints]}")

        return True

    except Exception as e:
        print(f"  [ERROR] Schema update failed: {str(e)}")
        import traceback
        print(f"  [DEBUG] Full traceback: {traceback.format_exc()}")
        return False

def main():
    """Run schema update."""
    print("[INFO] Starting Schema Update...\n")

    success = update_schema()

    if success:
        print(f"\n[SUCCESS] Schema update completed!")
        print("The database should now match the current models.")
    else:
        print(f"\n[ERROR] Schema update failed!")

if __name__ == "__main__":
    main()