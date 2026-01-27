import sys
import os

# Add the backend directory to the Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

# Now run the uvicorn server
import subprocess
import sys

result = subprocess.run([
    sys.executable, '-m', 'uvicorn', 'src.main:app', 
    '--host', '0.0.0.0', 
    '--port', '8000', 
    '--reload'
], cwd=backend_dir)

sys.exit(result.returncode)
