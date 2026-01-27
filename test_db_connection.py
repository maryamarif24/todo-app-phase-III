#!/usr/bin/env python3
"""Test script to check database connectivity and todo creation"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.src.models.database import init_db, sync_engine
from backend.src.models.entities import Todo, User
from backend.src.services.todo_service import create_todo
from sqlmodel import Session, select
import uuid

def test_database():
    print("Testing database connection...")
    
    try:
        # Initialize the database
        init_db()
        print("Database initialization completed")
        
        # Test basic connection
        with Session(sync_engine) as session:
            print("Connected to database successfully")
            
            # Check if users table has any records
            users = session.exec(select(User)).all()
            print(f"Found {len(users)} users in database")
            
            # Try to create a mock todo object (without saving)
            mock_user_id = uuid.uuid4()
            todo = create_todo(session, mock_user_id, "Test Title", "Test Description")
            print(f"Created todo object in memory: {todo.title}")
            
    except Exception as e:
        print(f"Database error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database()
