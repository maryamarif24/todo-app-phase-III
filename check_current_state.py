#!/usr/bin/env python3
"""
Quick test to verify current database state and foreign key constraints.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def check_current_state():
    """Check the current database state."""
    print("[INFO] Checking Current Database State...")

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

        # Check foreign key constraints for todo table specifically
        print("\n[INFO] Checking 'todo' table foreign key constraints:")
        fk_constraints = inspector.get_foreign_keys('todo')
        for fk in fk_constraints:
            print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

        # Check which user tables exist
        tables = inspector.get_table_names()
        user_tables = [t for t in tables if 'user' in t.lower()]
        print(f"\n[INFO] User-related tables: {user_tables}")

        # Check columns of both user tables if they exist
        for table_name in user_tables:
            columns = inspector.get_columns(table_name)
            column_names = [col['name'] for col in columns]
            print(f"  - {table_name}: {column_names}")

        return True

    except Exception as e:
        print(f"  [ERROR] State check failed: {str(e)}")
        import traceback
        print(f"  [DEBUG] Full traceback: {traceback.format_exc()}")
        return False

def main():
    print("[INFO] Starting Current State Check...\n")

    success = check_current_state()

    if success:
        print(f"\n[SUCCESS] State check completed!")
    else:
        print(f"\n[ERROR] State check failed!")

if __name__ == "__main__":
    main()