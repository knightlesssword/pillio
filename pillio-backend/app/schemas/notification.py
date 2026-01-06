from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.common import NotificationType


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


# Notification response schema
class Notification(NotificationBase):
    id: int
    user_id: int
    is_read: bool
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