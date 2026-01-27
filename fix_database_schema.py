#!/usr/bin/env python3
"""
Script to fix the database schema by dropping and recreating the todo table with correct foreign key.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def fix_database_schema():
    """Fix the database schema by recreating the todo table with correct foreign key."""
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
        import uuid

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

                # Store users that are referenced by todos
                referenced_user_ids = list(set([todo['user_id'] for todo in existing_todos]))

                # Check which user table has these users
                users_in_users_table = []
                users_in_user_table = []

                for user_id in referenced_user_ids:
                    user_in_users = conn.execute(text("SELECT * FROM users WHERE id = %s"), (user_id,)).fetchone()
                    if user_in_users:
                        users_in_users_table.append(dict(user_in_users._mapping))

                    user_in_user = conn.execute(text("SELECT * FROM user WHERE id = %s"), (user_id,)).fetchone()
                    if user_in_user:
                        users_in_user_table.append(dict(user_in_user._mapping))

                print(f"  [INFO] Referenced users in 'users' table: {len(users_in_users_table)}")
                print(f"  [INFO] Referenced users in 'user' table: {len(users_in_user_table)}")

            # Drop the todo table
            print("  [INFO] Dropping todo table...")
            conn.execute(text("DROP TABLE IF EXISTS todo CASCADE"))

            # Now recreate the todo table with correct foreign key constraint
            print("  [INFO] Creating todo table with correct foreign key to 'users' table...")

            # Create todo table with foreign key to 'users' table instead of 'user' table
            create_todo_table_sql = """
            CREATE TABLE todo (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL,
                title VARCHAR(200) NOT NULL,
                description VARCHAR(2000),
                is_complete BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP NULL,
                due_date TIMESTAMP NULL,
                CONSTRAINT fk_todo_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
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
                    user_exists = conn.execute(
                        text("SELECT 1 FROM users WHERE id = %s"),
                        (todo['user_id'],)
                    ).fetchone()

                    if user_exists:
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
            new_fk_constraints = new_inspector.get_foreign_keys('todo')
            print(f"  [INFO] New foreign key constraints: {[(fk['constrained_columns'], fk['referred_table'], fk['referred_columns']) for fk in new_fk_constraints]}")

        return True

    except Exception as e:
        print(f"  [ERROR] Schema fix failed: {str(e)}")
        import traceback
        print(f"  [DEBUG] Full traceback: {traceback.format_exc()}")

        # Try to rollback if connection is still open
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