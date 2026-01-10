from typing import Optional, List, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate, NotificationUpdate, NotificationFilter,
    NotificationCount, BulkNotificationUpdate, NotificationActionRequest
)
from app.schemas.common import NotificationType


class NotificationService:
    """Service for notification business logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_notification(
        self, user_id: int, notification_data: NotificationCreate
    ) -> Notification:
        """Create a new notification for a user"""
        notification = Notification(
            user_id=user_id,
            type=notification_data.type.value if isinstance(notification_data.type, NotificationType) else notification_data.type,
            title=notification_data.title,
            message=notification_data.message,
            reference_id=notification_data.reference_id,
            reference_type=notification_data.reference_type,
            is_read=False,
        )
        
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        
        return notification
    
    async def get_user_notifications(
        self, user_id: int, filters: Optional[NotificationFilter] = None
    ) -> Tuple[List[Notification], int]:
        """Get notifications for a user with optional filtering"""
        query = select(Notification).where(Notification.user_id == user_id)
        
        if filters:
            if filters.type:
                query = query.where(Notification.type == filters.type.value if isinstance(filters.type, NotificationType) else filters.type)
            if filters.is_read is not None:
                query = query.where(Notification.is_read == filters.is_read)
            if filters.reference_type:
                query = query.where(Notification.reference_type == filters.reference_type)
        
        # Get total count
        count_query = select(func.count(Notification.id)).where(Notification.user_id == user_id)
        if filters:
            if filters.type:
                count_query = count_query.where(Notification.type == filters.type.value if isinstance(filters.type, NotificationType) else filters.type)
            if filters.is_read is not None:
                count_query = count_query.where(Notification.is_read == filters.is_read)
            if filters.reference_type:
                count_query = count_query.where(Notification.reference_type == filters.reference_type)
        
        total_result = await self.db.execute(count_query)
        total_count = total_result.scalar() or 0
        
        # Apply pagination
        page = filters.page if filters else 1
        per_page = filters.per_page if filters else 20
        query = query.offset((page - 1) * per_page).limit(per_page)
        
        # Order by created_at descending (newest first)
        query = query.order_by(Notification.created_at.desc())
        
        result = await self.db.execute(query)
        notifications = result.scalars().all()
        
        return list(notifications), total_count
    
    async def get_notification_by_id(
        self, notification_id: int, user_id: int
    ) -> Optional[Notification]:
        """Get a specific notification by ID"""
        query = select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_notification(
        self, notification_id: int, user_id: int, update_data: NotificationUpdate
    ) -> Optional[Notification]:
        """Update a notification"""
        notification = await self.get_notification_by_id(notification_id, user_id)
        
        if not notification:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(notification, field, value)
        
        await self.db.commit()
        await self.db.refresh(notification)
        
        return notification
    
    async def mark_as_read(
        self, notification_id: int, user_id: int
    ) -> Optional[Notification]:
        """Mark a notification as read"""
        notification = await self.get_notification_by_id(notification_id, user_id)
        
        if not notification:
            return None
        
        notification.is_read = True
        await self.db.commit()
        await self.db.refresh(notification)
        
        return notification
    
    async def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications for a user as read"""
        query = select(Notification).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
        
        result = await self.db.execute(query)
        notifications = result.scalars().all()
        
        count = len(notifications)
        for notification in notifications:
            notification.is_read = True
        
        if count > 0:
            await self.db.commit()
        
        return count
    
    async def delete_notification(
        self, notification_id: int, user_id: int
    ) -> bool:
        """Delete a notification"""
        notification = await self.get_notification_by_id(notification_id, user_id)
        
        if not notification:
            return False
        
        await self.db.delete(notification)
        await self.db.commit()
        
        return True
    
    async def clear_all_notifications(self, user_id: int) -> int:
        """Delete all notifications for a user"""
        query = select(Notification.id).where(Notification.user_id == user_id)
        result = await self.db.execute(query)
        notification_ids = result.scalars().all()
        
        count = len(notification_ids)
        
        delete_query = select(Notification).where(Notification.user_id == user_id)
        delete_result = await self.db.execute(delete_query)
        notifications = delete_result.scalars().all()
        
        for notification in notifications:
            await self.db.delete(notification)
        
        if count > 0:
            await self.db.commit()
        
        return count
    
    async def get_notification_counts(
        self, user_id: int
    ) -> NotificationCount:
        """Get notification counts by type and read status"""
        # Total count
        total_query = select(func.count(Notification.id)).where(Notification.user_id == user_id)
        total_result = await self.db.execute(total_query)
        total = total_result.scalar() or 0
        
        # Unread count
        unread_query = select(func.count(Notification.id)).where(
            and_(Notification.user_id == user_id, Notification.is_read == False)
        )
        unread_result = await self.db.execute(unread_query)
        unread = unread_result.scalar() or 0
        
        # Count by type
        reminder_query = select(func.count(Notification.id)).where(
            and_(Notification.user_id == user_id, Notification.type == NotificationType.REMINDER.value)
        )
        reminder_result = await self.db.execute(reminder_query)
        reminder_count = reminder_result.scalar() or 0
        
        low_stock_query = select(func.count(Notification.id)).where(
            and_(Notification.user_id == user_id, Notification.type == NotificationType.LOW_STOCK.value)
        )
        low_stock_result = await self.db.execute(low_stock_query)
        low_stock_count = low_stock_result.scalar() or 0
        
        prescription_query = select(func.count(Notification.id)).where(
            and_(Notification.user_id == user_id, Notification.type == NotificationType.PRESCRIPTION_EXPIRY.value)
        )
        prescription_result = await self.db.execute(prescription_query)
        prescription_count = prescription_result.scalar() or 0
        
        system_query = select(func.count(Notification.id)).where(
            and_(Notification.user_id == user_id, Notification.type == NotificationType.SYSTEM.value)
        )
        system_result = await self.db.execute(system_query)
        system_count = system_result.scalar() or 0
        
        return NotificationCount(
            total=total,
            unread=unread,
            by_type={
                "reminder": reminder_count,
                "low_stock": low_stock_count,
                "prescription_expiry": prescription_count,
                "system": system_count,
            }
        )
    
    async def cleanup_old_notifications(
        self, user_id: int, days_old: int = 30
    ) -> int:
        """Delete notifications older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        query = select(Notification).where(
            and_(
                Notification.user_id == user_id,
                Notification.created_at < cutoff_date
            )
        )
        
        result = await self.db.execute(query)
        notifications = result.scalars().all()
        
        count = len(notifications)
        for notification in notifications:
            await self.db.delete(notification)
        
        if count > 0:
            await self.db.commit()
        
        return count
    
    async def bulk_update(
        self, user_id: int, update_data: BulkNotificationUpdate
    ) -> int:
        """Bulk update notifications (mark as read/unread)"""
        query = select(Notification).where(
            and_(
                Notification.id.in_(update_data.notification_ids),
                Notification.user_id == user_id
            )
        )
        
        result = await self.db.execute(query)
        notifications = result.scalars().all()
        
        count = len(notifications)
        for notification in notifications:
            notification.is_read = update_data.is_read
        
        if count > 0:
            await self.db.commit()
        
        return count
    
    async def take_action(
        self,
        notification_id: int,
        user_id: int,
        action_request: NotificationActionRequest
    ) -> Optional[Notification]:
        """Take an action on a notification (taken, skipped, snoozed, dismissed)"""
        notification = await self.get_notification_by_id(notification_id, user_id)
        
        if not notification:
            return None
        
        # Update the notification with action
        notification.action_taken = action_request.action.value if hasattr(action_request.action, 'value') else action_request.action
        notification.action_time = datetime.utcnow()
        notification.is_read = True
        
        await self.db.commit()
        await self.db.refresh(notification)
        
        return notification
    
    async def mark_taken(
        self, notification_id: int, user_id: int
    ) -> Optional[Notification]:
        """Mark a notification as taken (✓ action)"""
        notification = await self.get_notification_by_id(notification_id, user_id)
        
        if not notification:
            return None
        
        notification.action_taken = "taken"
        notification.action_time = datetime.utcnow()
        notification.is_read = True
        
        await self.db.commit()
        await self.db.refresh(notification)
        
        return notification
    
    async def mark_skipped(
        self, notification_id: int, user_id: int
    ) -> Optional[Notification]:
        """Mark a notification as skipped (✗ action)"""
        notification = await self.get_notification_by_id(notification_id, user_id)
        
        if not notification:
            return None
        
        notification.action_taken = "skipped"
        notification.action_time = datetime.utcnow()
        notification.is_read = True
        
        await self.db.commit()
        await self.db.refresh(notification)
        
        return notification
    
    # ========== Notification Creation Helpers ==========
    
    async def create_reminder_notification(
        self,
        user_id: int,
        medicine_name: str,
        dosage: str,
        reminder_id: Optional[int] = None
    ) -> Notification:
        """Create a time-to-take-medicine notification"""
        notification_data = NotificationCreate(
            user_id=user_id,
            type=NotificationType.REMINDER,
            title="💊 Time to take your medicine",
            message=f"{medicine_name} - {dosage}",
            reference_id=reminder_id,
            reference_type="reminder",
        )
        return await self.create_notification(user_id, notification_data)
    
    async def create_low_stock_notification(
        self,
        user_id: int,
        medicine_name: str,
        remaining_quantity: int,
        medicine_id: Optional[int] = None
    ) -> Notification:
        """Create a low stock alert notification"""
        notification_data = NotificationCreate(
            user_id=user_id,
            type=NotificationType.LOW_STOCK,
            title="Low stock alert",
            message=f"{medicine_name} is running low ({remaining_quantity} tablets left)",
            reference_id=medicine_id,
            reference_type="medicine",
        )
        return await self.create_notification(user_id, notification_data)
    
    async def create_prescription_expiry_notification(
        self,
        user_id: int,
        doctor_name: str,
        days_until_expiry: int,
        prescription_id: Optional[int] = None
    ) -> Notification:
        """Create a prescription expiry notification"""
        notification_data = NotificationCreate(
            user_id=user_id,
            type=NotificationType.PRESCRIPTION_EXPIRY,
            title="Prescription expiring soon",
            message=f"Your prescription from {doctor_name} expires in {days_until_expiry} days",
            reference_id=prescription_id,
            reference_type="prescription",
        )
        return await self.create_notification(user_id, notification_data)
    
    async def create_refill_notification(
        self,
        user_id: int,
        medicine_name: str,
        days_until_empty: int,
        medicine_id: Optional[int] = None
    ) -> Notification:
        """Create a refill suggestion notification"""
        notification_data = NotificationCreate(
            user_id=user_id,
            type=NotificationType.REFILL,
            title="Time to refill",
            message=f"{medicine_name} will run out in approximately {days_until_empty} days",
            reference_id=medicine_id,
            reference_type="medicine",
        )
        return await self.create_notification(user_id, notification_data)
