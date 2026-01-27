#!/usr/bin/env python3
"""Simple test to check database connection"""

import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session, select
from backend.src.models.entities import User, Todo
import uuid
from datetime import datetime

# Load environment variables
load_dotenv(dotenv_path='backend/.env')

# Get database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@ep-xyz.region.neon.tech/dbname?sslmode=require"
)

print(f"Using database URL: {DATABASE_URL[:50]}...")

# Create engine with extend_existing=True to handle conflicts
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Enable to see SQL queries
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10,
    }
)

try:
    # Create tables
    SQLModel.metadata.create_all(engine, checkfirst=True)
    print("Tables created successfully")
    
    # Test connection with a simple query
    with Session(engine) as session:
        print("Connected to database successfully")
        
        # Count users (safe query)
        user_count = session.query(User).count()
        print(f"Number of users in database: {user_count}")
        
        # Try to create a todo object without saving it
        user_id = uuid.uuid4()
        todo = Todo(
            user_id=user_id,
            title="Test Todo",
            description="Test Description",
        )
        print(f"Created todo object: {todo.title}")
        
        # Now try to save it
        session.add(todo)
        session.commit()
        print("Todo saved successfully")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
