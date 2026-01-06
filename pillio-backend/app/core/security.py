from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.auth_service import AuthService
from app.models.user import User
from app.schemas.common import TokenData
from app.utils.jwt import verify_access_token


# Security scheme for JWT tokens
security = HTTPBearer()


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        db: Database session
        credentials: JWT token credentials
        
    Returns:
        Current user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token
        token_data = verify_access_token(credentials.credentials)
        if token_data is None:
            raise credentials_exception
        
        # Get user from database
        auth_service = AuthService(db)
        user = await auth_service.get_user_by_id(token_data.user_id)
        
        if user is None:
            raise credentials_exception
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        return user
        
    except Exception:
        raise credentials_exception


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current active user (alias for get_current_user)
    
    Args:
        current_user: Current user from JWT token
        
    Returns:
        Current active user
    """
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current superuser
    
    Args:
        current_user: Current user from JWT token
        
    Returns:
        Current superuser
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_optional_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """
    Get current user if token is provided, otherwise return None
    
    Args:
        db: Database session
        credentials: Optional JWT token credentials
        
    Returns:
        Current user if token is valid, None otherwise
    """
    if not credentials:
        return None
    
    try:
        auth_service = AuthService(db)
        return await auth_service.verify_token(credentials.credentials)
    except Exception:
        return None


def create_access_token_for_user(user: User) -> str:
    """
    Create access token for a user
    
    Args:
        user: User object
        
    Returns:
        JWT access token
    """
    from datetime import timedelta
    from app.utils.jwt import create_access_token
    from app.config import settings
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    
    token_data = {
        "sub": user.email,
        "user_id": user.id,
        "type": "access"
    }
    
    return create_access_token(token_data, access_token_expires)


def create_refresh_token_for_user(user: User) -> str:
    """
    Create refresh token for a user
    
    Args:
        user: User object
        
    Returns:
        JWT refresh token
    """
    from app.utils.jwt import create_refresh_token
    
    token_data = {
        "sub": user.email,
        "user_id": user.id,
        "type": "refresh"
    }
    
    return create_refresh_token(token_data)


class TokenData:
    """Token data class for type hints"""
    def __init__(self, email: str, user_id: int):
        self.email = email
        self.user_id = user_id