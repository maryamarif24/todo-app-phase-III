import os
import sys
import uuid

# Add backend to Python path
sys.path.insert(0, './backend')

# Set environment variables to avoid warnings
os.environ.setdefault('FRONTEND_URL', 'http://localhost:3000')
os.environ.pop('OPENROUTER_API_KEY', None)  # Remove any existing API key to trigger offline mode

from backend.src.agents.todo_agent import TodoAgent

def test_todo_agent():
    print("Testing TodoAgent instantiation and processing...")
    
    try:
        # Create a TodoAgent instance
        agent = TodoAgent()
        print(f"TodoAgent created. Offline mode: {agent.offline_mode}")
        
        # Test processing a message
        user_id = uuid.uuid4()
        message = "Hello, can you help me create a todo?"
        
        print(f"Processing message: {message}")
        response = agent.process_message(user_id, message)
        print(f"Response received: {response[:100]}...")  # Print first 100 chars
        return True
    except Exception as e:
        print(f"Error in TodoAgent: {str(e)}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_todo_agent()
    if success:
        print("\nTest PASSED: TodoAgent works correctly!")
    else:
        print("\nTest FAILED: TodoAgent has issues!")