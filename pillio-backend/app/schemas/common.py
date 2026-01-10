from pydantic import BaseModel, EmailStr
from typing import Optional, List, Generic, TypeVar
from enum import Enum

T = TypeVar('T')


# Authentication schemas
class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# Response schemas
class MessageResponse(BaseModel):
    message: str
    success: bool = True


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int


# Report schemas
class AdherenceReport(BaseModel):
    period: str
    total_scheduled: int
    taken: int
    missed: int
    skipped: int
    adherence_rate: float


class ConsumptionReport(BaseModel):
    medicine_id: int
    medicine_name: str
    period: str
    total_consumed: int
    unit: str


# Dashboard schemas
class DashboardStats(BaseModel):
    total_medicines: int
    today_reminders: int
    completed_today: int
    low_stock_count: int
    adherence_rate: float
    upcoming_reminders: List = []
    low_stock_medicines: List = []


# File upload schemas
class FileUploadResponse(BaseModel):
    filename: str
    file_url: str
    file_size: int
    content_type: str


# Notification types enum
class NotificationType(str, Enum):
    REMINDER = "reminder"
    LOW_STOCK = "low_stock"
    PRESCRIPTION_EXPIRY = "prescription_expiry"
    REFILL = "refill"
    ADHERENCE = "adherence"
    SYSTEM = "system"


# Reminder status enum
class ReminderStatus(str, Enum):
    TAKEN = "taken"
    SKIPPED = "skipped"
    MISSED = "missed"


# Stock change types enum
class StockChangeType(str, Enum):
    ADDED = "added"
    CONSUMED = "consumed"
    ADJUSTED = "adjusted"
    EXPIRED = "expired"


# Frequency types enum
class FrequencyType(str, Enum):
    DAILY = "daily"
    SPECIFIC_DAYS = "specific_days"
    INTERVAL = "interval"

