from sqlalchemy import Column, String, Text, Date, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Prescription(BaseModel):
    """
    Prescription model representing a doctor's prescription.
    
    A prescription can contain multiple medicines, each with their own
    dosage, frequency, and duration. The medicines are stored in the
    PrescriptionMedicine table for many-to-many relationship.
    """
    __tablename__ = "prescriptions"
    
    # Prescription details
    doctor_name = Column(String(255), nullable=False)
    hospital_clinic = Column(String(255), nullable=True)
    prescription_date = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=True)
    
    # Additional information
    notes = Column(Text, nullable=True)
    
    # File storage
    image_url = Column(String(500), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="prescriptions")
    prescription_medicines = relationship("PrescriptionMedicine", back_populates="prescription", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="prescription")
    
    def __repr__(self) -> str:
        return f"<Prescription(id={self.id}, doctor='{self.doctor_name}', date='{self.prescription_date}')>"
    
    @property
    def is_expired(self) -> bool:
        """Check if prescription is expired"""
        if not self.valid_until:
            return False
        from datetime import date
        return self.valid_until < date.today()
    
    @property
    def days_until_expiry(self) -> int:
        """Get days until prescription expires"""
        if not self.valid_until:
            return -1
        from datetime import date
        return (self.valid_until - date.today()).days