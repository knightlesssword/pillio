from sqlalchemy import Column, String, Text, Date, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Prescription(BaseModel):
    __tablename__ = "prescriptions"
    
    # Prescription details
    doctor_name = Column(String(255), nullable=False)
    hospital_clinic = Column(String(255), nullable=True)
    prescription_date = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=True)
    
    # Medication instructions
    dosage_instructions = Column(Text, nullable=True)
    frequency = Column(String(100), nullable=True)
    duration_days = Column(Integer, nullable=True)
    
    # File storage
    image_url = Column(String(500), nullable=True)
    
    # Additional information
    notes = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="prescriptions")
    medicine = relationship("Medicine", back_populates="prescriptions")
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