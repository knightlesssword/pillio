from datetime import timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.schemas.common import Token
from app.utils.password import get_password_hash, verify_password, validate_password_strength
from app.utils.jwt import create_access_token, create_refresh_token, verify_access_token
from app.config import settings


class AuthService:
    """Service for handling authentication operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register_user(self, user_data: UserCreate) -> Tuple[User, Token]:
        """
        Register a new user and return the user object and tokens
        
        Args:
            user_data: User registration data
            
        Returns:
            Tuple of (User, Token)
            
        Raises:
            ValueError: If user already exists or password validation fails
        """
        # Check if user already exists
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Validate password strength
        is_valid, errors = validate_password_strength(user_data.password)
        if not is_valid:
            raise ValueError(f"Password validation failed: {'; '.join(errors)}")
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        
        user = User(
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            date_of_birth=user_data.date_of_birth,
            is_active=True,
            is_superuser=False
        )
        
        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            
            # Generate tokens
            tokens = await self.create_tokens_for_user(user)
            
            return user, tokens
        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"Failed to create user: {str(e)}")
    
    async def authenticate_user(self, login_data: UserLogin) -> Tuple[User, Token]:
        """
        Authenticate user with email and password
        
        Args:
            login_data: User login data
            
        Returns:
            Tuple of (User, Token)
            
        Raises:
            ValueError: If credentials are invalid
        """
        user = await self.get_user_by_email(login_data.email)
        if not user:
            raise ValueError("Invalid email or password")
        
        if not verify_password(login_data.password, user.password_hash):
            raise ValueError("Invalid email or password")
        
        if not user.is_active:
            raise ValueError("User account is disabled")
        
        # Generate tokens
        tokens = await self.create_tokens_for_user(user)
        
        return user, tokens
    
    async def create_tokens_for_user(self, user: User) -> Token:
        """Create access and refresh tokens for a user"""
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        
        access_token_data = {
            "sub": user.email,
            "user_id": user.id,
            "type": "access"
        }
        
        refresh_token_data = {
            "sub": user.email,
            "user_id": user.id,
            "type": "refresh"
        }
        
        access_token = create_access_token(access_token_data, access_token_expires)
        refresh_token = create_refresh_token(refresh_token_data)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[Token]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token if refresh token is valid, None otherwise
        """
        from app.utils.jwt import verify_refresh_token
        
        token_data = verify_refresh_token(refresh_token)
        if not token_data:
            return None
        
        user = await self.get_user_by_id(token_data.user_id)
        if not user or not user.is_active:
            return None
        
        # Create new tokens
        return await self.create_tokens_for_user(user)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address"""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def verify_token(self, token: str) -> Optional[User]:
        """
        Verify JWT token and return associated user
        
        Args:
            token: JWT access token
            
        Returns:
            User object if token is valid, None otherwise
        """
        token_data = verify_access_token(token)
        if not token_data:
            return None
        
        user = await self.get_user_by_id(token_data.user_id)
        if not user or not user.is_active:
            return None
        
        return user
    
    async def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """
        Change user password
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            True if password was changed successfully
            
        Raises:
            ValueError: If current password is incorrect or new password is invalid
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")
        
        # Validate new password
        is_valid, errors = validate_password_strength(new_password)
        if not is_valid:
            raise ValueError(f"New password validation failed: {'; '.join(errors)}")
        
        # Update password
        user.password_hash = get_password_hash(new_password)
        await self.db.commit()
        
        return True
    
    async def update_user_profile(self, user_id: int, **kwargs) -> Optional[User]:
        """
        Update user profile information
        
        Args:
            user_id: User ID
            **kwargs: Fields to update
            
        Returns:
            Updated user object
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'phone', 'date_of_birth', 'email']
        
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(user, field):
                setattr(user, field, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def deactivate_user(self, user_id: int) -> bool:
        """
        Deactivate user account
        
        Args:
            user_id: User ID
            
        Returns:
            True if user was deactivated
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        await self.db.commit()
        
        return True
    
    async def activate_user(self, user_id: int) -> bool:
        """
        Activate user account
        
        Args:
            user_id: User ID
            
        Returns:
            True if user was activated
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = True
        await self.db.commit()
        
        return True