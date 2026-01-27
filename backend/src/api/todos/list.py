"""
Todo CRUD API endpoints.

Optimized for Neon PostgreSQL with sync database operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List, Optional
from pydantic import BaseModel, Field

from ...models import Todo, User
from ...services import (
    get_todos_by_user,
    get_todo_by_id,
    create_todo,
    update_todo,
    delete_todo,
    toggle_todo_complete,
)
from ..dependencies import get_db, get_current_user, get_todo


router = APIRouter()


# Request/Response schemas
class CreateTodoRequest(BaseModel):
    """Request schema for creating a todo."""

    title: str = Field(..., min_length=1, max_length=200, description="Todo title")
    description: Optional[str] = Field(None, max_length=2000, description="Optional description")


class CreateTodoResponse(BaseModel):
    """Response schema for created todo."""

    id: str
    user_id: str
    title: str
    description: Optional[str]
    is_complete: bool
    created_at: str
    updated_at: str


class UpdateTodoRequest(BaseModel):
    """Request schema for updating a todo."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    is_complete: Optional[bool] = None


class TodoResponse(BaseModel):
    """Response schema for a single todo."""

    id: str
    user_id: str
    title: str
    description: Optional[str]
    is_complete: bool
    created_at: str
    updated_at: str


class TodoListResponse(BaseModel):
    """Response schema for todo list."""

    todos: List[TodoResponse]


class ToggleTodoResponse(BaseModel):
    """Response schema for toggle todo."""

    id: str
    user_id: str
    title: str
    description: Optional[str]
    is_complete: bool
    created_at: str
    updated_at: str


class DeleteTodoResponse(BaseModel):
    """Response schema for delete todo."""

    message: str = "Todo deleted successfully"


@router.get("", response_model=TodoListResponse)
async def list_todos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve all todos for the authenticated user.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        List of todos belonging to the user
    """
    todos = get_todos_by_user(db, current_user.id)

    return TodoListResponse(
        todos=[
            TodoResponse(
                id=str(todo.id),
                user_id=str(todo.user_id),
                title=todo.title,
                description=todo.description,
                is_complete=todo.is_complete,
                created_at=todo.created_at.isoformat(),
                updated_at=todo.updated_at.isoformat(),
            )
            for todo in todos
        ]
    )


@router.post("", response_model=CreateTodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo_endpoint(
    request: CreateTodoRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new todo for the authenticated user.

    Args:
        request: Todo creation request
        current_user: Authenticated user
        db: Database session

    Returns:
        Created todo
    """
    # Validate the request data
    if not request.title or len(request.title.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Todo title is required",
        )

    # Trim the title to remove leading/trailing whitespace
    title = request.title.strip()
    description = request.description.strip() if request.description else None

    try:
        # Validate title length
        if len(title) > 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Todo title must be 200 characters or less",
            )

        # Validate description length if provided
        if description and len(description) > 2000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Todo description must be 2000 characters or less",
            )

        todo = create_todo(
            db,
            current_user.id,
            title,
            description,
        )
        db.add(todo)
        db.commit()
        db.refresh(todo)

        return CreateTodoResponse(
            id=str(todo.id),
            user_id=str(todo.user_id),
            title=todo.title,
            description=todo.description,
            is_complete=todo.is_complete,
            created_at=todo.created_at.isoformat(),
            updated_at=todo.updated_at.isoformat(),
        )
    except HTTPException:
        # Re-raise HTTP exceptions with specific details
        raise
    except Exception as e:
        db.rollback()
        error_detail = str(e)
        print(f"Error creating todo: {error_detail}")  # Debug log

        # Provide more specific error messages based on the exception type
        if "duplicate" in error_detail.lower() or "unique" in error_detail.lower():
            error_msg = "A todo with similar properties already exists"
        elif "foreign key" in error_detail.lower():
            error_msg = "User not found. Please log in again."
        elif "not null" in error_detail.lower() or "constraint" in error_detail.lower():
            error_msg = "Required field is missing or invalid"
        elif "connection" in error_detail.lower() or "database" in error_detail.lower():
            error_msg = "Database connection error - please try again later"
        else:
            error_msg = f"Failed to create todo: {error_detail}"

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg,
        )


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo_endpoint(
    todo: Todo = Depends(get_todo),
):
    """
    Retrieve a specific todo by ID.

    Args:
        todo: Todo from dependency (with ownership verification)

    Returns:
        Todo details
    """
    return TodoResponse(
        id=str(todo.id),
        user_id=str(todo.user_id),
        title=todo.title,
        description=todo.description,
        is_complete=todo.is_complete,
        created_at=todo.created_at.isoformat(),
        updated_at=todo.updated_at.isoformat(),
    )


@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo_endpoint(
    request: UpdateTodoRequest,
    todo: Todo = Depends(get_todo),
    db: Session = Depends(get_db),
):
    """
    Update an existing todo.

    Args:
        request: Todo update request
        todo: Todo from dependency (with ownership verification)
        db: Database session

    Returns:
        Updated todo
    """
    updated_todo = update_todo(
        db,
        todo.id,
        title=request.title,
        description=request.description,
        is_complete=request.is_complete,
    )
    db.commit()
    db.refresh(updated_todo)

    return TodoResponse(
        id=str(updated_todo.id),
        user_id=str(updated_todo.user_id),
        title=updated_todo.title,
        description=updated_todo.description,
        is_complete=updated_todo.is_complete,
        created_at=updated_todo.created_at.isoformat(),
        updated_at=updated_todo.updated_at.isoformat(),
    )


@router.patch("/{todo_id}/toggle", response_model=ToggleTodoResponse)
async def toggle_todo_endpoint(
    todo: Todo = Depends(get_todo),
    db: Session = Depends(get_db),
):
    """
    Toggle the complete status of a todo.

    Args:
        todo: Todo from dependency (with ownership verification)
        db: Database session

    Returns:
        Updated todo with toggled status
    """
    updated_todo = toggle_todo_complete(db, todo.id)
    db.commit()
    db.refresh(updated_todo)

    return ToggleTodoResponse(
        id=str(updated_todo.id),
        user_id=str(updated_todo.user_id),
        title=updated_todo.title,
        description=updated_todo.description,
        is_complete=updated_todo.is_complete,
        created_at=updated_todo.created_at.isoformat(),
        updated_at=updated_todo.updated_at.isoformat(),
    )


@router.delete("/{todo_id}", response_model=DeleteTodoResponse)
async def delete_todo_endpoint(
    todo: Todo = Depends(get_todo),
    db: Session = Depends(get_db),
):
    """
    Delete a todo.

    Args:
        todo: Todo from dependency (with ownership verification)
        db: Database session

    Returns:
        Success message
    """
    delete_todo(db, todo.id)
    db.commit()
    return DeleteTodoResponse()
