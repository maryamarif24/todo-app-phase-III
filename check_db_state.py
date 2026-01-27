#!/usr/bin/env python3
"""
Simple script to check the current database state.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def check_db_state():
    """Check the current database state."""
    print("Checking database state...")

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

        print(f"Current tables: {tables}")

        # Check foreign key constraints for todo table
        if 'todo' in tables:
            print("\n'Verifying 'todo' table foreign key constraints:")
            fk_constraints = inspector.get_foreign_keys('todo')
            print(f"Foreign key constraints for 'todo' table:")
            for fk in fk_constraints:
                print(f"  - Columns {fk['constrained_columns']} reference table '{fk['referred_table']}', columns {fk['referred_columns']}")

        # Check which user table exists and has data
        with sync_engine.connect() as conn:
            for table_name in ['user', 'users']:
                if table_name in tables:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                    print(f"Records in '{table_name}' table: {result}")

                    # Show sample of user IDs if any exist
                    if result > 0:
                        sample = conn.execute(text(f"SELECT id, email FROM {table_name} LIMIT 3")).fetchall()
                        print(f"Sample users from '{table_name}' table:")
                        for user in sample:
                            print(f"  - ID: {user[0]}, Email: {user[1]}")

    except Exception as e:
        print(f"Error checking database state: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")

def main():
    print("Starting database state check...\n")
    check_db_state()

if __name__ == "__main__":
    main()