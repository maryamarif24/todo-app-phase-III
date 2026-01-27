#!/usr/bin/env python3
"""
Script to restart the backend server and ensure database schema is updated.
"""

import subprocess
import sys
import time
import requests
import os
from pathlib import Path

def kill_existing_servers():
    """Kill any existing backend servers running on port 8000."""
    print("[INFO] Killing any existing servers on port 8000...")

    try:
        # On Windows, use netstat and taskkill
        import platform
        if platform.system().lower() == "windows":
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            lines = result.stdout.split('\n')

            for line in lines:
                if ':8000' in line and 'LISTENING' in line:
                    # Extract PID
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[4]
                        print(f"  [INFO] Killing process {pid} on port 8000...")
                        subprocess.run(['taskkill', '/PID', pid, '/F'], capture_output=True)
                        break
    except Exception as e:
        print(f"  [WARN] Could not kill existing servers: {e}")

def start_backend_server():
    """Start the backend server."""
    print("[INFO] Starting backend server...")

    # Change to backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)

    # Start the server in a subprocess
    cmd = [sys.executable, "-m", "uvicorn", "src.main:app", "--reload", "--port", "8000"]

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Give it a moment to start
        time.sleep(3)

        # Check if it started successfully
        poll_result = process.poll()
        if poll_result is None:
            print("  [SUCCESS] Backend server started successfully on port 8000")
            print("  [INFO] Server PID:", process.pid)

            # Try to access the health endpoint to verify it's running
            try:
                response = requests.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    print("  [SUCCESS] Health check passed - server is responsive")
                    return process
                else:
                    print(f"  [WARN] Health check failed with status {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"  [WARN] Could not reach server: {e}")

            return process
        else:
            # Server failed to start, get error output
            _, stderr = process.communicate()
            print(f"  [ERROR] Server failed to start. Error output: {stderr}")
            return None

    except Exception as e:
        print(f"  [ERROR] Failed to start server: {e}")
        return None

def test_todo_creation():
    """Test todo creation after server restart."""
    print("\n[INFO] Testing todo creation after server restart...")

    try:
        # First, create a test user
        api_url = "http://localhost:8000"

        import random
        test_email = f"testuser_{random.randint(1000, 9999)}@example.com"
        test_password = "Password123!"

        # Sign up the user
        signup_data = {
            "email": test_email,
            "password": test_password
        }

        print(f"  [INFO] Creating test user: {test_email}")
        signup_response = requests.post(f"{api_url}/auth/signup", json=signup_data, timeout=10)

        if signup_response.status_code != 201:
            print(f"  [ERROR] Signup failed: {signup_response.status_code}, {signup_response.text}")
            return False

        signup_result = signup_response.json()
        auth_token = signup_result["session"]["token"]

        print("  [SUCCESS] User created successfully")

        # Now try to create a todo
        todo_data = {
            "title": "Test todo after server restart",
            "description": "This is a test todo created after server restart"
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }

        print("  [INFO] Creating todo with authenticated user...")
        todo_response = requests.post(f"{api_url}/todos", json=todo_data, headers=headers, timeout=10)

        if todo_response.status_code == 201:
            todo_result = todo_response.json()
            print(f"  [SUCCESS] Todo created successfully: {todo_result['title']}")
            print(f"  [INFO] Todo ID: {todo_result['id']}")
            return True
        else:
            print(f"  [ERROR] Todo creation failed: {todo_response.status_code}")
            try:
                error_text = todo_response.json()
                print(f"  [ERROR] Error details: {error_text}")
            except:
                print(f"  [ERROR] Error details: {todo_response.text}")
            return False

    except Exception as e:
        print(f"  [ERROR] Test failed with exception: {str(e)}")
        import traceback
        print(f"  [DEBUG] Full traceback: {traceback.format_exc()}")
        return False

def main():
    """Main function to restart server and test."""
    print("[INFO] Starting Backend Server Restart Process...\n")

    # Kill any existing servers
    kill_existing_servers()

    # Wait a moment
    time.sleep(2)

    # Start the new server
    server_process = start_backend_server()

    if server_process:
        print("\n[INFO] Server is now running. You can test the todo creation functionality.")
        print("Keep this server running while testing.")

        # Optionally test the functionality
        print("\n[INFO] Running automated test...")
        success = test_todo_creation()

        if success:
            print("\n[SUCCESS] Todo creation is now working!")
            print("The schema changes have been applied successfully.")
        else:
            print("\n[ERROR] Todo creation is still failing.")
            print("There may be other issues that need to be addressed.")

        # Keep the server running or let the user decide
        print(f"\n[INFO] Server is running on PID {server_process.pid}")
        print("[INFO] You can continue using the server or press Ctrl+C to stop it.")

        try:
            # Wait for user to stop the server
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[INFO] Shutting down server...")
            server_process.terminate()
            server_process.wait()
            print("[INFO] Server stopped.")
    else:
        print("\n[ERROR] Could not start the backend server.")
        print("Please start it manually with: python -m uvicorn src.main:app --reload --port 8000")

if __name__ == "__main__":
    main()