"""
Authentication middleware for session validation.

This module provides FastAPI dependencies for validating
authentication sessions on protected routes.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..models import User
from ..api.dependencies import get_current_user, get_optional_user


# HTTP Bearer token security scheme
bearer_scheme = HTTPBearer(auto_error=False)


class AuthenticatedUser:
    """Represents an authenticated user from session."""

    def __init__(self, user: User):
        self.user = user
        self.id = user.id
        self.email = user.email
