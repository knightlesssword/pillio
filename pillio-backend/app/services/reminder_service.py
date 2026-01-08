from typing import Optional, List, Tuple
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime, date, time, timedelta
from app.models.reminder import Reminder
from app.models.reminder_log import ReminderLog
from app.models.medicine import Medicine
from app.schemas.reminder import (
    ReminderCreate, ReminderUpdate, ReminderFilter,
    ReminderStatus, FrequencyType
)


class ReminderService:
    """Service for reminder business logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_reminder(self, user_id: int, reminder_data: ReminderCreate) -> Reminder:
        """Create a new reminder for a user"""
        # Verify medicine exists and belongs to user
        medicine = await self.db.execute(
            select(Medicine).where(
                and_(
                    Medicine.id == reminder_data.medicine_id,
                    Medicine.user_id == user_id
                )
            )
        )
        medicine = medicine.scalar_one_or_none()
        
        if not medicine:
            raise ValueError(f"Medicine with ID {reminder_data.medicine_id} not found")
        
        reminder = Reminder(
            user_id=user_id,
            medicine_id=reminder_data.medicine_id,
            prescription_id=reminder_data.prescription_id,
            reminder_time=reminder_data.reminder_time,
            frequency=reminder_data.frequency.value,
            specific_days=reminder_data.specific_days,
            dosage_amount=reminder_data.dosage_amount,
            dosage_unit=reminder_data.dosage_unit,
            start_date=reminder_data.start_date,
            end_date=reminder_data.end_date,
            is_active=reminder_data.is_active,
            notes=reminder_data.notes,
        )
        
        self.db.add(reminder)
        await self.db.commit()
        await self.db.refresh(reminder)
        
        return reminder
    
    async def get_reminders(
        self, user_id: int, filters: Optional[ReminderFilter] = None
    ) -> Tuple[List[Reminder], int]:
        """Get reminders for a user with optional filtering"""
        query = select(Reminder).where(Reminder.user_id == user_id)
        
        if filters:
            if filters.is_active is not None:
                query = query.where(Reminder.is_active == filters.is_active)
            if filters.medicine_id:
                query = query.where(Reminder.medicine_id == filters.medicine_id)
        
        # Get total count
        count_query = select(Reminder.id).where(Reminder.user_id == user_id)
        if filters:
            if filters.is_active is not None:
                count_query = count_query.where(Reminder.is_active == filters.is_active)
            if filters.medicine_id:
                count_query = count_query.where(Reminder.medicine_id == filters.medicine_id)
        
        total_result = await self.db.execute(count_query)
        total_count = len(total_result.scalars().all())
        
        # Apply pagination
        page = filters.page if filters else 1
        per_page = filters.per_page if filters else 20
        query = query.offset((page - 1) * per_page).limit(per_page)
        
        # Load medicine relationship
        query = query.options(selectinload(Reminder.medicine))
        query = query.order_by(Reminder.reminder_time.asc())
        
        result = await self.db.execute(query)
        reminders = result.scalars().all()
        
        return reminders, total_count
    
    async def get_reminder_by_id(self, reminder_id: int, user_id: int) -> Optional[Reminder]:
        """Get a specific reminder by ID"""
        query = select(Reminder).where(
            and_(
                Reminder.id == reminder_id,
                Reminder.user_id == user_id
            )
        )
        query = query.options(selectinload(Reminder.medicine))
        query = query.options(selectinload(Reminder.reminder_logs))
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_reminder(
        self, reminder_id: int, user_id: int, reminder_update: ReminderUpdate
    ) -> Optional[Reminder]:
        """Update a reminder"""
        reminder = await self.get_reminder_by_id(reminder_id, user_id)
        
        if not reminder:
            return None
        
        update_data = reminder_update.model_dump(exclude_unset=True)
        
        # Handle enum conversion
        if 'frequency' in update_data and update_data['frequency']:
            update_data['frequency'] = update_data['frequency'].value
        
        for field, value in update_data.items():
            setattr(reminder, field, value)
        
        await self.db.commit()
        await self.db.refresh(reminder)
        
        return reminder
    
    async def delete_reminder(self, reminder_id: int, user_id: int) -> bool:
        """Delete a reminder"""
        reminder = await self.get_reminder_by_id(reminder_id, user_id)
        
        if not reminder:
            return False
        
        await self.db.delete(reminder)
        await self.db.commit()
        
        return True
    
    async def get_today_reminders(self, user_id: int) -> List[Reminder]:
        """Get all active reminders for today"""
        today = date.today()
        
        query = select(Reminder).where(
            and_(
                Reminder.user_id == user_id,
                Reminder.is_active == True,
                Reminder.start_date <= today,
                or_(
                    Reminder.end_date.is_(None),
                    Reminder.end_date >= today
                )
            )
        )
        query = query.options(selectinload(Reminder.medicine))
        query = query.order_by(Reminder.reminder_time.asc())
        
        result = await self.db.execute(query)
        reminders = result.scalars().all()
        
        # Filter by specific days for weekly reminders
        today_weekday = today.weekday()
        filtered_reminders = []
        
        for reminder in reminders:
            if reminder.frequency == FrequencyType.DAILY.value:
                filtered_reminders.append(reminder)
            elif reminder.frequency == FrequencyType.SPECIFIC_DAYS.value:
                if reminder.specific_days and today_weekday in reminder.specific_days:
                    filtered_reminders.append(reminder)
            elif reminder.frequency == FrequencyType.INTERVAL.value:
                # Interval frequency - include all for now
                filtered_reminders.append(reminder)
        
        return filtered_reminders
    
    async def get_reminder_status(
        self, reminder_id: int, for_date: Optional[date] = None
    ) -> Tuple[Optional[ReminderLog], ReminderStatus]:
        """Get the current status of a reminder for a specific date"""
        if for_date is None:
            for_date = date.today()
        
        # Get today's log entry directly from reminder_logs table
        # This doesn't require fetching the reminder first
        start_of_day = datetime.combine(for_date, time.min)
        end_of_day = datetime.combine(for_date, time.max)
        
        query = select(ReminderLog).where(
            and_(
                ReminderLog.reminder_id == reminder_id,
                ReminderLog.scheduled_time >= start_of_day,
                ReminderLog.scheduled_time <= end_of_day
            )
        )
        query = query.order_by(ReminderLog.created_at.desc()).limit(1)
        
        result = await self.db.execute(query)
        log = result.scalar_one_or_none()
        
        if log:
            return log, log.status
        
        # No log exists - check if reminder is overdue
        # We need to get the reminder_time from the reminder table
        reminder_query = select(Reminder).where(Reminder.id == reminder_id)
        reminder_result = await self.db.execute(reminder_query)
        reminder = reminder_result.scalar_one_or_none()
        
        if not reminder:
            return None, ReminderStatus.MISSED
        
        now = datetime.now()
        reminder_datetime = datetime.combine(for_date, reminder.reminder_time)
        
        if now > reminder_datetime:
            return None, ReminderStatus.MISSED
        
        return None, ReminderStatus.SKIPPED  # Default status before action
    
    async def mark_reminder_taken(
        self, reminder_id: int, user_id: int, notes: Optional[str] = None
    ) -> ReminderLog:
        """Mark a reminder as taken"""
        reminder = await self.get_reminder_by_id(reminder_id, user_id)
        
        if not reminder:
            raise ValueError(f"Reminder with ID {reminder_id} not found")
        
        today = date.today()
        now = datetime.now()
        
        # Create log entry
        log = ReminderLog(
            reminder_id=reminder_id,
            scheduled_time=datetime.combine(today, reminder.reminder_time),
            taken_time=now,
            status=ReminderStatus.TAKEN.value,
            notes=notes,
        )
        
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        
        return log
    
    async def mark_reminder_skipped(
        self, reminder_id: int, user_id: int, notes: Optional[str] = None
    ) -> ReminderLog:
        """Mark a reminder as skipped"""
        reminder = await self.get_reminder_by_id(reminder_id, user_id)
        
        if not reminder:
            raise ValueError(f"Reminder with ID {reminder_id} not found")
        
        today = date.today()
        
        # Create log entry
        log = ReminderLog(
            reminder_id=reminder_id,
            scheduled_time=datetime.combine(today, reminder.reminder_time),
            taken_time=None,
            status=ReminderStatus.SKIPPED.value,
            notes=notes,
        )
        
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        
        return log
    
    async def get_adherence_stats(
        self, user_id: int, start_date: date, end_date: date
    ) -> dict:
        """Get adherence statistics for a date range"""
        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)
        
        # Get all logs in range
        query = select(ReminderLog).join(Reminder).where(
            and_(
                Reminder.user_id == user_id,
                ReminderLog.scheduled_time >= start_datetime,
                ReminderLog.scheduled_time <= end_datetime
            )
        )
        
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        taken = sum(1 for log in logs if log.status == ReminderStatus.TAKEN.value)
        skipped = sum(1 for log in logs if log.status == ReminderStatus.SKIPPED.value)
        missed = sum(1 for log in logs if log.status == ReminderStatus.MISSED.value)
        total = len(logs)
        
        adherence_rate = (taken / total * 100) if total > 0 else 0
        
        return {
            "total_scheduled": total,
            "taken": taken,
            "skipped": skipped,
            "missed": missed,
            "adherence_rate": round(adherence_rate, 2)
        }
