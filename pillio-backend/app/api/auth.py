from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from app.database import get_db
from app.core.security import get_current_user
from app.api.deps import get_auth_service_dep
from app.services.auth_service import AuthService
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, User as UserSchema, UserUpdate
from app.schemas.common import Token, MessageResponse, PasswordReset, PasswordResetConfirm, RefreshTokenRequest
from app.core.exceptions import (
    UserAlreadyExistsException, InvalidCredentialsException,
    InactiveUserException, UserNotFoundException
)
from app.utils.password import verify_password_reset_token

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service_dep)
):
    """
    Register a new user
    
    - **email**: User's email address (must be unique)
    - **password**: Strong password (min 8 chars, uppercase, lowercase, number, special char)
    - **first_name**: User's first name (optional)
    - **last_name**: User's last name (optional)
    - **phone**: Phone number (optional)
    - **date_of_birth**: Date of birth (optional)
    """
    try:
        user, token = await auth_service.register_user(user_data)
        logger.info(f"New user registered: {user.email} (ID: {user.id})")
        
        return Token(
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            token_type=token.token_type,
            expires_in=token.expires_in
        )
    
    except ValueError as e:
        error_msg = str(e)
        if "already exists" in error_msg:
            logger.warning(f"Registration failed: User {user_data.email} already exists")
            raise UserAlreadyExistsException(user_data.email)
        elif "validation failed" in error_msg:
            logger.warning(f"Registration validation failed for {user_data.email}: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        elif "Failed to create user" in error_msg:
            logger.error(f"Registration failed for {user_data.email}: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed due to server error"
            )
        else:
            logger.warning(f"Registration failed for {user_data.email}: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    except Exception as e:
        logger.error(f"Registration error for {user_data.email}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to server error"
        )


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service_dep)
):
    """
    Authenticate user and return JWT tokens
    
    - **email**: User's email address
    - **password**: User's password
    """
    try:
        user, token = await auth_service.authenticate_user(login_data)
        logger.info(f"User logged in: {user.email} (ID: {user.id})")
        
        return Token(
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            token_type=token.token_type,
            expires_in=token.expires_in
        )
    
    except ValueError as e:
        error_msg = str(e)
        if "Invalid email or password" in error_msg:
            logger.warning(f"Login failed: Invalid credentials for {login_data.email}")
            raise InvalidCredentialsException()
        elif "disabled" in error_msg:
            logger.warning(f"Login failed: Account disabled for {login_data.email}")
            raise InactiveUserException()
        else:
            logger.warning(f"Login failed for {login_data.email}: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
    
    except Exception as e:
        logger.error(f"Login error for {login_data.email}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service_dep)
):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token
    """
    try:
        new_token = await auth_service.refresh_access_token(refresh_request.refresh_token)
        
        if not new_token:
            logger.warning("Token refresh failed: Invalid refresh token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info("Token refreshed successfully")
        return Token(
            access_token=new_token.access_token,
            refresh_token=new_token.refresh_token,
            token_type=new_token.token_type,
            expires_in=new_token.expires_in
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Token refresh error: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout user (client should discard tokens)
    
    Note: In a stateless JWT system, logout is handled client-side
    by removing stored tokens. This endpoint can be used for logging.
    """
    logger.info(f"User logged out: {current_user.email}")
    return MessageResponse(
        message="Successfully logged out",
        success=True
    )


@router.get("/me", response_model=UserSchema)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user profile information
    """
    return current_user


@router.put("/me", response_model=UserSchema)
async def update_current_user_profile(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service_dep)
):
    """
    Update current user profile
    
    - **email**: New email address (optional)
    - **first_name**: New first name (optional)
    - **last_name**: New last name (optional)
    - **phone**: New phone number (optional)
    - **date_of_birth**: New date of birth (optional)
    """
    try:
        # Check if email is being changed and if it's already taken
        if user_update.email and user_update.email != current_user.email:
            existing_user = await auth_service.get_user_by_email(user_update.email)
            if existing_user:
                logger.warning(f"Profile update failed: Email {user_update.email} already in use")
                raise UserAlreadyExistsException(user_update.email)
        
        # Update user
        updated_user = await auth_service.update_user_profile(
            user_id=current_user.id,
            **user_update.dict(exclude_unset=True)
        )
        
        if not updated_user:
            logger.warning(f"Profile update failed: User {current_user.id} not found")
            raise UserNotFoundException(current_user.id)
        
        logger.info(f"Profile updated for user: {updated_user.email}")
        return updated_user
    
    except UserAlreadyExistsException:
        raise
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Profile update error for user {current_user.id}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service_dep)
):
    """
    Change user password
    
    - **current_password**: Current password
    - **new_password**: New password (must meet strength requirements)
    """
    try:
        await auth_service.change_password(
            user_id=current_user.id,
            current_password=current_password,
            new_password=new_password
        )
        
        logger.info(f"Password changed for user: {current_user.email}")
        return MessageResponse(
            message="Password changed successfully",
            success=True
        )
    
    except ValueError as e:
        error_msg = str(e)
        if "Current password is incorrect" in error_msg:
            logger.warning(f"Password change failed: Incorrect password for {current_user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        elif "validation failed" in error_msg:
            logger.warning(f"Password validation failed for {current_user.email}: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        else:
            logger.warning(f"Password change failed for {current_user.email}: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
    
    except Exception as e:
        logger.error(f"Password change error for {current_user.email}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.post("/forgot-password")
async def forgot_password(
    password_reset: PasswordReset,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service_dep)
):
    """
    Request password reset
    
    - **email**: User's email address
    
    Sends a password reset link to the user's email.
    """
    try:
        user = await auth_service.get_user_by_email(password_reset.email)
        
        if user:
            # Generate a reset token (this would be sent via email in production)
            from app.utils.password import create_password_reset_token
            reset_token = create_password_reset_token(user.email)
            logger.info(f"Password reset token generated for user: {user.email}")
            # In production, you would send this token via email
            # For now, we just log it
            logger.debug(f"Reset token (debug): {reset_token}")
        
        # Always return success to prevent email enumeration
        logger.debug(f"Password reset requested for email: {password_reset.email}")
        return MessageResponse(
            message="If an account with that email exists, a password reset link has been sent",
            success=True
        )
    
    except Exception as e:
        logger.error(f"Password reset request error for {password_reset.email}: {type(e).__name__}: {str(e)}", exc_info=True)
        # Don't reveal whether the email exists or not
        return MessageResponse(
            message="If an account with that email exists, a password reset link has been sent",
            success=True
        )


@router.post("/reset-password")
async def reset_password(
    password_reset_confirm: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service_dep)
):
    """
    Reset password using reset token
    
    - **token**: Password reset token (from email)
    - **new_password**: New password
    """
    try:
        # Verify reset token
        email = verify_password_reset_token(password_reset_confirm.token)
        
        if not email:
            logger.warning("Password reset failed: Invalid or expired reset token")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Get user and reset password
        user = await auth_service.get_user_by_email(email)
        if not user:
            logger.warning(f"Password reset failed: User not found for email {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
        
        from app.utils.password import get_password_hash, validate_password_strength
        
        # Validate new password
        is_valid, errors = validate_password_strength(password_reset_confirm.new_password)
        if not is_valid:
            logger.warning(f"Password validation failed for {email}: {errors}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {'; '.join(errors)}"
            )
        
        # Update password
        user.password_hash = get_password_hash(password_reset_confirm.new_password)
        await db.commit()
        
        logger.info(f"Password reset successfully for user: {email}")
        return MessageResponse(
            message="Password reset successfully",
            success=True
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Password reset error: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )
