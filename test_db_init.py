import sys
import os

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

os.environ['FRONTEND_URL'] = 'http://localhost:3000'
os.environ['DATABASE_URL'] = 'sqlite:///../test.db'

from backend.src.models.database import sync_engine
from sqlalchemy import inspect

print("Creating tables...")
from backend.src.models.database import init_db
init_db()

print("Checking tables...")
inspector = inspect(sync_engine)
tables = inspector.get_table_names()
print('Tables in database:', tables)

# Check columns in the conversation table
if 'conversation' in tables:
    columns = inspector.get_columns('conversation')
    print('Columns in conversation table:', [col['name'] for col in columns])

    # Check foreign keys for conversation table
    foreign_keys = inspector.get_foreign_keys('conversation')
    print('Foreign keys in conversation table:', foreign_keys)
else:
    print('No conversation table found')

# Also check the users table
if 'users' in tables:
    columns = inspector.get_columns('users')
    print('Columns in users table:', [col['name'] for col in columns])
else:
    print('No users table found')