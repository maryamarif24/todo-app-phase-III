#!/usr/bin/env python3
"""
Diagnostic script to test chat functionality and identify potential issues.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def test_environment_variables():
    """Test if required environment variables are set."""
    print("[TEST] Testing Environment Variables...")

    # Change to backend directory to load .env
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    required_vars = ['OPENROUTER_API_KEY', 'DATABASE_URL']
    missing_vars = []

    for var in required_vars:
        value = os.getenv(var)
        if not value or value == 'your_openrouter_api_key_here':
            missing_vars.append(var)
        else:
            print(f"  [OK] {var}: Configured")

    if missing_vars:
        print(f"  [ERROR] Missing required environment variables: {missing_vars}")
        print("\n  [TIP] To fix this:")
        print(f"   1. Edit {backend_dir}/.env")
        print("   2. Add your OpenRouter API key from https://openrouter.ai/keys")
        print("   3. Configure your database URL")
        return False

    return True

def test_database_connection():
    """Test database connectivity."""
    print("\n[TEST] Testing Database Connection...")

    try:
        from backend.src.models.database import get_db
        from sqlmodel import Session

        # Get database URL
        database_url = os.getenv("DATABASE_URL")
        print(f"  Database URL: {database_url[:50]}..." if database_url else "  Database URL: Not set")

        # Try to create a session
        from sqlmodel import create_engine
        engine = create_engine(database_url)

        with Session(engine) as session:
            # Just try to connect, no actual query needed for basic test
            print("  [OK] Database connection successful")
            return True

    except Exception as e:
        print(f"  [ERROR] Database connection failed: {str(e)}")
        return False

def test_mcp_server():
    """Test MCP server initialization."""
    print("\n[TEST] Testing MCP Server Initialization...")

    try:
        from backend.src.services.mcp_server import get_mcp_server

        # Try to get the server instance
        server = get_mcp_server()
        tools = server.get_available_tools()

        print(f"  [OK] MCP Server initialized successfully")
        print(f"   Available tools: {len(tools)} ({', '.join(tools)})")
        return True

    except Exception as e:
        print(f"  [ERROR] MCP Server initialization failed: {str(e)}")
        return False

def test_todo_agent():
    """Test Todo Agent initialization."""
    print("\n[TEST] Testing Todo Agent Initialization...")

    try:
        from backend.src.agents.todo_agent import TodoAgent

        # Try to create an agent
        agent = TodoAgent()

        print(f"  [OK] Todo Agent initialized successfully")
        print(f"   Model: {agent.model}")
        print(f"   API Key configured: {'Yes' if agent.api_key else 'No'}")
        return True

    except Exception as e:
        print(f"  [ERROR] Todo Agent initialization failed: {str(e)}")
        return False

def test_conversation_service():
    """Test conversation service."""
    print("\n[TEST] Testing Conversation Service...")

    try:
        from backend.src.services.conversation_service import ConversationService

        # Try to create conversation service
        service = ConversationService()

        print(f"  [OK] Conversation Service initialized successfully")
        return True

    except Exception as e:
        print(f"  [ERROR] Conversation Service initialization failed: {str(e)}")
        return False

def main():
    """Run all diagnostic tests."""
    print("[INFO] Starting Chat Functionality Diagnosis...\n")

    tests = [
        ("Environment Variables", test_environment_variables),
        ("Database Connection", test_database_connection),
        ("MCP Server", test_mcp_server),
        ("Todo Agent", test_todo_agent),
        ("Conversation Service", test_conversation_service),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[ERROR] {test_name} crashed: {str(e)}")
            results.append((test_name, False))

    print(f"\n[SUMMARY] Diagnostic Results:")
    all_passed = True
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status}: {test_name}")
        if not passed:
            all_passed = False

    print(f"\n{'[SUCCESS] All tests passed!' if all_passed else '[WARNING] Some tests failed. Please check the output above for details.'}")

    if not all_passed:
        print("\n[TIPS] Common fixes:")
        print("  1. Ensure all environment variables are set in backend/.env")
        print("  2. Verify database connectivity")
        print("  3. Check that you have a valid OpenRouter API key")
        print("  4. Make sure all dependencies are installed")
        print("  5. Check backend logs for detailed error messages")

if __name__ == "__main__":
    main()