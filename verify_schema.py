#!/usr/bin/env python3
"""
Script to verify the current database schema state.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def verify_schema():
    """Verify the current database schema."""
    print("Verifying database schema...")

    # Change to backend directory to load .env
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    try:
        from backend.src.models.database import sync_engine
        from sqlalchemy import inspect

        # Get table information
        inspector = inspect(sync_engine)
        tables = inspector.get_table_names()

        print(f"Current tables: {tables}")

        # Check foreign key constraints for todo table
        if 'todo' in tables:
            print("\nChecking 'todo' table foreign key constraints:")
            fk_constraints = inspector.get_foreign_keys('todo')
            for fk in fk_constraints:
                print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

        # Check both user tables
        if 'user' in tables:
            print("\nChecking 'user' table structure:")
            user_cols = inspector.get_columns('user')
            for col in user_cols:
                print(f"  - {col['name']}: {col['type']} (nullable: {col['nullable']})")

        if 'users' in tables:
            print("\nChecking 'users' table structure:")
            users_cols = inspector.get_columns('users')
            for col in users_cols:
                print(f"  - {col['name']}: {col['type']} (nullable: {col['nullable']})")

        # Count records in both user tables
        with sync_engine.connect() as conn:
            if 'user' in tables:
                count_user = conn.execute(inspector.bind.dialect.statement_compiler(inspector.bind.dialect, None).process(inspector.bind.dialect.select([inspector.bind.dialect.literal_column("COUNT(*)")], from_obj=inspector.bind.dialect.table("user")))).scalar()
                print(f"\nRecords in 'user' table: {count_user}")

            if 'users' in tables:
                count_users = conn.execute(inspector.bind.dialect.statement_compiler(inspector.bind.dialect, None).process(inspector.bind.dialect.select([inspector.bind.dialect.literal_column("COUNT(*)")], from_obj=inspector.bind.dialect.table("users")))).scalar()
                print(f"Records in 'users' table: {count_users}")

    except Exception as e:
        print(f"Error verifying schema: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")

def main():
    print("Starting schema verification...\n")
    verify_schema()

if __name__ == "__main__":
    main()