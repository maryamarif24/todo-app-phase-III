"""
AI Agent for todo management using OpenAI Agents SDK with OpenRouter.

This agent uses OpenAI Agents SDK to create an intelligent agent that can manage todos
and engage in conversation using OpenRouter API.
"""
import os
import json
import httpx
from typing import Dict, Any, Optional
from openai import OpenAI

from ..services.conversation_service import ConversationService
from sqlmodel import Session


class TodoAgent:
    """
    AI Agent using OpenAI Agents SDK for managing todos through natural language conversations.
    """

    def __init__(self):
        """Initialize the TodoAgent with OpenRouter API configuration."""
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.offline_mode = not bool(self.openrouter_api_key)
        self.current_user_id = None  # Will be set when processing messages

        # Define the API configuration attributes
        self.api_key = self.openrouter_api_key
        self.model = "openai/gpt-4o-mini"
        self.base_url = "https://openrouter.ai/api/v1"

        if self.offline_mode:
            print("Warning: OPENROUTER_API_KEY not found. Running in offline mode with limited functionality.")
        else:
            # Initialize OpenAI client with OpenRouter
            self.client = OpenAI(
                api_key=self.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1",
            )
            print("TodoAgent initialized with OpenRouter API")

    def _call_openrouter_api(self, messages: list, tools: list = None) -> dict:
        """
        Call the OpenRouter API with Gemini 2.5 Flash model.

        Args:
            messages: List of messages for the conversation
            tools: Optional list of tools to provide to the model

        Returns:
            Response from the OpenRouter API
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7
        }

        if tools:
            payload["tools"] = tools

        try:
            # Increase timeout and add retry logic
            timeout = httpx.Timeout(60.0, connect=10.0)  # 60s total, 10s connect
            with httpx.Client(timeout=timeout) as client:
                response = client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException as e:
            print(f"Timeout error calling OpenRouter API: {str(e)}")
            # Return a helpful response when request times out
            return {
                "choices": [{
                    "message": {
                        "content": "The request timed out. Please check your internet connection and try again. I can still help you manage your todos if you'd like!"
                    }
                }]
            }
        except httpx.RequestError as e:
            print(f"Network error calling OpenRouter API: {str(e)}")
            # Return a mock response structure when network fails
            return {
                "choices": [{
                    "message": {
                        "content": "I'm currently unable to connect to my AI services due to a network issue. I can help you manage your todos directly though. What would you like to do?"
                    }
                }]
            }
        except httpx.HTTPStatusError as e:
            print(f"HTTP error from OpenRouter API: {e.response.status_code} - {e.response.text}")
            # Return a mock response structure when API returns error
            return {
                "choices": [{
                    "message": {
                        "content": f"API Error {e.response.status_code}: I'm having trouble connecting to my AI services. What would you like to do with your todos?"
                    }
                }]
            }
        except Exception as e:
            print(f"Unexpected error calling OpenRouter API: {str(e)}")
            # Return a mock response structure for other errors
            return {
                "choices": [{
                    "message": {
                        "content": "I'm experiencing an issue connecting to my AI services. What would you like to do with your todos?"
                    }
                }]
            }

    def process_message(self, user_id, message: str, conversation_id: Optional[str] = None) -> str:
        """
        Process a natural language message and return an appropriate response.

        Args:
            user_id: The user's UUID
            message: The natural language message from the user
            conversation_id: Optional conversation ID for context

        Returns:
            AI-generated response string
        """
        # Set current user ID for tool functions
        self.current_user_id = user_id
        user_id_str = str(user_id)
        message_lower = message.lower().strip()

        # Handle todo-specific commands first
        if self._is_todo_command(message_lower):
            return self._handle_todo_command(user_id_str, message_lower)

        # Handle general conversation
        if self._is_general_conversation(message_lower):
            if not self.offline_mode:
                return self._process_with_ai(user_id_str, message)
            else:
                return self._handle_general_conversation(message)

        # If not in offline mode, use AI for more complex queries
        if not self.offline_mode:
            return self._process_with_ai(user_id_str, message)

        # Default response for offline mode
        return "I can help you manage your todos! Try saying things like:\n- 'Create a todo to buy groceries'\n- 'Show me my todos'\n- 'Mark todo abc-123 as complete'\n- 'Delete todo abc-123'"

    def _extract_todo_title(self, message: str) -> Optional[str]:
        """Extract todo title from a create message."""
        # Simple extraction - look for common patterns
        message_lower = message.lower()

        # Patterns like "create todo to [title]" or "add [title] to my todos"
        if 'todo to' in message_lower:
            parts = message.split('todo to', 1)
            if len(parts) > 1:
                return parts[1].strip()
        elif 'todo:' in message:
            parts = message.split('todo:', 1)
            if len(parts) > 1:
                return parts[1].strip()
        elif 'add' in message_lower and 'to' in message_lower:
            # Extract between "add" and "to"
            add_idx = message_lower.find('add')
            to_idx = message_lower.find('to', add_idx)
            if add_idx != -1 and to_idx != -1:
                return message[add_idx + 3:to_idx].strip()

        # Fallback: return the whole message after removing common words
        words_to_remove = ['create', 'add', 'new', 'make', 'todo', 'to', 'a', 'an', 'the']
        title = message
        for word in words_to_remove:
            title = title.replace(word, ' ')
        return title.strip() or None

    def _is_todo_command(self, message_lower: str) -> bool:
        """Check if the message is a todo command."""
        todo_keywords = ['create', 'add', 'new', 'make', 'todo', 'task', 'delete', 'remove', 'complete', 'finish', 'done', 'mark', 'show', 'list', 'view', 'get']
        for keyword in todo_keywords:
            if keyword in message_lower:
                return True
        return False

    def _handle_todo_command(self, user_id_str: str, message_lower: str) -> str:
        """Handle todo-specific commands."""
        # This would typically integrate with the todo service
        # For now, return a helpful message
        if any(word in message_lower for word in ['create', 'add', 'new', 'make']) and any(word in message_lower for word in ['todo', 'task']):
            return "I can help you create a todo! In a full implementation, I would create a todo based on your request."
        elif any(word in message_lower for word in ['show', 'list', 'view', 'get']) and any(word in message_lower for word in ['todo', 'task', 'todos', 'tasks']):
            return "I can help you view your todos! In a full implementation, I would show your todo list."
        elif any(word in message_lower for word in ['complete', 'finish', 'done', 'mark']) and any(word in message_lower for word in ['todo', 'task']):
            return "I can help you mark a todo as complete! In a full implementation, I would update the todo status."
        elif any(word in message_lower for word in ['delete', 'remove']) and any(word in message_lower for word in ['todo', 'task']):
            return "I can help you delete a todo! In a full implementation, I would remove the todo."
        else:
            return "I can help you manage your todos! Try saying things like 'Create a todo to buy groceries' or 'Show me my todos'."

    def _extract_todo_id(self, message: str) -> Optional[str]:
        """Extract todo ID from message."""
        import re
        # Look for UUID pattern or simple ID
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        match = re.search(uuid_pattern, message, re.IGNORECASE)
        if match:
            return match.group(0)
        return None

    def _is_general_conversation(self, message_lower: str) -> bool:
        """Check if the message is general conversation (not todo-specific)."""
        # General conversation keywords
        general_keywords = [
            'hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon',
            'good evening', 'how are you', 'what\'s up', 'howdy', 'sup',
            'thanks', 'thank you', 'bye', 'goodbye', 'see you', 'later',
            'how can you help', 'what can you do', 'help', 'who are you',
            'what are you', 'tell me about yourself', 'introduce yourself',
            'nice to meet you', 'pleased to meet you', 'how\'s it going',
            'what\'s new', 'how have you been', 'long time no see',
            'what do you think', 'in your opinion', 'do you like', 'favorite',
            'hobby', 'interest', 'passion', 'dream', 'goal', 'wish',
            'weather', 'time', 'date', 'day', 'today', 'tomorrow',
            'yesterday', 'weekend', 'vacation', 'holiday', 'birthday',
            'celebration', 'party', 'fun', 'joke', 'laugh', 'smile',
            'happy', 'sad', 'angry', 'excited', 'bored', 'tired',
            'hungry', 'thirsty', 'sleepy', 'awake', 'dream', 'nightmare',
            'music', 'song', 'movie', 'film', 'book', 'game', 'sport',
            'food', 'drink', 'color', 'animal', 'place', 'country',
            'city', 'travel', 'adventure', 'story', 'memory', 'experience'
        ]

        # Check if message contains general conversation keywords
        for keyword in general_keywords:
            if keyword in message_lower:
                return True

        # Check for questions (starts with who, what, where, when, why, how)
        question_words = ['who ', 'what ', 'where ', 'when ', 'why ', 'how ', 'which ', 'whose ']
        for word in question_words:
            if message_lower.startswith(word) or f' {word}' in message_lower:
                return True

        # If message is very short (likely greeting or simple response)
        if len(message_lower.split()) <= 3:
            return True

        return False

    def _handle_general_conversation(self, message: str) -> str:
        """Handle general conversation in offline mode."""
        message_lower = message.lower().strip()

        # Greetings
        if any(word in message_lower for word in ['hi', 'hello', 'hey', 'greetings', 'howdy', 'sup']):
            return "Hello! I'm your todo assistant. I can help you manage your tasks and have a chat too! How can I help you today?"

        # How are you
        elif 'how are you' in message_lower or 'how\'s it going' in message_lower:
            return "I'm doing great, thanks for asking! I'm here and ready to help you with your todos or just chat. What's on your mind?"

        # Thanks
        elif any(word in message_lower for word in ['thanks', 'thank you', 'thx', 'ty']):
            return "You're welcome! I'm always here to help with your todos or chat. Is there anything else I can assist you with?"

        # Goodbye
        elif any(word in message_lower for word in ['bye', 'goodbye', 'see you', 'later', 'cya']):
            return "Goodbye! Don't forget to check your todos. Come back anytime!"

        # Help/About
        elif any(word in message_lower for word in ['help', 'what can you do', 'how can you help']):
            return """I'm your friendly todo assistant! I can help you:

📝 **Todo Management:**
• Create new todos: "Create a todo to buy groceries"
• View your todos: "Show me my todos"
• Mark complete: "Mark todo abc-123 as complete"
• Delete todos: "Delete todo abc-123"

💬 **Chat with me:**
• Ask questions, tell jokes, or just say hi!
• I can talk about various topics

What would you like to do?"""

        # Who are you
        elif any(phrase in message_lower for phrase in ['who are you', 'what are you', 'introduce yourself', 'tell me about yourself']):
            return "I'm your personal todo assistant and chat companion! I help you manage your tasks while also being here for friendly conversation. I love helping people stay organized and productive!"

        # Weather/Time questions
        elif any(word in message_lower for word in ['weather', 'time', 'date', 'day']):
            return "I don't have access to current weather or time data, but I can definitely help you manage your todos and chat about other things! What's on your agenda today?"

        # Jokes/Fun
        elif any(word in message_lower for word in ['joke', 'funny', 'laugh']):
            return "Why did the todo list go to therapy? It had too many unresolved issues! 😄 What else can I help you with?"

        # Default friendly response
        else:
            responses = [
                "That's interesting! Tell me more about that.",
                "I love chatting! What's been happening with you?",
                "Sounds good! How else can I help you today?",
                "I'm all ears! What's next on your mind?",
                "Great to hear from you! What else is going on?",
                "I enjoy our conversations! What's new with you?"
            ]
            import random
            return random.choice(responses)

    def _process_with_ai(self, user_id_str: str, message: str) -> str:
        """
        Process message using OpenRouter API.
        Falls back to offline mode if API is unavailable.
        """
        # Check if API key is available
        if self.offline_mode:
            print("OpenRouter API key not available, using offline mode")
            return self._handle_offline_fallback(message)

        try:
            # Prepare messages for the API call
            messages = [
                {
                    "role": "system",
                    "content": """You are a helpful assistant that manages todo items for users.
                    You can help users create, view, update, delete, and toggle completion status of todos.
                    Be friendly and conversational. If the user wants to perform todo operations, guide them on how to do it.
                    For example:
                    - To create: "Create a todo to buy groceries"
                    - To view: "Show me my todos"
                    - To complete: "Mark todo abc-123 as complete"
                    - To delete: "Delete todo abc-123"
                    """
                },
                {
                    "role": "user",
                    "content": f"User ID: {user_id_str}\nMessage: {message}"
                }
            ]

            # Call the OpenRouter API
            response = self.client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=messages,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error calling OpenRouter API: {str(e)}")
            # Fallback to offline mode
            return self._handle_offline_fallback(message)



    def _handle_offline_fallback(self, message: str) -> str:
        """Handle requests when AI API is unavailable."""
        message_lower = message.lower().strip()

        # Check for basic todo commands
        if any(word in message_lower for word in ['create', 'add', 'new']) and 'todo' in message_lower:
            return "I'd love to create a todo for you, but I'm currently in offline mode. Please try again when the AI service is available."
        elif any(word in message_lower for word in ['show', 'list', 'view', 'get']):
            return "I'd love to show you your todos, but I'm currently in offline mode. Please try again when the AI service is available."
        elif any(word in message_lower for word in ['complete', 'finish', 'done', 'mark']):
            return "I'd love to update your todos, but I'm currently in offline mode. Please try again when the AI service is available."
        elif any(word in message_lower for word in ['delete', 'remove']):
            return "I'd love to delete that todo, but I'm currently in offline mode. Please try again when the AI service is available."
        else:
            return "I'm currently in offline mode due to connectivity issues. I can still help with basic todo management when the AI service is back online. What would you like to chat about in the meantime?"

    def get_conversation_context(self, conversation_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get conversation context for multi-turn conversations.

        Args:
            conversation_id: The conversation ID
            user_id: The user ID

        Returns:
            Dictionary containing conversation context
        """
        # This would integrate with the conversation service to retrieve recent messages
        # For now, returning an empty context - in a real implementation you'd retrieve
        # recent messages to provide context for the AI
        return {
            "recent_messages": [],
            "user_todos": []  # Could include user's current todos for context
        }