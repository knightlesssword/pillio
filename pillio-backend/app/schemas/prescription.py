from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from app.schemas.common import FileUploadResponse


# Prescription medicine item for creating/updating
class PrescriptionMedicineCreate(BaseModel):
    """Schema for adding a medicine to a prescription"""
    id: Optional[int] = None  # For updates
    medicine_id: Optional[int] = None  # Optional: link to inventory medicine
    medicine_name: str  # Required: medicine name
    dosage: str  # e.g., "500mg", "10ml"
    frequency: str  # e.g., "twice daily", "every 8 hours"
    duration_days: int  # e.g., 7, 14, 30
    instructions: Optional[str] = None  # e.g., "take with food"


# Prescription medicine item in response
class PrescriptionMedicineResponse(BaseModel):
    """Schema for prescription medicine in responses"""
    id: int
    prescription_id: int
    medicine_id: Optional[int] = None
    medicine_name: str
    dosage: str
    frequency: str
    duration_days: int
    instructions: Optional[str] = None
    
    class Config:
        from_attributes = True


# Base prescription schema
class PrescriptionBase(BaseModel):
    doctor_name: str = Field(..., min_length=1, max_length=255)
    hospital_clinic: Optional[str] = None
    prescription_date: date
    valid_until: Optional[date] = None
    notes: Optional[str] = None
    is_active: bool = True


# Prescription creation schema
class PrescriptionCreate(PrescriptionBase):
    """Schema for creating a new prescription with multiple medicines"""
    medicines: List[PrescriptionMedicineCreate] = Field(..., min_length=1, description="At least one medicine is required")
    image: Optional[bytes] = None  # For file upload


# Prescription update schema
class PrescriptionUpdate(BaseModel):
    doctor_name: Optional[str] = None
    hospital_clinic: Optional[str] = None
    prescription_date: Optional[date] = None
    valid_until: Optional[date] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    # For updating medicines, use separate endpoints


# Prescription update with medicines
class PrescriptionUpdateWithMedicines(PrescriptionUpdate):
    """Schema for updating prescription with medicines"""
    medicines: Optional[List[PrescriptionMedicineCreate]] = None


# Prescription response schema (base)
class Prescription(PrescriptionBase):
    id: int
    user_id: int
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Prescription with medicines list
class PrescriptionWithMedicines(Prescription):
    """Full prescription response with all medicines"""
    prescription_medicines: List[PrescriptionMedicineResponse] = []
    is_expired: bool = False
    days_until_expiry: int = 0
    
    class Config:
        from_attributes = True


# Prescription file upload response
class PrescriptionUploadResponse(BaseModel):
    prescription: PrescriptionWithMedicines
    file: FileUploadResponse


# Prescription filter
class PrescriptionFilter(BaseModel):
    is_active: Optional[bool] = None
    is_expired: Optional[bool] = None
    doctor_name: Optional[str] = None
    search: Optional[str] = None  # Search in doctor name or medicine names
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


# Prescription search
class PrescriptionSearch(BaseModel):
    query: str
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
