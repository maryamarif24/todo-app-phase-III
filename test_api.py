#!/usr/bin/env python3
"""
Simple test script to verify the backend API is working correctly.
"""

import requests
import json

def test_backend_health():
    """Test if the backend is running and responding."""
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Health check status: {response.status_code}")
        print(f"Health check response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error connecting to backend: {e}")
        return False

def test_todos_endpoint():
    """Test the todos endpoint with a sample request."""
    try:
        # First, let's try to get the list of todos (without authentication)
        # This should return an authentication error, which is expected
        response = requests.get("http://localhost:8000/todos")
        print(f"Todos GET status: {response.status_code}")

        # Now let's try to post to todos without authentication
        # This should also return an authentication error
        response = requests.post("http://localhost:8000/todos",
                                json={"title": "Test todo", "description": "Test description"})
        print(f"Todos POST status: {response.status_code}")
        if response.status_code != 401:
            print(f"Todos POST response: {response.text}")

        return True
    except Exception as e:
        print(f"Error testing todos endpoint: {e}")
        return False

if __name__ == "__main__":
    print("Testing backend API connectivity...")

    if test_backend_health():
        print("[OK] Backend health check passed")
        test_todos_endpoint()
    else:
        print("[ERROR] Backend health check failed - server might not be running")
        print("\nMake sure to start the backend server with:")
        print("cd backend")
        print("python -m uvicorn src.main:app --reload --port 8000")