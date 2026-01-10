"""
Notification Triggers Service

Orchestrates automatic notification creation for:
- Low stock alerts
- Prescription expiry
- Adherence patterns (streaks, drops)
- Refill suggestions
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import date, timedelta
from sqlalchemy import and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.medicine import Medicine
from app.models.prescription import Prescription
from app.models.notification import Notification
from app.services.notification_service import NotificationService
from app.services.medicine_service import MedicineService
from app.services.prescription_service import PrescriptionService
from app.services.reminder_service import ReminderService

logger = logging.getLogger(__name__)


class NotificationTriggers:
    """Service for triggering automatic notifications"""
    
    # Adherence streak milestones to celebrate
    STREAK_MILESTONES = [3, 7, 14, 30, 60, 90, 180, 365]
    
    # Days before expiry to send prescription notification
    PRESCRIPTION_EXPIRY_DAYS = [30, 14, 7, 3, 1]
    
    # Refill warning thresholds (days until empty)
    REFILL_WARNING_DAYS = [14, 7, 3, 1]
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.notification_service = NotificationService(db)
        self.medicine_service = MedicineService(db)
        self.prescription_service = PrescriptionService(db)
        self.reminder_service = ReminderService(db)
    
    # ========== Low Stock Notifications ==========
    
    async def check_and_notify_low_stock(
        self,
        user_id: int,
        medicine_id: Optional[int] = None
    ) -> List[Notification]:
        """
        Check medicine stock levels and create low stock notifications.
        
        Args:
            user_id: User ID
            medicine_id: Optional specific medicine to check.
                        If None, checks all medicines for user.
        
        Returns:
            List of created notifications
        """
        notifications = []
        
        try:
            if medicine_id:
                # Check specific medicine
                medicine = await self.medicine_service.get_medicine_by_id(medicine_id, user_id)
                if medicine and medicine.current_stock <= medicine.min_stock_alert:
                    # Create notification
                    notification = await self.notification_service.create_low_stock_notification(
                        user_id=user_id,
                        medicine_name=medicine.name,
                        remaining_quantity=medicine.current_stock,
                        medicine_id=medicine.id
                    )
                    notifications.append(notification)
                    logger.info(f"Low stock notification created for medicine {medicine.name}")
            else:
                # Check all low stock medicines
                low_stock_medicines = await self.medicine_service.get_low_stock_medicines(user_id)
                
                for medicine in low_stock_medicines:
                    # Only notify if not already notified recently (within 24 hours)
                    already_notified = await self._was_notified_recently(
                        user_id, "low_stock", medicine.id
                    )
                    
                    if not already_notified:
                        notification = await self.notification_service.create_low_stock_notification(
                            user_id=user_id,
                            medicine_name=medicine.name,
                            remaining_quantity=medicine.current_stock,
                            medicine_id=medicine.id
                        )
                        notifications.append(notification)
                
                logger.info(f"Created {len(notifications)} low stock notifications for user {user_id}")
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error checking low stock for user {user_id}: {e}", exc_info=True)
            return notifications
    
    async def check_and_notify_refill(
        self,
        user_id: int,
        medicine_id: Optional[int] = None
    ) -> List[Notification]:
        """
        Calculate refill needs and create refill notifications.
        
        Args:
            user_id: User ID
            medicine_id: Optional specific medicine to check.
        
        Returns:
            List of created notifications
        """
        notifications = []
        
        try:
            if medicine_id:
                medicine = await self.medicine_service.get_medicine_by_id(medicine_id, user_id)
                if medicine:
                    days_until_empty = await self._calculate_days_until_empty(user_id, medicine.id)
                    if days_until_empty is not None and days_until_empty <= min(self.REFILL_WARNING_DAYS):
                        already_notified = await self._was_notified_recently(
                            user_id, "refill", medicine.id, hours=48
                        )
                        if not already_notified:
                            notification = await self.notification_service.create_refill_notification(
                                user_id=user_id,
                                medicine_name=medicine.name,
                                days_until_empty=days_until_empty,
                                medicine_id=medicine.id
                            )
                            notifications.append(notification)
            else:
                # Check all medicines for refill needs
                medicines, _ = await self.medicine_service.get_medicines(user_id)
                
                for medicine in medicines:
                    days_until_empty = await self._calculate_days_until_empty(user_id, medicine.id)
                    
                    if days_until_empty is not None and days_until_empty <= min(self.REFILL_WARNING_DAYS):
                        already_notified = await self._was_notified_recently(
                            user_id, "refill", medicine.id, hours=48
                        )
                        if not already_notified:
                            notification = await self.notification_service.create_refill_notification(
                                user_id=user_id,
                                medicine_name=medicine.name,
                                days_until_empty=days_until_empty,
                                medicine_id=medicine.id
                            )
                            notifications.append(notification)
            
            logger.info(f"Created {len(notifications)} refill notifications for user {user_id}")
            return notifications
            
        except Exception as e:
            logger.error(f"Error checking refill needs for user {user_id}: {e}", exc_info=True)
            return notifications
    
    async def _calculate_days_until_empty(self, user_id: int, medicine_id: int) -> Optional[int]:
        """Calculate estimated days until medicine runs out based on consumption."""
        try:
            # Get last 30 days of consumption
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            
            from app.models.reminder import Reminder
            from app.models.reminder_log import ReminderLog
            
            # Calculate total consumed in last 30 days
            query = select(ReminderLog).join(Reminder).where(
                and_(
                    Reminder.user_id == user_id,
                    Reminder.medicine_id == medicine_id,
                    ReminderLog.status == 'taken',
                    ReminderLog.scheduled_time >= start_date,
                    ReminderLog.scheduled_time <= end_date
                )
            )
            
            result = await self.db.execute(query)
            logs = result.scalars().all()
            
            total_consumed = len(logs)  # Assuming 1 log = 1 dosage unit
            if total_consumed == 0:
                return None  # Can't calculate without consumption data
            
            # Calculate daily average
            daily_avg = total_consumed / 30
            
            if daily_avg <= 0:
                return None
            
            # Get current stock
            medicine = await self.medicine_service.get_medicine_by_id(medicine_id, user_id)
            if not medicine:
                return None
            
            days_until_empty = int(medicine.current_stock / daily_avg)
            return days_until_empty
            
        except Exception as e:
            logger.error(f"Error calculating days until empty for medicine {medicine_id}: {e}")
            return None
    
    # ========== Prescription Expiry Notifications ==========
    
    async def check_and_notify_prescription_expiry(
        self,
        user_id: int,
        days_ahead: int = 30
    ) -> List[Notification]:
        """
        Check for expiring prescriptions and create notifications.
        
        Args:
            user_id: User ID
            days_ahead: Days to look ahead for expiring prescriptions
        
        Returns:
            List of created notifications
        """
        notifications = []
        
        try:
            expiring_prescriptions = await self.prescription_service.get_expiring_prescriptions(
                user_id, days_ahead
            )
            
            for prescription in expiring_prescriptions:
                days_until_expiry = (prescription.valid_until - date.today()).days
                
                # Only notify if within our configured days and not recently notified
                if days_until_expiry in self.PRESCRIPTION_EXPIRY_DAYS:
                    already_notified = await self._was_notified_recently(
                        user_id, "prescription_expiry", prescription.id, hours=24
                    )
                    
                    if not already_notified:
                        notification = await self.notification_service.create_prescription_expiry_notification(
                            user_id=user_id,
                            doctor_name=prescription.doctor_name,
                            days_until_expiry=days_until_expiry,
                            prescription_id=prescription.id
                        )
                        notifications.append(notification)
            
            logger.info(f"Created {len(notifications)} prescription expiry notifications for user {user_id}")
            return notifications
            
        except Exception as e:
            logger.error(f"Error checking prescription expiry for user {user_id}: {e}", exc_info=True)
            return notifications
    
    # ========== Adherence Notifications ==========
    
    async def check_adherence_patterns(
        self,
        user_id: int
    ) -> List[Notification]:
        """
        Check adherence patterns and create streak/drop notifications.
        
        Args:
            user_id: User ID
        
        Returns:
            List of created notifications
        """
        notifications = []
        
        try:
            # Get current streak
            streak_data = await self.reminder_service.get_adherence_streak(user_id)
            current_streak = streak_data.get("current_streak", 0)
            longest_streak = streak_data.get("longest_streak", 0)
            
            # Check for new streak milestone
            for milestone in self.STREAK_MILESTONES:
                if current_streak >= milestone and longest_streak < milestone:
                    # New milestone reached!
                    notification = await self._create_adherence_streak_notification(
                        user_id, current_streak
                    )
                    if notification:
                        notifications.append(notification)
                    break  # Only notify for the highest newly reached milestone
            
            # Check for adherence drop
            drop_notification = await self._check_adherence_drop(user_id)
            if drop_notification:
                notifications.append(drop_notification)
            
            logger.info(f"Created {len(notifications)} adherence notifications for user {user_id}")
            return notifications
            
        except Exception as e:
            logger.error(f"Error checking adherence patterns for user {user_id}: {e}", exc_info=True)
            return notifications
    
    async def _create_adherence_streak_notification(
        self,
        user_id: int,
        streak_days: int
    ) -> Optional[Notification]:
        """Create notification for reaching a streak milestone."""
        try:
            # Check if we already sent this notification
            already_notified = await self._was_notified_recently(
                user_id, "adherence_streak", None, hours=24
            )
            
            if already_notified:
                return None
            
            messages = {
                3: "Great start! You've taken all medicines for 3 days in a row! 💪",
                7: "One week strong! Keep up the excellent work! 🎉",
                14: "Two weeks of perfect adherence! You're doing amazing! 🌟",
                30: "A full month of taking your medicines on time! Incredible! 🏆",
                60: "Two months of consistent adherence! You're a health champion! 👑",
                90: "Three months - 90 days of medication discipline! Outstanding! 🌈",
                180: "Six months of perfect adherence! This is amazing commitment! 🎯",
                365: "A full year of taking your medicines as prescribed! You're inspirational! 🎊"
            }
            
            title = "🔥 Adherence Streak!"
            message = messages.get(streak_days, f"Amazing! {streak_days} days of perfect adherence!")
            
            from app.schemas.notification import NotificationCreate
            from app.schemas.common import NotificationType
            
            notification_data = NotificationCreate(
                user_id=user_id,
                type=NotificationType.ADHERENCE,
                title=title,
                message=message,
                reference_type="adherence",
                reference_id=None,
            )
            
            return await self.notification_service.create_notification(user_id, notification_data)
            
        except Exception as e:
            logger.error(f"Error creating streak notification: {e}")
            return None
    
    async def _check_adherence_drop(self, user_id: int) -> Optional[Notification]:
        """Check for significant adherence drop and notify."""
        try:
            # Get last 7 days adherence
            daily_adherence = await self.reminder_service.get_daily_adherence(user_id, 7)
            
            if len(daily_adherence) < 2:
                return None
            
            # Compare this week to last week (if we have enough data)
            this_week = daily_adherence[-3:]  # Last 3 days
            last_week = daily_adherence[-7:-3]  # Previous 4 days
            
            if not this_week or not last_week:
                return None
            
            this_week_avg = sum(d["adherence_rate"] for d in this_week) / len(this_week)
            last_week_avg = sum(d["adherence_rate"] for d in last_week) / len(last_week)
            
            # If drop is more than 20%, send notification
            if this_week_avg < last_week_avg - 20:
                # Check if we already notified recently
                already_notified = await self._was_notified_recently(
                    user_id, "adherence_drop", None, hours=24
                )
                
                if already_notified:
                    return None
                
                from app.schemas.notification import NotificationCreate
                from app.schemas.common import NotificationType
                
                notification_data = NotificationCreate(
                    user_id=user_id,
                    type=NotificationType.ADHERENCE,
                    title="📉 Adherence Drop Alert",
                    message=f"Your medication adherence has dropped to {this_week_avg:.0f}%. Let's get back on track!",
                    reference_type="adherence",
                    reference_id=None,
                )
                
                return await self.notification_service.create_notification(user_id, notification_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking adherence drop: {e}")
            return None
    
    # ========== Bulk Operations ==========
    
    async def run_all_daily_checks(
        self,
        user_id: Optional[int] = None
    ) -> Dict[str, List[Notification]]:
        """
        Run all daily notification checks.
        
        Args:
            user_id: Optional specific user to check.
                    If None, checks all users.
        
        Returns:
            Dictionary with notification counts by type
        """
        results = {
            "low_stock": [],
            "refill": [],
            "prescription_expiry": [],
            "adherence": []
        }
        
        try:
            if user_id:
                # Check specific user
                results["low_stock"] = await self.check_and_notify_low_stock(user_id)
                results["refill"] = await self.check_and_notify_refill(user_id)
                results["prescription_expiry"] = await self.check_and_notify_prescription_expiry(user_id)
                results["adherence"] = await self.check_adherence_patterns(user_id)
            else:
                # Get all active users
                result = await self.db.execute(
                    select(User).where(User.is_active == True)
                )
                users = result.scalars().all()
                
                for user in users:
                    results["low_stock"].extend(
                        await self.check_and_notify_low_stock(user.id)
                    )
                    results["refill"].extend(
                        await self.check_and_notify_refill(user.id)
                    )
                    results["prescription_expiry"].extend(
                        await self.check_and_notify_prescription_expiry(user.id)
                    )
                    results["adherence"].extend(
                        await self.check_adherence_patterns(user.id)
                    )
            
            total = sum(len(v) for v in results.values())
            logger.info(f"Daily checks completed: {total} notifications created")
            
            return results
            
        except Exception as e:
            logger.error(f"Error running daily checks: {e}", exc_info=True)
            return results
    
    async def check_adherence_patterns_all_users(
        self,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Run adherence checks for all users (for weekly job)."""
        try:
            if user_id:
                adherence_notifications = await self.check_adherence_patterns(user_id)
                return {"user_id": user_id, "notifications": len(adherence_notifications)}
            
            result = await self.db.execute(
                select(User).where(User.is_active == True)
            )
            users = result.scalars().all()
            
            total_notifications = 0
            for user in users:
                notifications = await self.check_adherence_patterns(user.id)
                total_notifications += len(notifications)
            
            return {"users_checked": len(users), "notifications": total_notifications}
            
        except Exception as e:
            logger.error(f"Error in weekly adherence check: {e}", exc_info=True)
            return {"error": str(e)}
    
    # ========== Helper Methods ==========
    
    async def _was_notified_recently(
        self,
        user_id: int,
        notification_type: str,
        reference_id: Optional[int],
        hours: int = 24
    ) -> bool:
        """Check if user was already notified about this recently."""
        from datetime import datetime, timedelta
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        query = select(Notification).where(
            and_(
                Notification.user_id == user_id,
                Notification.type == notification_type,
                Notification.created_at >= cutoff
            )
        )
        
        if reference_id:
            query = query.where(Notification.reference_id == reference_id)
        
        result = await self.db.execute(query)
        notification = result.scalar_one_or_none()
        
        return notification is not None
