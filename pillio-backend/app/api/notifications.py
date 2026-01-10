from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.notification_service import NotificationService
from app.schemas.notification import (
    Notification as NotificationSchema,
    NotificationCreate,
    NotificationUpdate,
    NotificationFilter,
    NotificationCount,
    BulkNotificationUpdate,
    NotificationActionRequest,
)
from app.schemas.common import MessageResponse
from app.core.exceptions import NotFoundException, BadRequestException

router = APIRouter()


@router.get("", response_model=dict)
async def get_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    type: Optional[str] = Query(None, description="Filter by notification type"),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    reference_type: Optional[str] = Query(None, description="Filter by reference type"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """Get all notifications for the current user"""
    service = NotificationService(db)
    
    filters = NotificationFilter(
        type=type,
        is_read=is_read,
        reference_type=reference_type,
        page=page,
        per_page=per_page,
    )
    
    notifications, total = await service.get_user_notifications(current_user.id, filters)
    
    return {
        "items": [NotificationSchema.model_validate(n) for n in notifications],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
    }


@router.get("/counts", response_model=NotificationCount)
async def get_notification_counts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get notification counts by type and read status"""
    service = NotificationService(db)
    return await service.get_notification_counts(current_user.id)


@router.get("/{notification_id}", response_model=NotificationSchema)
async def get_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific notification by ID"""
    service = NotificationService(db)
    notification = await service.get_notification_by_id(notification_id, current_user.id)
    
    if not notification:
        raise NotFoundException(f"Notification with ID {notification_id} not found")
    
    return notification


@router.put("/{notification_id}/read", response_model=NotificationSchema)
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a notification as read"""
    service = NotificationService(db)
    notification = await service.mark_as_read(notification_id, current_user.id)
    
    if not notification:
        raise NotFoundException(f"Notification with ID {notification_id} not found")
    
    return notification


@router.put("/{notification_id}/taken", response_model=NotificationSchema)
async def mark_notification_taken(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a notification as taken (✓ tick action)"""
    service = NotificationService(db)
    notification = await service.mark_taken(notification_id, current_user.id)
    
    if not notification:
        raise NotFoundException(f"Notification with ID {notification_id} not found")
    
    return notification


@router.put("/{notification_id}/skipped", response_model=NotificationSchema)
async def mark_notification_skipped(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a notification as skipped (✗ cross action)"""
    service = NotificationService(db)
    notification = await service.mark_skipped(notification_id, current_user.id)
    
    if not notification:
        raise NotFoundException(f"Notification with ID {notification_id} not found")
    
    return notification


@router.put("/{notification_id}/action", response_model=NotificationSchema)
async def take_notification_action(
    notification_id: int,
    action_request: NotificationActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Take an action on a notification (taken, skipped, snoozed, dismissed)"""
    service = NotificationService(db)
    notification = await service.take_action(notification_id, current_user.id, action_request)
    
    if not notification:
        raise NotFoundException(f"Notification with ID {notification_id} not found")
    
    return notification


@router.put("/read-all", response_model=dict)
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all notifications as read"""
    service = NotificationService(db)
    count = await service.mark_all_as_read(current_user.id)
    
    return {
        "message": f"Marked {count} notifications as read",
        "count": count,
    }


@router.put("", response_model=dict)
async def bulk_update_notifications(
    update_data: BulkNotificationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bulk update notifications (mark as read/unread)"""
    service = NotificationService(db)
    count = await service.bulk_update(current_user.id, update_data)
    
    status = "read" if update_data.is_read else "unread"
    return {
        "message": f"Updated {count} notifications to {status}",
        "count": count,
    }


@router.delete("/{notification_id}", response_model=MessageResponse)
async def delete_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a notification"""
    service = NotificationService(db)
    deleted = await service.delete_notification(notification_id, current_user.id)
    
    if not deleted:
        raise NotFoundException(f"Notification with ID {notification_id} not found")
    
    return MessageResponse(message="Notification deleted successfully")


@router.delete("", response_model=dict)
async def clear_all_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete all notifications for the current user"""
    service = NotificationService(db)
    count = await service.clear_all_notifications(current_user.id)
    
    return {
        "message": f"Deleted {count} notifications",
        "count": count,
    }


@router.delete("/cleanup", response_model=dict)
async def cleanup_old_notifications(
    days_old: int = Query(30, ge=1, le=365, description="Delete notifications older than this many days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete notifications older than specified days"""
    service = NotificationService(db)
    count = await service.cleanup_old_notifications(current_user.id, days_old)
    
    return {
        "message": f"Cleaned up {count} notifications older than {days_old} days",
        "count": count,
    }


# ========== Notification Trigger Endpoints ==========

@router.post("/triggers/check-low-stock", response_model=dict)
async def trigger_low_stock_check(
    medicine_id: Optional[int] = Query(None, description="Specific medicine ID to check (optional)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually trigger low stock check for the current user"""
    from app.services.notification_triggers import NotificationTriggers
    
    service = NotificationTriggers(db)
    notifications = await service.check_and_notify_low_stock(current_user.id, medicine_id)
    
    return {
        "message": f"Low stock check completed",
        "notifications_created": len(notifications),
        "medicine_id": medicine_id,
    }


@router.post("/triggers/check-refill", response_model=dict)
async def trigger_refill_check(
    medicine_id: Optional[int] = Query(None, description="Specific medicine ID to check (optional)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually trigger refill check for the current user"""
    from app.services.notification_triggers import NotificationTriggers
    
    service = NotificationTriggers(db)
    notifications = await service.check_and_notify_refill(current_user.id, medicine_id)
    
    return {
        "message": f"Refill check completed",
        "notifications_created": len(notifications),
        "medicine_id": medicine_id,
    }


@router.post("/triggers/check-prescriptions", response_model=dict)
async def trigger_prescription_check(
    days_ahead: int = Query(30, ge=1, le=365, description="Days to look ahead for expiring prescriptions"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually trigger prescription expiry check for the current user"""
    from app.services.notification_triggers import NotificationTriggers
    
    service = NotificationTriggers(db)
    notifications = await service.check_and_notify_prescription_expiry(current_user.id, days_ahead)
    
    return {
        "message": f"Prescription expiry check completed",
        "notifications_created": len(notifications),
        "days_ahead": days_ahead,
    }


@router.post("/triggers/check-adherence", response_model=dict)
async def trigger_adherence_check(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually trigger adherence pattern check for the current user"""
    from app.services.notification_triggers import NotificationTriggers
    
    service = NotificationTriggers(db)
    notifications = await service.check_adherence_patterns(current_user.id)
    
    return {
        "message": f"Adherence check completed",
        "notifications_created": len(notifications),
    }


@router.post("/triggers/run-all", response_model=dict)
async def trigger_all_checks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run all notification checks for the current user"""
    from app.services.notification_triggers import NotificationTriggers
    
    service = NotificationTriggers(db)
    results = await service.run_all_daily_checks(current_user.id)
    
    total_notifications = sum(len(v) for v in results.values())
    
    return {
        "message": f"All notification checks completed",
        "results": {
            "low_stock": len(results.get("low_stock", [])),
            "refill": len(results.get("refill", [])),
            "prescription_expiry": len(results.get("prescription_expiry", [])),
            "adherence": len(results.get("adherence", [])),
        },
        "total_notifications_created": total_notifications,
    }


# ========== Admin/System Trigger Endpoints ==========

@router.post("/triggers/admin/run-all-users", response_model=dict)
async def trigger_all_users_checks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run all notification checks for all users (admin only)"""
    # Note: In production, add admin authorization check here
    from app.services.notification_triggers import NotificationTriggers
    
    service = NotificationTriggers(db)
    results = await service.run_all_daily_checks()
    
    total_notifications = sum(len(v) for v in results.values())
    
    return {
        "message": f"All-user notification checks completed",
        "results": {
            "low_stock": len(results.get("low_stock", [])),
            "refill": len(results.get("refill", [])),
            "prescription_expiry": len(results.get("prescription_expiry", [])),
            "adherence": len(results.get("adherence", [])),
        },
        "total_notifications_created": total_notifications,
    }
