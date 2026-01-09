from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from datetime import datetime, date
import logging
from app.database import get_db
from app.core.security import get_current_user
from app.services.reminder_service import ReminderService
from app.models.user import User
from app.models.reminder import Reminder
from app.models.reminder_log import ReminderLog
from app.schemas.reminder import (
    Reminder as ReminderSchema,
    ReminderCreate,
    ReminderUpdate,
    ReminderFilter,
    ReminderWithMedicine,
    ReminderWithLogs,
    ReminderLog as ReminderLogSchema,
)
from app.schemas.common import PaginatedResponse, MessageResponse
from app.schemas.common import ReminderStatus


logger = logging.getLogger(__name__)

router = APIRouter()


def get_reminder_service(db: AsyncSession = Depends(get_db)) -> ReminderService:
    """Dependency to get reminder service"""
    return ReminderService(db)


@router.post("/", response_model=ReminderSchema, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    reminder_data: ReminderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """Create a new reminder"""
    try:
        reminder = await reminder_service.create_reminder(
            user_id=current_user.id,
            reminder_data=reminder_data
        )
        logger.info(f"Reminder created: ID {reminder.id} for user {current_user.id}")
        return reminder
    except ValueError as e:
        logger.warning(f"Reminder creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating reminder: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create reminder"
        )


@router.get("/", response_model=PaginatedResponse[ReminderWithMedicine])
async def get_reminders(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    medicine_id: Optional[int] = Query(None, description="Filter by medicine ID"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """Get all reminders for the current user with optional filtering"""
    try:
        filters = ReminderFilter(
            is_active=is_active,
            medicine_id=medicine_id,
            page=page,
            per_page=per_page
        )
        
        reminders, total_count = await reminder_service.get_reminders(
            user_id=current_user.id,
            filters=filters
        )
        
        pages = (total_count + per_page - 1) // per_page
        
        return PaginatedResponse(
            items=reminders,
            total=total_count,
            page=page,
            per_page=per_page,
            pages=pages
        )
    except Exception as e:
        logger.error(f"Error fetching reminders: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch reminders"
        )


@router.get("/today", response_model=list[ReminderWithMedicine])
async def get_today_reminders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """Get all reminders scheduled for today"""
    try:
        reminders = await reminder_service.get_today_reminders(user_id=current_user.id)
        return reminders
    except Exception as e:
        logger.error(f"Error fetching today's reminders: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch today's reminders"
        )


@router.get("/today-with-status", response_model=list[dict])
async def get_today_reminders_with_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """Get today's pending reminders with their status (taken/skipped/missed/pending)"""
    try:
        reminders = await reminder_service.get_today_reminders(user_id=current_user.id)
        today = date.today()
        now = datetime.now()
        
        logger.debug(f"Found {len(reminders)} reminders for today")
        
        result = []
        for reminder in reminders:
            # Get status for this reminder
            log, status = await reminder_service.get_reminder_status(reminder.id, today)
            
            logger.debug(f"Reminder {reminder.id}: status={status}, is_pending check")
            
            # Skip reminders that have been taken or skipped
            if status in [ReminderStatus.TAKEN.value, ReminderStatus.SKIPPED.value]:
                logger.debug(f"Skipping reminder {reminder.id} with status {status}")
                continue
            
            # Determine if pending (due now and not yet taken/skipped)
            reminder_datetime = datetime.combine(today, reminder.reminder_time)
            is_pending = now >= reminder_datetime and status not in [ReminderStatus.TAKEN.value, ReminderStatus.SKIPPED.value]
            
            # Build medicine name and dosage
            medicine_name = reminder.medicine.name if reminder.medicine else "Unknown"
            dosage = ""
            if reminder.dosage_amount:
                dosage = f"{reminder.dosage_amount}"
                if reminder.dosage_unit:
                    dosage += f" {reminder.dosage_unit}"
            
            # Map status for frontend
            # SKIPPED should show as 'upcoming' if not yet past time, otherwise as 'skipped'
            display_status = status
            if status == ReminderStatus.SKIPPED.value:
                display_status = "upcoming"
            elif status == ReminderStatus.MISSED.value and not is_pending:
                display_status = "missed"
            
            # Build reminder dict without the full ORM object
            reminder_dict = {
                "id": reminder.id,
                "user_id": reminder.user_id,
                "medicine_id": reminder.medicine_id,
                "prescription_id": reminder.prescription_id,
                "reminder_time": reminder.reminder_time.isoformat() if reminder.reminder_time else None,
                "frequency": reminder.frequency,
                "specific_days": reminder.specific_days,
                "interval_days": reminder.interval_days,
                "dosage_amount": reminder.dosage_amount,
                "dosage_unit": reminder.dosage_unit,
                "start_date": reminder.start_date.isoformat() if reminder.start_date else None,
                "end_date": reminder.end_date.isoformat() if reminder.end_date else None,
                "is_active": reminder.is_active,
                "notes": reminder.notes,
                "created_at": reminder.created_at.isoformat() if reminder.created_at else None,
                "updated_at": reminder.updated_at.isoformat() if reminder.updated_at else None,
            }
            
            result.append({
                "id": reminder.id,
                "medicineName": medicine_name,
                "dosage": dosage,
                "time": reminder_datetime.isoformat(),
                "status": display_status,
                "is_pending": is_pending,
                "reminder": reminder_dict
            })
        
        # Sort by time
        result.sort(key=lambda x: x["time"])
        
        logger.debug(f"Returning {len(result)} reminders for dashboard")
        
        return result
    except Exception as e:
        logger.error(f"Error fetching reminders with status: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch reminders with status"
        )


@router.get("/history")
async def get_reminder_history(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    reminder_status: Optional[str] = Query(None, description="Filter by status (taken, skipped, missed)"),
    medicine_id: Optional[int] = Query(None, description="Filter by medicine ID"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """Get reminder history with optional filtering and pagination"""
    try:
        history, total_count = await reminder_service.get_reminder_history(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            status=reminder_status,
            medicine_id=medicine_id,
            page=page,
            per_page=per_page
        )
        
        pages = (total_count + per_page - 1) // per_page
        
        return {
            "items": history,
            "total": total_count,
            "page": page,
            "per_page": per_page,
            "pages": pages
        }
    except Exception as e:
        logger.error(f"Error fetching reminder history: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch reminder history"
        )


@router.get("/mark-missed")
async def mark_overdue_reminders_missed(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """Mark all overdue reminders as missed (can be called by scheduler)"""
    try:
        count = await reminder_service.mark_overdue_reminders_as_missed(user_id=current_user.id)
        logger.info(f"Marked {count} reminders as missed for user {current_user.id}")
        return {"message": f"Marked {count} reminders as missed", "count": count}
    except Exception as e:
        logger.error(f"Error marking reminders as missed: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark reminders as missed"
        )


@router.get("/{reminder_id}", response_model=ReminderWithLogs)
async def get_reminder(
    reminder_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """Get a specific reminder by ID"""
    try:
        reminder = await reminder_service.get_reminder_by_id(
            reminder_id=reminder_id,
            user_id=current_user.id
        )
        
        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reminder with ID {reminder_id} not found"
            )
        
        return reminder
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching reminder {reminder_id}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch reminder"
        )


@router.put("/{reminder_id}", response_model=ReminderSchema)
async def update_reminder(
    reminder_id: int,
    reminder_update: ReminderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """Update a reminder"""
    try:
        reminder = await reminder_service.update_reminder(
            reminder_id=reminder_id,
            user_id=current_user.id,
            reminder_update=reminder_update
        )
        
        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reminder with ID {reminder_id} not found"
            )
        
        logger.info(f"Reminder {reminder_id} updated for user {current_user.id}")
        return reminder
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating reminder {reminder_id}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update reminder"
        )


@router.delete("/{reminder_id}")
async def delete_reminder(
    reminder_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """Delete a reminder"""
    try:
        success = await reminder_service.delete_reminder(
            reminder_id=reminder_id,
            user_id=current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reminder with ID {reminder_id} not found"
            )
        
        logger.info(f"Reminder {reminder_id} deleted for user {current_user.id}")
        return MessageResponse(
            message="Reminder deleted successfully",
            success=True
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting reminder {reminder_id}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete reminder"
        )


@router.post("/{reminder_id}/take", response_model=ReminderLogSchema)
async def mark_reminder_taken(
    reminder_id: int,
    notes: Optional[str] = Query(None, description="Optional notes"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """Mark a reminder as taken"""
    try:
        log = await reminder_service.mark_reminder_taken(
            reminder_id=reminder_id,
            user_id=current_user.id,
            notes=notes
        )
        
        logger.info(f"Reminder {reminder_id} marked as taken by user {current_user.id}")
        return log
    except ValueError as e:
        logger.warning(f"Failed to mark reminder as taken: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error marking reminder {reminder_id} as taken: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark reminder as taken"
        )


@router.post("/{reminder_id}/skip", response_model=ReminderLogSchema)
async def mark_reminder_skipped(
    reminder_id: int,
    notes: Optional[str] = Query(None, description="Optional notes"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """Mark a reminder as skipped"""
    try:
        log = await reminder_service.mark_reminder_skipped(
            reminder_id=reminder_id,
            user_id=current_user.id,
            notes=notes
        )
        
        logger.info(f"Reminder {reminder_id} marked as skipped by user {current_user.id}")
        return log
    except ValueError as e:
        logger.warning(f"Failed to mark reminder as skipped: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error marking reminder {reminder_id} as skipped: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark reminder as skipped"
        )


@router.get("/adherence/stats")
async def get_adherence_stats(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """Get adherence statistics for a date range"""
    try:
        stats = await reminder_service.get_adherence_stats(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        return stats
    except Exception as e:
        logger.error(f"Error fetching adherence stats: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch adherence statistics"
        )


@router.get("/adherence/daily")
async def get_daily_adherence(
    days: int = Query(7, ge=1, le=365, description="Number of days to fetch"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """Get daily adherence data for the past N days"""
    try:
        daily_data = await reminder_service.get_daily_adherence(
            user_id=current_user.id,
            days=days
        )
        return daily_data
    except Exception as e:
        logger.error(f"Error fetching daily adherence: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch daily adherence data"
        )


@router.get("/adherence/streak")
async def get_adherence_streak(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """Get current and longest adherence streak"""
    try:
        streak = await reminder_service.get_adherence_streak(
            user_id=current_user.id
        )
        return streak
    except Exception as e:
        logger.error(f"Error fetching adherence streak: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch adherence streak"
        )


@router.get("/adherence/by-medicine")
async def get_medicine_adherence(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """Get adherence breakdown by medicine"""
    try:
        medicine_stats = await reminder_service.get_medicine_adherence(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        return medicine_stats
    except Exception as e:
        logger.error(f"Error fetching medicine adherence: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch medicine adherence data"
        )



