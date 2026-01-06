from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime


# Base user schema
class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None


# User creation schema
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long and contain uppercase, lowercase, number, and special character")


# User update schema
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None


# User login schema
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# User response schema
class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# User with full name property
class UserWithStats(User):
    full_name: str
    total_medicines: int
    active_reminders: int
    low_stock_count: int
    adherence_rate: float


# Password change schema
class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, description="Password must be at least 8 characters long and contain uppercase, lowercase, number, and special character")


# Profile update response
class UserProfileUpdate(BaseModel):
    message: str
    user: User