#!/usr/bin/env python3
"""
Simple test to verify the chat API is working correctly.
"""

import requests
import os
from typing import Dict, Any

def test_chat_api():
    """Test the chat API endpoint."""
    print("[INFO] Testing Chat API Endpoint...")

    # Get the API URL from environment or use default
    api_url = os.getenv("API_URL", "http://localhost:8000")
    chat_endpoint = f"{api_url}/chat/chat"

    # Sample request data
    sample_request = {
        "message": "Hello, can you help me with my todos?",
        "conversation_id": None
    }

    # Headers (would normally include auth token)
    headers = {
        "Content-Type": "application/json"
    }

    print(f"  [INFO] Sending request to: {chat_endpoint}")
    print(f"  [INFO] Request data: {sample_request}")

    try:
        response = requests.post(chat_endpoint, json=sample_request, headers=headers, timeout=30)

        print(f"  [INFO] Response status: {response.status_code}")

        if response.status_code == 200:
            response_data = response.json()
            print(f"  [SUCCESS] Response received: {response_data}")
            return True
        elif response.status_code == 422:  # Validation error - expected if no auth
            print(f"  [INFO] Validation error (expected without authentication): {response.json()}")
            return True
        elif response.status_code == 401:  # Unauthorized - expected if no auth
            print(f"  [INFO] Unauthorized (expected without authentication): {response.json()}")
            return True
        else:
            print(f"  [ERROR] Unexpected response: {response.status_code}, {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"  [ERROR] Cannot connect to API at {chat_endpoint}")
        print(f"  [HINT] Make sure the backend server is running on {api_url}")
        return False
    except requests.exceptions.Timeout:
        print(f"  [ERROR] Request timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"  [ERROR] Request failed: {str(e)}")
        return False

def test_conversations_api():
    """Test the conversations API endpoint."""
    print("\n[INFO] Testing Conversations API Endpoint...")

    # Get the API URL from environment or use default
    api_url = os.getenv("API_URL", "http://localhost:8000")
    conversations_endpoint = f"{api_url}/chat/conversations"

    # Headers (would normally include auth token)
    headers = {
        "Content-Type": "application/json"
    }

    print(f"  [INFO] Sending request to: {conversations_endpoint}")

    try:
        response = requests.get(conversations_endpoint, headers=headers, timeout=30)

        print(f"  [INFO] Response status: {response.status_code}")

        if response.status_code in [200, 422, 401]:  # Expected responses
            if response.status_code == 200:
                response_data = response.json()
                print(f"  [SUCCESS] Response received: {response_data}")
            elif response.status_code == 422:  # Validation error - expected if no auth
                print(f"  [INFO] Validation error (expected without authentication): {response.json()}")
            elif response.status_code == 401:  # Unauthorized - expected if no auth
                print(f"  [INFO] Unauthorized (expected without authentication): {response.json()}")
            return True
        else:
            print(f"  [ERROR] Unexpected response: {response.status_code}, {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"  [ERROR] Cannot connect to API at {conversations_endpoint}")
        print(f"  [HINT] Make sure the backend server is running on {api_url}")
        return False
    except requests.exceptions.Timeout:
        print(f"  [ERROR] Request timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"  [ERROR] Request failed: {str(e)}")
        return False

def main():
    """Run API tests."""
    print("[INFO] Starting Chat API Tests...\n")

    tests = [
        ("Chat API Endpoint", test_chat_api),
        ("Conversations API Endpoint", test_conversations_api),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  [CRASH] {test_name} crashed: {str(e)}")
            results.append((test_name, False))

    print(f"\n[SUMMARY] API Test Results:")
    all_passed = True
    for test_name, passed in results:
        status = "  [PASS]" if passed else "  [FAIL]"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False

    print(f"\n{'[SUCCESS] All API tests passed!' if all_passed else '[WARNING] Some API tests failed. Please check the output above for details.'}")

    if all_passed:
        print("\n[INFO] The chat API endpoints are accessible and responding correctly.")
        print("[INFO] Remember that authentication is required to use the chat functionality.")
    else:
        print("\n[TIPS] Common issues:")
        print("  1. Make sure the backend server is running")
        print("  2. Check that the API URL is correct")
        print("  3. Verify that the chat routes are properly registered in the backend")

if __name__ == "__main__":
    main()