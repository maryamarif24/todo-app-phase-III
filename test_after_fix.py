#!/usr/bin/env python3
"""
Test to see if todo creation works after the schema fix.
"""

import requests
import random

def test_todo_creation_after_fix():
    """Test todo creation after schema fix."""
    print("Testing todo creation after schema fix...")

    try:
        # Create a test user
        test_email = f"testuser_{random.randint(1000, 9999)}@example.com"
        test_password = "Password123!"

        # Sign up
        signup_data = {
            "email": test_email,
            "password": test_password
        }

        print(f"Creating user: {test_email}")
        signup_response = requests.post("http://localhost:8000/auth/signup", json=signup_data, timeout=10)

        if signup_response.status_code != 201:
            print(f"✗ Signup failed: {signup_response.status_code}, {signup_response.text}")
            return False

        signup_result = signup_response.json()
        auth_token = signup_result["session"]["token"]
        print("✓ User created successfully")

        # Create a todo
        todo_data = {
            "title": "Test todo after schema fix",
            "description": "This is a test todo created after the schema fix"
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }

        print("Creating todo with authenticated user...")
        todo_response = requests.post("http://localhost:8000/todos", json=todo_data, headers=headers, timeout=10)

        if todo_response.status_code == 201:
            todo_result = todo_response.json()
            print(f"✓ Todo created successfully: {todo_result['title']}")
            print(f"  Todo ID: {todo_result['id']}")
            return True
        else:
            print(f"✗ Todo creation failed: {todo_response.status_code}")
            try:
                error_text = todo_response.json()
                print(f"  Error: {error_text}")
            except:
                print(f"  Error: {todo_response.text}")
            return False

    except Exception as e:
        print(f"✗ Test failed with exception: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

def main():
    print("Testing functionality after schema fix...\n")

    success = test_todo_creation_after_fix()

    if success:
        print("\n✓ Todo creation is working after the schema fix!")
    else:
        print("\n✗ Todo creation is still failing.")

if __name__ == "__main__":
    main()