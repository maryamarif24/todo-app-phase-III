#!/usr/bin/env python3
"""
Test script to verify the fix for todo creation.
"""

import os
import sys
import requests
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def test_with_new_fix():
    """Test todo creation with the fix applied."""
    print("[INFO] Testing with Applied Fix...")

    # Test with an existing user or create a new one
    api_url = os.getenv("API_URL", "http://localhost:8000")

    # First, try to create a test user with proper password
    signup_endpoint = f"{api_url}/auth/signup"

    import random
    test_email = f"testuser_{random.randint(1000, 9999)}@example.com"
    test_password = "Password123!"

    signup_data = {
        "email": test_email,
        "password": test_password
    }

    print(f"  [INFO] Creating test user: {test_email}")

    try:
        # Sign up the user
        signup_response = requests.post(signup_endpoint, json=signup_data, timeout=30)

        if signup_response.status_code != 201:
            print(f"  [ERROR] Signup failed: {signup_response.status_code}")
            try:
                error_json = signup_response.json()
                print(f"  [ERROR] Error details: {error_json}")
            except:
                print(f"  [ERROR] Response text: {signup_response.text}")
            return False

        signup_result = signup_response.json()
        auth_token = signup_result["session"]["token"]

        print(f"  [SUCCESS] User created successfully")

        # Now try to create a todo with the authenticated user
        todos_endpoint = f"{api_url}/todos"
        todo_data = {
            "title": "Test todo after fix",
            "description": "This is a test todo created after applying the fix"
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }

        print(f"  [INFO] Creating todo with authenticated user...")
        todo_response = requests.post(todos_endpoint, json=todo_data, headers=headers, timeout=30)

        if todo_response.status_code == 201:
            todo_result = todo_response.json()
            print(f"  [SUCCESS] Todo created successfully: {todo_result['title']}")
            print(f"  [INFO] Todo ID: {todo_result['id']}")
            return True
        elif todo_response.status_code == 422:
            error_data = todo_response.json()
            print(f"  [ERROR] Validation error: {error_data}")
            return False
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
    """Run the test."""
    print("[INFO] Starting Test with Applied Fix...\n")

    success = test_with_new_fix()

    if success:
        print(f"\n[SUCCESS] Fix test passed!")
        print("Todo creation is now working correctly.")
    else:
        print(f"\n[ERROR] Fix test failed!")
        print("There may still be issues with the todo creation functionality.")

if __name__ == "__main__":
    main()