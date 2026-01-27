#!/usr/bin/env python3
"""
Script to properly fix the foreign key constraint by recreating the todo table.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def recreate_todo_table():
    """Recreate the todo table with the correct foreign key."""
    print("Recreating todo table with correct foreign key...")

    # Change to backend directory to load .env
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    try:
        from backend.src.models.database import sync_engine
        from sqlalchemy import text

        with sync_engine.connect() as conn:
            trans = conn.begin()

            # Get existing todo data to preserve
            print("Getting existing todo data...")
            todos_result = conn.execute(text("SELECT * FROM todo")).fetchall()
            existing_todos = [dict(row._mapping) for row in todos_result]
            print(f"Found {len(existing_todos)} existing todos to preserve")

            # Get the current foreign key constraint name
            print("Checking current foreign key constraint...")

            # Drop the todo table
            print("Dropping todo table...")
            conn.execute(text("DROP TABLE todo CASCADE"))

            # Create the todo table with the correct foreign key constraint to 'users' table
            print("Creating todo table with correct foreign key to 'users' table...")
            create_table_sql = """
            CREATE TABLE todo (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL,
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

            # Now add the foreign key constraint to the 'users' table
            print("Adding foreign key constraint to 'users' table...")
            fk_sql = """
            ALTER TABLE todo ADD CONSTRAINT fk_todo_user_id
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
            """
            conn.execute(text(fk_sql))

            # Create index for performance
            conn.execute(text("CREATE INDEX idx_todo_user_id ON todo(user_id);"))

            # Restore the todo data if possible
            if existing_todos:
                print(f"Restoring {len(existing_todos)} todos...")

                for todo in existing_todos:
                    # Check if the user exists in the 'users' table before restoring
                    user_exists = conn.execute(
                        text("SELECT 1 FROM users WHERE id = %s"),
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
            print("Table recreated successfully!")

            # Verify the structure
            verify_result = conn.execute(text("""
                SELECT
                    tc.constraint_name,
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM
                    information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                        AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name='todo';
            """)).fetchall()

            print("Foreign key constraints verification:")
            for row in verify_result:
                print(f"  - {row[2]} references {row[3]}.{row[4]}")

        return True

    except Exception as e:
        print(f"Error recreating table: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")

        try:
            trans.rollback()
        except:
            pass

        return False

def main():
    print("Starting todo table recreation...\n")
    success = recreate_todo_table()

    if success:
        print("\nSUCCESS: Todo table has been recreated with correct foreign key!")
        print("The todo table now references the 'users' table correctly.")
    else:
        print("\nFAILED: Table recreation was unsuccessful.")

if __name__ == "__main__":
    main()