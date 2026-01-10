from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from app.schemas.common import NotificationType


class NotificationActionType(str, Enum):
    """Types of actions users can take on notifications"""
    TAKEN = "taken"      # ✓ Tick - User took the medicine
    SKIPPED = "skipped"  # ✗ Cross - User skipped the medicine
    SNOOZED = "snoozed"  # ⏰ Later - User snoozed the notification
    DISMISSED = "dismissed"  # User dismissed the notification
    VIEWED = "viewed"    # User viewed the related item


# Base notification schema
class NotificationBase(BaseModel):
    type: NotificationType
    title: str = Field(..., min_length=1, max_length=255)
    message: Optional[str] = None
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None


# Notification creation schema
class NotificationCreate(NotificationBase):
    user_id: int


# Notification update schema (for marking as read)
class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
    action_taken: Optional[NotificationActionType] = None
    action_time: Optional[datetime] = None


# Notification response schema
class Notification(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    action_taken: Optional[NotificationActionType] = None
    action_time: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Notification with user details
class NotificationWithUser(Notification):
    user: Optional["User"] = None
    
    class Config:
        from_attributes = True


# Notification filter
class NotificationFilter(BaseModel):
    type: Optional[NotificationType] = None
    is_read: Optional[bool] = None
    reference_type: Optional[str] = None
    action_taken: Optional[NotificationActionType] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


# Notification count response
class NotificationCount(BaseModel):
    total: int
    unread: int
    by_type: dict[str, int]


# Bulk notification update
class BulkNotificationUpdate(BaseModel):
    notification_ids: list[int]
    is_read: bool


# Notification action request (for tick/cross actions)
class NotificationActionRequest(BaseModel):
    action: NotificationActionType
    notes: Optional[str] = None


# Notification summary for dashboard
class NotificationSummary(BaseModel):
    total_unread: int
    reminder_notifications: int
    low_stock_notifications: int
    prescription_expiry_notifications: int
    system_notifications: int


# Forward reference for User
from app.schemas.user import User

NotificationWithUser.model_rebuild()
