#!/usr/bin/env python3
"""
Direct script to fix the database schema using raw SQL.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def fix_database_schema():
    """Direct fix for the database schema using raw SQL."""
    print("[INFO] Fixing Database Schema with Raw SQL...")

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
                result = conn.execute(text("SELECT * FROM todo ORDER BY created_at")).fetchall()
                existing_todos = [dict(row._mapping) for row in result]
                print(f"  [INFO] Found {len(existing_todos)} existing todos to preserve")

            # Drop the todo table
            print("  [INFO] Dropping todo table...")
            try:
                # Use a more forceful approach to drop the table
                conn.execute(text("DROP TABLE IF EXISTS todo CASCADE"))
            except Exception as e:
                print(f"  [WARN] Error dropping todo table: {e}")

            # Now recreate the todo table with correct foreign key constraint
            print("  [INFO] Creating todo table with correct foreign key to 'users' table...")

            # Create todo table with proper foreign key reference to 'users' table
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
                print(f"  [INFO] Attempting to restore {len(existing_todos)} todos...")

                for i, todo in enumerate(existing_todos):
                    try:
                        # Insert the todo record - for now, let's just try to create it
                        # We'll handle user validation later if needed
                        insert_sql = """
                        INSERT INTO todo (id, user_id, title, description, is_complete, created_at, updated_at, completed_at, due_date)
                        VALUES (%(id)s, %(user_id)s, %(title)s, %(description)s, %(is_complete)s, %(created_at)s, %(updated_at)s, %(completed_at)s, %(due_date)s)
                        """

                        conn.execute(text(insert_sql), {
                            'id': str(todo['id']),
                            'user_id': str(todo['user_id']),
                            'title': str(todo['title']),
                            'description': todo.get('description'),
                            'is_complete': bool(todo['is_complete']),
                            'created_at': todo['created_at'],
                            'updated_at': todo['updated_at'],
                            'completed_at': todo.get('completed_at'),
                            'due_date': todo.get('due_date')
                        })

                        print(f"    [INFO] Restored todo {i+1}/{len(existing_todos)}: {todo['title']}")
                    except Exception as e:
                        print(f"    [WARN] Could not restore todo '{todo['title']}': {e}")
                        # Continue with other todos

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
    print("[INFO] Starting Direct Database Schema Fix...\n")

    success = fix_database_schema()

    if success:
        print(f"\n[SUCCESS] Database schema has been fixed!")
        print("The todo table now has the correct foreign key reference to the 'users' table.")
        print("Todo creation should now work properly.")
    else:
        print(f"\n[ERROR] Database schema fix failed!")

if __name__ == "__main__":
    main()