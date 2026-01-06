from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from app.schemas.common import FileUploadResponse


# Prescription medicine item
class PrescriptionMedicine(BaseModel):
    name: str
    dosage: str
    frequency: str
    duration: str
    instructions: Optional[str] = None


# Base prescription schema
class PrescriptionBase(BaseModel):
    doctor_name: str = Field(..., min_length=1, max_length=255)
    hospital_clinic: Optional[str] = None
    prescription_date: date
    valid_until: Optional[date] = None
    dosage_instructions: Optional[str] = None
    frequency: Optional[str] = None
    duration_days: Optional[int] = None
    notes: Optional[str] = None
    is_active: bool = True


# Prescription creation schema
class PrescriptionCreate(PrescriptionBase):
    medicine_id: Optional[int] = None
    image: Optional[bytes] = None  # For file upload
    medicines: List[PrescriptionMedicine] = []


# Prescription update schema
class PrescriptionUpdate(BaseModel):
    doctor_name: Optional[str] = None
    hospital_clinic: Optional[str] = None
    prescription_date: Optional[date] = None
    valid_until: Optional[date] = None
    dosage_instructions: Optional[str] = None
    frequency: Optional[str] = None
    duration_days: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


# Prescription response schema
class Prescription(PrescriptionBase):
    id: int
    user_id: int
    medicine_id: Optional[int] = None
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Prescription with details
class PrescriptionWithDetails(Prescription):
    is_expired: bool
    days_until_expiry: int
    
    class Config:
        from_attributes = True


# Prescription with medicines list
class PrescriptionWithMedicines(PrescriptionWithDetails):
    medicines: List[PrescriptionMedicine] = []
    
    class Config:
        from_attributes = True


# Prescription file upload response
class PrescriptionUploadResponse(BaseModel):
    prescription: Prescription
    file: FileUploadResponse


# Prescription filter
class PrescriptionFilter(BaseModel):
    is_active: Optional[bool] = None
    is_expired: Optional[bool] = None
    doctor_name: Optional[str] = None
    medicine_id: Optional[int] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


# Prescription search
class PrescriptionSearch(BaseModel):
    query: str
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)

