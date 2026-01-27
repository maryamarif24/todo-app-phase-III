#!/usr/bin/env python3
"""Simple script to start the backend server."""

import os
import sys
import subprocess
from pathlib import Path

# Change to backend directory
backend_dir = Path(__file__).parent / "backend"
os.chdir(backend_dir)

# Set environment variables
os.environ['DATABASE_URL'] = os.environ.get('DATABASE_URL',
    'postgresql://neondb_owner:npg_cQqgN21neoJU@ep-lingering-boat-ah4x1tsd-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require')

# Start the uvicorn server
cmd = [
    sys.executable,
    '-m',
    'uvicorn',
    'src.main:app',
    '--host', '0.0.0.0',
    '--port', '8000',
    '--reload'
]

print("Starting backend server on http://localhost:8000")
print("Command:", " ".join(cmd))

try:
    result = subprocess.run(cmd)
    sys.exit(result.returncode)
except KeyboardInterrupt:
    print("\nServer stopped by user")
    sys.exit(0)