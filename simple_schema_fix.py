#!/usr/bin/env python3
"""
Simple script to fix the database schema by dropping and recreating the todo table.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def fix_database_schema():
    """Simple fix for the database schema."""
    print("[INFO] Fixing Database Schema...")

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

        with sync_engine.connect() as conn:
            trans = conn.begin()

            # Check if there are existing todos to preserve
            existing_todos = []
            if 'todo' in tables:
                result = conn.execute(text("SELECT * FROM todo")).fetchall()
                existing_todos = [dict(row._mapping) for row in result]
                print(f"  [INFO] Found {len(existing_todos)} existing todos to preserve")

            # Drop the todo table
            print("  [INFO] Dropping todo table...")
            # First drop any dependent objects/indexes, then the table itself
            try:
                conn.execute(text("DROP TABLE IF EXISTS todo CASCADE"))
            except Exception as e:
                print(f"  [WARN] Error dropping todo table: {e}")

            # Now recreate the todo table with correct foreign key constraint
            print("  [INFO] Creating todo table with correct foreign key to 'users' table...")

            # Create todo table with foreign key to 'users' table instead of 'user' table
            # First, make sure the users table exists and check its structure
            users_columns = inspector.get_columns('users')
            print(f"  [INFO] Users table columns: {[col['name'] for col in users_columns]}")

            # Create todo table with proper foreign key reference
            create_todo_table_sql = """
            CREATE TABLE todo (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(200) NOT NULL,
                description VARCHAR(2000),
                is_complete BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP NULL,
                due_date TIMESTAMP NULL
            );
            """

            conn.execute(text(create_todo_table_sql))

            # Create index on user_id for performance
            conn.execute(text("CREATE INDEX idx_todo_user_id ON todo(user_id);"))

            # If we had existing todos, try to restore them
            if existing_todos:
                print(f"  [INFO] Restoring {len(existing_todos)} todos...")

                for todo in existing_todos:
                    # Check if the user exists in the 'users' table before inserting
                    user_check = conn.execute(
                        text("SELECT id FROM users WHERE id = %s"),
                        (todo['user_id'],)
                    ).fetchone()

                    if user_check:
                        # Insert the todo record
                        insert_sql = """
                        INSERT INTO todo (id, user_id, title, description, is_complete, created_at, updated_at, completed_at, due_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """

                        conn.execute(text(insert_sql), (
                            todo['id'],
                            todo['user_id'],
                            todo['title'],
                            todo.get('description'),
                            todo['is_complete'],
                            todo['created_at'],
                            todo['updated_at'],
                            todo.get('completed_at'),
                            todo.get('due_date')
                        ))
                        print(f"    [INFO] Restored todo: {todo['title']}")
                    else:
                        print(f"    [WARN] User {todo['user_id']} not found in 'users' table, skipping todo: {todo['title']}")

            trans.commit()
            print("  [SUCCESS] Database schema fixed successfully")

            # Verify the new structure
            new_inspector = inspect(sync_engine)
            new_tables = new_inspector.get_table_names()
            print(f"  [INFO] New tables: {new_tables}")

            if 'todo' in new_tables:
                new_fk_constraints = new_inspector.get_foreign_keys('todo')
                print(f"  [INFO] New foreign key constraints: {[(fk['constrained_columns'], fk['referred_table'], fk['referred_columns']) for fk in new_fk_constraints]}")

        return True

    except Exception as e:
        print(f"  [ERROR] Schema fix failed: {str(e)}")
        import traceback
        print(f"  [DEBUG] Full traceback: {traceback.format_exc()}")

        try:
            trans.rollback()
        except:
            pass

        return False

def main():
    """Run schema fix."""
    print("[INFO] Starting Database Schema Fix...\n")

    success = fix_database_schema()

    if success:
        print(f"\n[SUCCESS] Database schema has been fixed!")
        print("The todo table now has the correct foreign key reference to the 'users' table.")
        print("Todo creation should now work properly.")
    else:
        print(f"\n[ERROR] Database schema fix failed!")

if __name__ == "__main__":
    main()