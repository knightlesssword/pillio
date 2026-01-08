from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class PrescriptionMedicine(BaseModel):
    """
    PrescriptionMedicine model for storing multiple medicines per prescription.
    
    This allows a single prescription to contain multiple medicines,
    each with their own dosage, frequency, duration, and instructions.
    """
    __tablename__ = "prescription_medicines"
    
    # Foreign keys
    prescription_id = Column(Integer, ForeignKey("prescriptions.id", ondelete="CASCADE"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"), nullable=True)
    
    # Medicine details (can be linked to inventory medicine or standalone)
    medicine_name = Column(String(255), nullable=False)
    dosage = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)
    duration_days = Column(Integer, nullable=False)
    instructions = Column(Text, nullable=True)
    
    # Relationships
    prescription = relationship("Prescription", back_populates="prescription_medicines")
    medicine = relationship("Medicine", back_populates="prescription_medicines")
    
    def __repr__(self) -> str:
        return f"<PrescriptionMedicine(id={self.id}, prescription_id={self.prescription_id}, medicine='{self.medicine_name}', dosage='{self.dosage}')>"
