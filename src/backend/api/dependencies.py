"""
Common dependencies for FastAPI routes.
"""

from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session"""
    async for session in get_db():
        yield session


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency to get the current authenticated user.
    Usage:
        @app.get("/users/me")
        async def read_users_me(current_user = Depends(get_current_user)):
            return current_user
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication not implemented",
    )
