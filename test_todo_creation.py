#!/usr/bin/env python3
"""
Test script to verify todo creation functionality.
"""

import requests
import uuid
import os

def test_todo_creation():
    """Test the todo creation endpoint with a mock user ID."""
    print("[INFO] Testing Todo Creation Endpoint...")

    # Get the API URL from environment or use default
    api_url = os.getenv("API_URL", "http://localhost:8000")
    todos_endpoint = f"{api_url}/todos"

    # Create a mock user ID (this would normally come from auth)
    mock_user_id = str(uuid.uuid4())
    print(f"  [INFO] Using mock user ID: {mock_user_id}")

    # Sample todo data
    todo_data = {
        "title": "Test todo creation",
        "description": "This is a test todo created via the API"
    }

    # Headers (using the mock user ID as the auth token)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {mock_user_id}"  # Using the UUID as the token
    }

    print(f"  [INFO] Sending request to: {todos_endpoint}")
    print(f"  [INFO] Request data: {todo_data}")

    try:
        response = requests.post(todos_endpoint, json=todo_data, headers=headers, timeout=30)

        print(f"  [INFO] Response status: {response.status_code}")

        if response.status_code == 201:  # Created
            response_data = response.json()
            print(f"  [SUCCESS] Todo created successfully: {response_data}")
            return True
        elif response.status_code == 422:  # Validation error
            error_data = response.json()
            print(f"  [INFO] Validation error: {error_data}")
            return False
        else:
            error_text = response.text
            print(f"  [ERROR] Unexpected response: {response.status_code}")
            print(f"  [ERROR] Response body: {error_text}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"  [ERROR] Cannot connect to API at {todos_endpoint}")
        print(f"  [HINT] Make sure the backend server is running on {api_url}")
        return False
    except requests.exceptions.Timeout:
        print(f"  [ERROR] Request timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"  [ERROR] Request failed: {str(e)}")
        return False

def test_with_real_user():
    """Test with a real user by first signing up."""
    print("\n[INFO] Testing with Real User Registration...")

    # Get the API URL from environment or use default
    api_url = os.getenv("API_URL", "http://localhost:8000")

    # Signup endpoint
    signup_endpoint = f"{api_url}/auth/signup"

    # Create test user data
    import random
    test_email = f"testuser_{random.randint(1000, 9999)}@example.com"
    test_password = "password123"

    signup_data = {
        "email": test_email,
        "password": test_password
    }

    print(f"  [INFO] Creating test user: {test_email}")

    try:
        # Sign up the user
        signup_response = requests.post(signup_endpoint, json=signup_data, timeout=30)

        if signup_response.status_code != 201:
            print(f"  [ERROR] Signup failed: {signup_response.status_code}, {signup_response.text}")
            return False

        signup_result = signup_response.json()
        auth_token = signup_result["session"]["token"]

        print(f"  [SUCCESS] User created, got auth token")

        # Now try to create a todo with the real user
        todos_endpoint = f"{api_url}/todos"
        todo_data = {
            "title": "Real user test todo",
            "description": "Created by a real authenticated user"
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }

        print(f"  [INFO] Creating todo with auth token...")
        todo_response = requests.post(todos_endpoint, json=todo_data, headers=headers, timeout=30)

        if todo_response.status_code == 201:
            todo_result = todo_response.json()
            print(f"  [SUCCESS] Todo created with real user: {todo_result}")
            return True
        else:
            print(f"  [ERROR] Todo creation failed: {todo_response.status_code}, {todo_response.text}")
            return False

    except Exception as e:
        print(f"  [ERROR] Test with real user failed: {str(e)}")
        return False

def main():
    """Run todo creation tests."""
    print("[INFO] Starting Todo Creation Tests...\n")

    print("Note: These tests require the backend server to be running.")
    print("Start the backend with: python -m uvicorn backend.src.main:app --reload --port 8000\n")

    tests = [
        ("Todo Creation with Mock User", test_todo_creation),
        ("Todo Creation with Real User", test_with_real_user),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  [CRASH] {test_name} crashed: {str(e)}")
            results.append((test_name, False))

    print(f"\n[SUMMARY] Todo Creation Test Results:")
    all_passed = True
    for test_name, passed in results:
        status = "  [PASS]" if passed else "  [FAIL]"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False

    print(f"\n{'[SUCCESS] All tests passed!' if all_passed else '[WARNING] Some tests failed. Please check the output above for details.'}")

    if all_passed:
        print("\n[INFO] Todo creation functionality is working correctly.")
    else:
        print("\n[TIPS] Common issues:")
        print("  1. Make sure the backend server is running")
        print("  2. Check that the database is properly configured and connected")
        print("  3. Verify that authentication is working properly")

if __name__ == "__main__":
    main()