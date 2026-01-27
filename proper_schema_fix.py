#!/usr/bin/env python3
"""
Properly fix the database schema by updating the foreign key constraint.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def fix_schema_properly():
    """Properly fix the database schema."""
    print("Fixing database schema properly...")

    # Change to backend directory to load .env
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    try:
        from backend.src.models.database import sync_engine
        from sqlalchemy import inspect, text

        with sync_engine.connect() as conn:
            trans = conn.begin()

            # First, check the current state
            inspector = inspect(sync_engine)

            # Get existing todo data to preserve
            print("Getting existing todo data...")
            todos_result = conn.execute(text("SELECT * FROM todo")).fetchall()
            existing_todos = [dict(row._mapping) for row in todos_result]
            print(f"Found {len(existing_todos)} existing todos to preserve")

            # Drop the todo table
            print("Dropping todo table...")
            conn.execute(text("DROP TABLE todo CASCADE"))

            # Create the todo table with the correct foreign key constraint to 'users' table
            print("Creating todo table with correct foreign key to 'users' table...")
            create_table_sql = """
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
            conn.execute(text(create_table_sql))

            # Create index for performance
            conn.execute(text("CREATE INDEX idx_todo_user_id ON todo(user_id);"))

            # Restore the todo data if possible
            if existing_todos:
                print(f"Restoring {len(existing_todos)} todos...")

                for todo in existing_todos:
                    # Check if the user exists in the 'users' table before restoring
                    user_exists = conn.execute(
                        text("SELECT id FROM users WHERE id = %s"),
                        (str(todo['user_id']),)
                    ).fetchone()

                    if user_exists:
                        # Insert the todo
                        insert_sql = """
                        INSERT INTO todo (id, user_id, title, description, is_complete,
                                         created_at, updated_at, completed_at, due_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """

                        conn.execute(text(insert_sql), (
                            str(todo['id']),
                            str(todo['user_id']),
                            todo['title'],
                            todo.get('description'),
                            todo['is_complete'],
                            todo['created_at'],
                            todo['updated_at'],
                            todo.get('completed_at'),
                            todo.get('due_date')
                        ))
                        print(f"  Restored: {todo['title']}")
                    else:
                        print(f"  Skipped (user not in 'users' table): {todo['title']}")

            trans.commit()
            print("Schema fixed successfully!")

            # Verify the fix
            new_inspector = inspect(sync_engine)
            new_fks = new_inspector.get_foreign_keys('todo')
            print(f"New foreign key constraints: {[(fk['constrained_columns'], fk['referred_table'], fk['referred_columns']) for fk in new_fks]}")

        return True

    except Exception as e:
        print(f"Error fixing schema: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")

        try:
            trans.rollback()
        except:
            pass

        return False

def main():
    print("Starting proper schema fix...\n")
    success = fix_schema_properly()

    if success:
        print("\nSUCCESS: Schema has been properly fixed!")
        print("The todo table now references the 'users' table correctly.")
    else:
        print("\nFAILED: Schema fix was unsuccessful.")

if __name__ == "__main__":
    main()