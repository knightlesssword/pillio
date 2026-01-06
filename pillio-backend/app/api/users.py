from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date, timedelta
import logging
from app.database import get_db
from app.core.security import get_current_user, get_current_superuser
from app.api.deps import get_auth_service_dep
from app.services.auth_service import AuthService
from app.models.user import User
from app.models.medicine import Medicine
from app.models.reminder import Reminder
from app.models.reminder_log import ReminderLog
from app.schemas.user import User as UserSchema, UserUpdate
from app.schemas.common import MessageResponse, PaginatedResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/profile", response_model=UserSchema)
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's profile information
    """
    return current_user


@router.put("/profile", response_model=UserSchema)
async def update_user_profile(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service_dep)
):
    """
    Update current user's profile
    
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
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already in use"
                )
        
        # Update user
        updated_user = await auth_service.update_user_profile(
            user_id=current_user.id,
            **user_update.dict(exclude_unset=True)
        )
        
        if not updated_user:
            logger.warning(f"Profile update failed: User {current_user.id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"Profile updated for user: {updated_user.email}")
        return updated_user
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Profile update error for user {current_user.id}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


@router.delete("/account")
async def delete_user_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service_dep)
):
    """
    Delete current user's account
    
    Note: In a production system, you might want to:
    1. Soft delete (deactivate) instead of hard delete
    2. Anonymize personal data
    3. Archive data for compliance
    """
    try:
        # Soft delete by deactivating the account
        success = await auth_service.deactivate_user(current_user.id)
        
        if not success:
            logger.warning(f"Account deletion failed: User {current_user.id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"Account deactivated for user: {current_user.email}")
        return MessageResponse(
            message="Account deactivated successfully",
            success=True
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Account deletion error for user {current_user.id}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deletion failed"
        )


@router.get("/stats")
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user statistics for dashboard
    """
    try:
        # Get total medicines count
        medicines_count = await db.scalar(
            select(func.count(Medicine.id)).where(Medicine.user_id == current_user.id)
        ) or 0
        
        # Get low stock medicines count
        low_stock_count = await db.scalar(
            select(func.count(Medicine.id)).where(
                Medicine.user_id == current_user.id,
                Medicine.current_stock <= Medicine.min_stock_alert
            )
        ) or 0
        
        # Get today's reminders count
        today = date.today()
        today_reminders_count = await db.scalar(
            select(func.count(Reminder.id)).where(
                Reminder.user_id == current_user.id,
                Reminder.is_active == True,
                Reminder.start_date <= today,
                (Reminder.end_date >= today) | (Reminder.end_date.is_(None))
            )
        ) or 0
        
        # Get completed reminders today
        completed_today_count = await db.scalar(
            select(func.count(ReminderLog.id)).where(
                ReminderLog.reminder_id.in_(
                    select(Reminder.id).where(Reminder.user_id == current_user.id)
                ),
                func.date(ReminderLog.scheduled_time) == today,
                ReminderLog.status == "taken"
            )
        ) or 0
        
        # Calculate adherence rate (last 30 days)
        thirty_days_ago = today - timedelta(days=30)
        total_reminders = await db.scalar(
            select(func.count(ReminderLog.id)).where(
                ReminderLog.reminder_id.in_(
                    select(Reminder.id).where(Reminder.user_id == current_user.id)
                ),
                func.date(ReminderLog.scheduled_time) >= thirty_days_ago
            )
        ) or 0
        
        completed_reminders = await db.scalar(
            select(func.count(ReminderLog.id)).where(
                ReminderLog.reminder_id.in_(
                    select(Reminder.id).where(Reminder.user_id == current_user.id)
                ),
                func.date(ReminderLog.scheduled_time) >= thirty_days_ago,
                ReminderLog.status == "taken"
            )
        ) or 0
        
        adherence_rate = (completed_reminders / total_reminders * 100) if total_reminders > 0 else 0
        
        stats = {
            "total_medicines": medicines_count,
            "today_reminders": today_reminders_count,
            "completed_today": completed_today_count,
            "low_stock_count": low_stock_count,
            "adherence_rate": round(adherence_rate, 2)
        }
        
        logger.debug(f"User stats fetched for {current_user.email}: {stats}")
        return stats
    
    except Exception as e:
        logger.error(f"Error fetching user stats for {current_user.id}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user statistics"
        )


# Admin endpoints (require superuser privileges)

@router.get("/", response_model=PaginatedResponse[UserSchema])
async def get_all_users(
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Get all users (admin only)
    
    - **page**: Page number (default: 1)
    - **per_page**: Items per page (default: 20, max: 100)
    """
    try:
        offset = (page - 1) * per_page
        
        # Get total count
        total_count = await db.scalar(select(func.count(User.id))) or 0
        
        # Get users for current page
        result = await db.execute(
            select(User)
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(per_page)
        )
        users = result.scalars().all()
        
        logger.debug(f"Admin {current_user.email} fetched {len(users)} users (page {page})")
        return PaginatedResponse(
            items=users,
            total=total_count,
            page=page,
            per_page=per_page,
            pages=(total_count + per_page - 1) // per_page
        )
    
    except Exception as e:
        logger.error(f"Error fetching all users: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users"
        )


@router.get("/{user_id}", response_model=UserSchema)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Get user by ID (admin only)
    """
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"Admin {current_user.email} tried to fetch non-existent user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.debug(f"Admin {current_user.email} fetched user {user_id}")
        return user
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user"
        )


@router.put("/{user_id}/activate")
async def activate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
    auth_service: AuthService = Depends(get_auth_service_dep)
):
    """
    Activate user account (admin only)
    """
    try:
        success = await auth_service.activate_user(user_id)
        
        if not success:
            logger.warning(f"Admin {current_user.email} tried to activate non-existent user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"Admin {current_user.email} activated user {user_id}")
        return MessageResponse(
            message="User activated successfully",
            success=True
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error activating user {user_id}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate user"
        )


@router.put("/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
    auth_service: AuthService = Depends(get_auth_service_dep)
):
    """
    Deactivate user account (admin only)
    """
    try:
        success = await auth_service.deactivate_user(user_id)
        
        if not success:
            logger.warning(f"Admin {current_user.email} tried to deactivate non-existent user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"Admin {current_user.email} deactivated user {user_id}")
        return MessageResponse(
            message="User deactivated successfully",
            success=True
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error deactivating user {user_id}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate user"
        )
