#!/usr/bin/env python3
"""
Script to debug the todo creation issue by running the server and triggering the error
"""

import subprocess
import time
import requests
import sys
import threading

def run_server_and_test():
    # Start the server with output redirected to capture logs
    server_process = subprocess.Popen([
        sys.executable, '-m', 'uvicorn', 'src.main:app', 
        '--host', '0.0.0.0', 
        '--port', '8000', 
        '--reload'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True, cwd='backend')
    
    # Wait for the server to start
    time.sleep(3)
    
    # Check if the server started successfully
    if server_process.poll() is not None:
        print("Server failed to start")
        stdout, stderr = server_process.communicate()
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        return
    
    print("Server started, attempting to create a todo...")
    
    try:
        # First, create a user
        signup_response = requests.post(
            'http://localhost:8000/auth/signup',
            json={'email': 'debug@example.com', 'password': 'DebugPass123!'},
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Signup status: {signup_response.status_code}")
        print(f"Signup response: {signup_response.text}")
        
        if signup_response.status_code == 201:
            user_data = signup_response.json()
            token = user_data['session']['token']
            
            print(f"Created user with token: {token}")
            
            # Now try to create a todo - this should trigger the error
            todo_response = requests.post(
                'http://localhost:8000/todos',
                json={'title': 'Debug Todo', 'description': 'Debug Description'},
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                }
            )
            
            print(f"Create todo status: {todo_response.status_code}")
            print(f"Create todo response: {todo_response.text}")
    
    except Exception as e:
        print(f"Error during API calls: {e}")
    
    # Wait a bit more to capture server logs
    time.sleep(2)
    
    # Get any server output
    server_process.terminate()
    stdout, stderr = server_process.communicate(timeout=5)
    
    print("\n--- SERVER STDOUT ---")
    print(stdout)
    print("\n--- SERVER STDERR ---")
    print(stderr)

if __name__ == "__main__":
    run_server_and_test()
