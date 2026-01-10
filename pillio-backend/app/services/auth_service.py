from datetime import timedelta, datetime
from typing import Optional, Tuple
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.schemas.common import Token
from app.utils.password import get_password_hash, verify_password, validate_password_strength
from app.utils.jwt import create_access_token, create_refresh_token, verify_access_token
from app.config import settings

logger = logging.getLogger(__name__)


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
        logger.info(f"Attempting to register user with email: {user_data.email}")
        
        try:
            # Check if user already exists
            existing_user = await self.get_user_by_email(user_data.email)
            if existing_user:
                logger.warning(f"Registration failed: User with email {user_data.email} already exists")
                raise ValueError("User with this email already exists")
            
            # Validate password strength
            is_valid, errors = validate_password_strength(user_data.password)
            if not is_valid:
                logger.warning(f"Registration failed: Password validation failed for {user_data.email}")
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
            
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            
            # Generate tokens
            tokens = await self.create_tokens_for_user(user)
            
            logger.info(f"User registered successfully: {user_data.email} (ID: {user.id})")
            return user, tokens
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error during user registration: {e}")
            raise ValueError(f"Failed to create user: Database error occurred")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error during user registration: {e}")
            raise
    
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
        logger.info(f"Authentication attempt for email: {login_data.email}")
        
        try:
            user = await self.get_user_by_email(login_data.email)
            if not user:
                logger.warning(f"Authentication failed: User not found for email {login_data.email}")
                raise ValueError("Invalid email or password")
            
            if not verify_password(login_data.password, user.password_hash):
                logger.warning(f"Authentication failed: Invalid password for email {login_data.email}")
                raise ValueError("Invalid email or password")
            
            if not user.is_active:
                logger.warning(f"Authentication failed: Account disabled for email {login_data.email}")
                raise ValueError("User account is disabled")
            
            # Check if user was soft deleted and restore if within 14 days
            if user.is_deleted and user.deletion_reason:
                # Extract timestamp from deletion_reason (format: "[timestamp] reason")
                try:
                    timestamp_str = user.deletion_reason.split(']')[0].strip('[')
                    deleted_at = datetime.fromisoformat(timestamp_str)
                    days_since_deletion = (datetime.utcnow() - deleted_at).days
                    
                    if days_since_deletion < 14:
                        # Restore the user account
                        user.is_deleted = False
                        user.deletion_reason = None
                        await self.db.commit()
                        logger.info(f"User account restored after soft delete: {login_data.email} ({days_since_deletion} days since deletion)")
                    else:
                        logger.warning(f"Authentication failed: Account deleted more than 14 days ago for email {login_data.email}")
                        raise ValueError("This account has been deleted and cannot be restored")
                except (ValueError, IndexError):
                    logger.warning(f"Could not parse deletion_reason for user {login_data.email}, treating as permanently deleted")
                    raise ValueError("This account has been deleted and cannot be restored")
            
            # Generate tokens
            tokens = await self.create_tokens_for_user(user)
            
            logger.info(f"User authenticated successfully: {login_data.email} (ID: {user.id})")
            return user, tokens
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {e}")
            raise ValueError("Authentication failed due to an internal error")
    
    async def create_tokens_for_user(self, user: User) -> Token:
        """Create access and refresh tokens for a user"""
        logger.debug(f"Creating tokens for user: {user.email}")
        
        try:
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
        except Exception as e:
            logger.error(f"Error creating tokens for user {user.email}: {e}")
            raise
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[Token]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token if refresh token is valid, None otherwise
        """
        logger.debug("Attempting to refresh access token")
        
        try:
            from app.utils.jwt import verify_refresh_token
            
            token_data = verify_refresh_token(refresh_token)
            if not token_data:
                logger.warning("Token refresh failed: Invalid refresh token")
                return None
            
            user = await self.get_user_by_id(token_data.user_id)
            if not user or not user.is_active:
                logger.warning(f"Token refresh failed: User not found or inactive (ID: {token_data.user_id})")
                return None
            
            # Create new tokens
            new_tokens = await self.create_tokens_for_user(user)
            logger.info(f"Token refreshed successfully for user: {user.email}")
            return new_tokens
            
        except Exception as e:
            logger.error(f"Error during token refresh: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address"""
        logger.debug(f"Looking up user by email: {email}")
        
        try:
            result = await self.db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            if user:
                logger.debug(f"User found by email: {email}")
            else:
                logger.debug(f"No user found with email: {email}")
            return user
        except SQLAlchemyError as e:
            logger.error(f"Database error looking up user by email {email}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error looking up user by email {email}: {e}")
            return None
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        logger.debug(f"Looking up user by ID: {user_id}")
        
        try:
            result = await self.db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                logger.debug(f"User found by ID: {user_id}")
            else:
                logger.debug(f"No user found with ID: {user_id}")
            return user
        except SQLAlchemyError as e:
            logger.error(f"Database error looking up user by ID {user_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error looking up user by ID {user_id}: {e}")
            return None
    
    async def verify_token(self, token: str) -> Optional[User]:
        """
        Verify JWT token and return associated user
        
        Args:
            token: JWT access token
            
        Returns:
            User object if token is valid, None otherwise
        """
        logger.debug("Verifying JWT token")
        
        try:
            token_data = verify_access_token(token)
            if not token_data:
                logger.warning("Token verification failed: Invalid token")
                return None
            
            user = await self.get_user_by_id(token_data.user_id)
            if not user or not user.is_active:
                logger.warning(f"Token verification failed: User not found or inactive (ID: {token_data.user_id})")
                return None
            
            logger.debug(f"Token verified successfully for user: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"Error during token verification: {e}")
            return None
    
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
        logger.info(f"Password change attempt for user ID: {user_id}")
        
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                logger.warning(f"Password change failed: User not found (ID: {user_id})")
                raise ValueError("User not found")
            
            # Verify current password
            if not verify_password(current_password, user.password_hash):
                logger.warning(f"Password change failed: Incorrect current password for user ID: {user_id}")
                raise ValueError("Current password is incorrect")
            
            # Validate new password
            is_valid, errors = validate_password_strength(new_password)
            if not is_valid:
                logger.warning(f"Password change failed: New password validation failed for user ID: {user_id}")
                raise ValueError(f"New password validation failed: {'; '.join(errors)}")
            
            # Update password
            user.password_hash = get_password_hash(new_password)
            await self.db.commit()
            
            logger.info(f"Password changed successfully for user ID: {user_id}")
            return True
            
        except ValueError:
            raise
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error during password change for user ID {user_id}: {e}")
            raise ValueError("Failed to change password due to database error")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error during password change for user ID {user_id}: {e}")
            raise ValueError("Failed to change password due to an internal error")
    
    async def update_user_profile(self, user_id: int, **kwargs) -> Optional[User]:
        """
        Update user profile information
        
        Args:
            user_id: User ID
            **kwargs: Fields to update
            
        Returns:
            Updated user object
        """
        logger.info(f"Profile update attempt for user ID: {user_id}")
        
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                logger.warning(f"Profile update failed: User not found (ID: {user_id})")
                return None
            
            # Update allowed fields
            allowed_fields = ['first_name', 'last_name', 'phone', 'date_of_birth', 'email']
            
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(user, field):
                    setattr(user, field, value)
            
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(f"Profile updated successfully for user ID: {user_id}")
            return user
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error during profile update for user ID {user_id}: {e}")
            return None
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error during profile update for user ID {user_id}: {e}")
            return None
    
    async def deactivate_user(self, user_id: int) -> bool:
        """
        Deactivate user account
        
        Args:
            user_id: User ID
            
        Returns:
            True if user was deactivated
        """
        logger.info(f"Account deactivation attempt for user ID: {user_id}")
        
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                logger.warning(f"Account deactivation failed: User not found (ID: {user_id})")
                return False
            
            user.is_active = False
            await self.db.commit()
            
            logger.info(f"Account deactivated successfully for user ID: {user_id}")
            return True
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error during account deactivation for user ID {user_id}: {e}")
            return False
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error during account deactivation for user ID {user_id}: {e}")
            return False
    
    async def activate_user(self, user_id: int) -> bool:
        """
        Activate user account
        
        Args:
            user_id: User ID
            
        Returns:
            True if user was activated
        """
        logger.info(f"Account activation attempt for user ID: {user_id}")
        
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                logger.warning(f"Account activation failed: User not found (ID: {user_id})")
                return False
            
            user.is_active = True
            await self.db.commit()
            
            logger.info(f"Account activated successfully for user ID: {user_id}")
            return True
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error during account activation for user ID {user_id}: {e}")
            return False
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error during account activation for user ID {user_id}: {e}")
            return False
