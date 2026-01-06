from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# Base medicine schema
class MedicineBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    generic_name: Optional[str] = None
    dosage: str = Field(..., min_length=1, max_length=100)
    form: str = Field(..., min_length=1, max_length=50)
    unit: str = Field(..., min_length=1, max_length=50)
    current_stock: int = Field(default=0, ge=0)
    min_stock_alert: int = Field(default=5, ge=0)
    notes: Optional[str] = None


# Medicine creation schema
class MedicineCreate(MedicineBase):
    pass


# Medicine update schema
class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    generic_name: Optional[str] = None
    dosage: Optional[str] = None
    form: Optional[str] = None
    unit: Optional[str] = None
    current_stock: Optional[int] = Field(default=None, ge=0)
    min_stock_alert: Optional[int] = Field(default=None, ge=0)
    notes: Optional[str] = None


# Medicine response schema
class Medicine(MedicineBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Medicine with additional properties
class MedicineWithDetails(Medicine):
    is_low_stock: bool
    stock_level: str
    
    class Config:
        from_attributes = True


# Medicine search/filter schema
class MedicineFilter(BaseModel):
    search: Optional[str] = None
    form: Optional[str] = None
    is_low_stock: Optional[bool] = None
    low_stock_only: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


# Medicine stock adjustment schema
class MedicineStockAdjustment(BaseModel):
    adjustment: int  # Positive for add, negative for remove
    reason: Optional[str] = None
    notes: Optional[str] = None


# Medicine with stock history
class MedicineWithHistory(MedicineWithDetails):
    
    class Config:
        from_attributes = True

