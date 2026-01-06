from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import time, date as dt, datetime
from app.schemas.common import FrequencyType, ReminderStatus


# Base reminder schema
class ReminderBase(BaseModel):
    reminder_time: time
    frequency: FrequencyType
    specific_days: Optional[List[int]] = None  # [0,1,2,3,4,5,6] for days of week
    dosage_amount: Optional[str] = None
    dosage_unit: Optional[str] = None
    start_date: dt
    end_date: Optional[dt] = None
    is_active: bool = True
    notes: Optional[str] = None


# Reminder creation schema
class ReminderCreate(ReminderBase):
    medicine_id: int
    prescription_id: Optional[int] = None


# Reminder update schema
class ReminderUpdate(BaseModel):
    reminder_time: Optional[time] = None
    frequency: Optional[FrequencyType] = None
    specific_days: Optional[List[int]] = None
    dosage_amount: Optional[str] = None
    dosage_unit: Optional[str] = None
    start_date: Optional[dt] = None
    end_date: Optional[dt] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


# Reminder response schema
class Reminder(ReminderBase):
    id: int
    user_id: int
    medicine_id: int
    prescription_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Reminder with medicine details
class ReminderWithMedicine(Reminder):
    
    class Config:
        from_attributes = True


# Reminder log creation schema
class ReminderLogCreate(BaseModel):
    status: ReminderStatus
    taken_time: Optional[datetime] = None
    notes: Optional[str] = None


# Reminder log response schema
class ReminderLog(BaseModel):
    id: int
    reminder_id: int
    scheduled_time: datetime
    taken_time: Optional[datetime] = None
    status: ReminderStatus
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Reminder with logs
class ReminderWithLogs(ReminderWithMedicine):
    reminder_logs: List[ReminderLog] = []
    
    class Config:
        from_attributes = True


# Today's reminder response
class TodayReminder(ReminderWithMedicine):
    is_due: bool
    is_overdue: bool
    minutes_until_due: Optional[int] = None


# Reminder schedule item
class ReminderSchedule(BaseModel):
    reminder_id: int
    medicine_name: str
    dosage: str
    scheduled_time: datetime
    status: str
    is_due: bool


# Reminder filter
class ReminderFilter(BaseModel):
    is_active: Optional[bool] = None
    medicine_id: Optional[int] = None
    date: Optional[dt] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)

