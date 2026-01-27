#!/usr/bin/env python3
"""
Script to check the structure of both user tables.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def check_table_structures():
    """Check the structure of both user tables."""
    print("[INFO] Checking Table Structures...")

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

        # Check 'users' table (plural) structure
        print("\n[INFO] 'users' table (plural) structure:")
        users_columns = inspector.get_columns('users')
        for col in users_columns:
            print(f"  - {col['name']}: {col['type']} (nullable: {col['nullable']})")

        print("\n[INFO] 'user' table (singular) structure:")
        user_columns = inspector.get_columns('user')
        for col in user_columns:
            print(f"  - {col['name']}: {col['type']} (nullable: {col['nullable']})")

        print("\n[INFO] 'todo' table structure:")
        todo_columns = inspector.get_columns('todo')
        for col in todo_columns:
            print(f"  - {col['name']}: {col['type']} (nullable: {col['nullable']})")

        # Check foreign key constraints
        print("\n[INFO] Foreign key constraints for 'todo' table:")
        fk_constraints = inspector.get_foreign_keys('todo')
        for fk in fk_constraints:
            print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

        return True

    except Exception as e:
        print(f"  [ERROR] Table structure check failed: {str(e)}")
        import traceback
        print(f"  [DEBUG] Full traceback: {traceback.format_exc()}")
        return False

def main():
    """Run table structure check."""
    print("[INFO] Starting Table Structure Analysis...\n")

    success = check_table_structures()

    if success:
        print(f"\n[SUCCESS] Table structure analysis completed!")
    else:
        print(f"\n[ERROR] Table structure analysis failed!")

if __name__ == "__main__":
    main()