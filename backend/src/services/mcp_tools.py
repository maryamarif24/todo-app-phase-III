"""
MCP tools for todo operations.

These are stateless tools that interact with the database through services.
All state is persisted via database operations only.
"""
from typing import Optional, List, Dict, Any
from sqlmodel import Session, create_engine
from ..models.entities import Todo
from ..services.todo_service import get_todo_by_id, get_todos_by_user, create_todo, update_todo, toggle_todo_complete, delete_todo, get_todos_by_title
from ..services.conversation_service import ConversationService
from ..models.conversation import ConversationCreate
from ..models.message import MessageCreate
from ..models.database import get_db
from datetime import datetime
import os


class MCPTools:
    """
    Container for all MCP tools that perform todo operations.
    All tools are stateless and persist data through database operations only.
    """

    @staticmethod
    def _get_db_session():
        """Helper method to get a database session."""
        # Get database URL from environment - reuse existing connection string from Phase II
        database_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")
        engine = create_engine(database_url)
        with Session(engine) as session:
            yield session

    @staticmethod
    def create_todo_tool(user_id: str, title: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        MCP tool for creating a new todo.

        Args:
            user_id: The ID of the user creating the todo
            title: The title of the todo
            description: Optional description of the todo

        Returns:
            Dictionary with the created todo information
        """
        try:
            # Get a database session
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise ValueError("DATABASE_URL environment variable is not set")
            engine = create_engine(database_url)

            with Session(engine) as session:
                # Create the todo using the service
                new_todo = create_todo(session, user_id, title, description)

                # Return the created todo data
                return {
                    "success": True,
                    "todo": {
                        "id": str(new_todo.id),
                        "title": new_todo.title,
                        "description": new_todo.description,
                        "is_complete": new_todo.is_complete,
                        "created_at": new_todo.created_at.isoformat(),
                        "completed_at": new_todo.completed_at.isoformat() if new_todo.completed_at else None
                    }
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def retrieve_todos_tool(user_id: str, completed: Optional[bool] = None) -> Dict[str, Any]:
        """
        MCP tool for retrieving todos for a user.

        Args:
            user_id: The ID of the user whose todos to retrieve
            completed: Optional filter for completion status (True for completed, False for incomplete, None for all)

        Returns:
            Dictionary with the list of todos
        """
        try:
            # Get a database session
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise ValueError("DATABASE_URL environment variable is not set")
            engine = create_engine(database_url)

            with Session(engine) as session:
                # Retrieve todos using the service
                todos = get_todos_by_user(session, user_id, completed)

                # Format the todos for return
                todos_data = []
                for todo in todos:
                    todos_data.append({
                        "id": str(todo.id),
                        "title": todo.title,
                        "description": todo.description,
                        "is_complete": todo.is_complete,
                        "created_at": todo.created_at.isoformat(),
                        "updated_at": todo.updated_at.isoformat(),
                        "completed_at": todo.completed_at.isoformat() if todo.completed_at else None
                    })

                return {
                    "success": True,
                    "todos": todos_data,
                    "count": len(todos_data)
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def update_todo_tool(
        todo_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        is_complete: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        MCP tool for updating a todo.

        Args:
            todo_id: The ID of the todo to update
            title: Optional new title
            description: Optional new description
            is_complete: Optional new completion status

        Returns:
            Dictionary with the updated todo information
        """
        try:
            # Get a database session
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise ValueError("DATABASE_URL environment variable is not set")
            engine = create_engine(database_url)

            with Session(engine) as session:
                # Update the todo using the service
                updated_todo = update_todo(session, todo_id, title, description, is_complete)

                if updated_todo:
                    return {
                        "success": True,
                        "todo": {
                            "id": str(updated_todo.id),
                            "title": updated_todo.title,
                            "description": updated_todo.description,
                            "is_complete": updated_todo.is_complete,
                            "created_at": updated_todo.created_at.isoformat(),
                            "updated_at": updated_todo.updated_at.isoformat(),
                            "completed_at": updated_todo.completed_at.isoformat() if updated_todo.completed_at else None
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": "Todo not found"
                    }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def delete_todo_tool(todo_id: str) -> Dict[str, Any]:
        """
        MCP tool for deleting a todo.

        Args:
            todo_id: The ID of the todo to delete

        Returns:
            Dictionary indicating success or failure
        """
        try:
            # Get a database session
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise ValueError("DATABASE_URL environment variable is not set")
            engine = create_engine(database_url)

            with Session(engine) as session:
                # Delete the todo using the service
                success = delete_todo(session, todo_id)

                if success:
                    return {
                        "success": True,
                        "message": "Todo deleted successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Todo not found"
                    }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def toggle_completion_tool(todo_id: str) -> Dict[str, Any]:
        """
        MCP tool for toggling a todo's completion status.

        Args:
            todo_id: The ID of the todo to toggle

        Returns:
            Dictionary with the updated todo information
        """
        try:
            # Get a database session
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise ValueError("DATABASE_URL environment variable is not set")
            engine = create_engine(database_url)

            with Session(engine) as session:
                # Toggle the todo completion using the service
                updated_todo = toggle_todo_complete(session, todo_id)

                if updated_todo:
                    return {
                        "success": True,
                        "todo": {
                            "id": str(updated_todo.id),
                            "title": updated_todo.title,
                            "description": updated_todo.description,
                            "is_complete": updated_todo.is_complete,
                            "created_at": updated_todo.created_at.isoformat(),
                            "updated_at": updated_todo.updated_at.isoformat(),
                            "completed_at": updated_todo.completed_at.isoformat() if updated_todo.completed_at else None
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": "Todo not found"
                    }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def get_todos_by_title_tool(user_id: str, title: str) -> Dict[str, Any]:
        """
        MCP tool for retrieving todos by title.

        Args:
            user_id: The ID of the user whose todos to retrieve
            title: The title to search for

        Returns:
            Dictionary with the list of matching todos
        """
        try:
            # Get a database session
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise ValueError("DATABASE_URL environment variable is not set")
            engine = create_engine(database_url)

            with Session(engine) as session:
                # Retrieve todos by title using the service
                todos = get_todos_by_title(session, user_id, title)

                # Format the todos for return
                todos_data = []
                for todo in todos:
                    todos_data.append({
                        "id": str(todo.id),
                        "title": todo.title,
                        "description": todo.description,
                        "is_complete": todo.is_complete,
                        "created_at": todo.created_at.isoformat(),
                        "updated_at": todo.updated_at.isoformat(),
                        "completed_at": todo.completed_at.isoformat() if todo.completed_at else None
                    })

                return {
                    "success": True,
                    "todos": todos_data,
                    "count": len(todos_data)
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }