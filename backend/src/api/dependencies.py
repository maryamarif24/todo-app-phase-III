"""
API dependencies for authentication and ownership verification.

Optimized for Neon PostgreSQL with sync database operations.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session

from ..models import User, Todo
from ..services import get_user_by_id, get_todo_by_id, verify_ownership
from ..models.database import get_db


# HTTP Bearer token security scheme
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency to get the current authenticated user.

    Args:
        credentials: Bearer token credentials
        db: Database session

    Returns:
        Authenticated User instance

    Raises:
        HTTPException: 401 if not authenticated
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID from token (simplified - in production use proper JWT/session validation)
    user_id_str = credentials.credentials
    print(f"Received token: {user_id_str}")  # Debug log

    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        import uuid

        # Handle potential UUID format variations by normalizing the string
        # Remove any whitespace and convert to lowercase
        normalized_token = user_id_str.strip().lower()

        # Attempt to parse as UUID, handling common format issues
        user_id = uuid.UUID(normalized_token)
        print(f"Parsed user ID: {user_id}")  # Debug log
    except ValueError as e:
        print(f"Invalid token format: {user_id_str}, error: {e}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token format: {user_id_str}. Please ensure you're logged in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_id(db, user_id)
    if user is None:
        print(f"User not found for ID: {user_id}")  # Debug log
        # Debug: List all users in database
        from sqlmodel import select
        all_users = db.execute(select(User)).scalars().all()
        print(f"All users in DB: {[(u.id, u.email) for u in all_users]}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print(f"Authenticated user: {user.email}")  # Debug log
    return user


def get_todo(
    todo_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Todo:
    """
    Dependency to get a todo with ownership verification.

    Args:
        todo_id: Todo UUID as string
        current_user: Authenticated user
        db: Database session

    Returns:
        Todo instance if found and owned by user

    Raises:
        HTTPException: 404 if not found, 403 if not owner
    """
    try:
        import uuid
        todo_uuid = uuid.UUID(todo_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid todo ID format",
        )

    todo = get_todo_by_id(db, todo_uuid)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    if not verify_ownership(todo, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this todo",
        )

    return todo


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Dependency to get the current user if authenticated, None otherwise.

    Used for routes that work both with and without authentication.
    """
    if not credentials:
        return None

    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None
