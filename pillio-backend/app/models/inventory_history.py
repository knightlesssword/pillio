from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class InventoryHistory(BaseModel):
    __tablename__ = "inventory_history"
    
    # Stock change information
    change_amount = Column(Integer, nullable=False)  # Positive for add, negative for consume
    change_type = Column(String(50), nullable=False)  # added, consumed, adjusted, expired
    previous_stock = Column(Integer, nullable=False)
    new_stock = Column(Integer, nullable=False)
    
    # Reference information
    reference_id = Column(Integer, nullable=True)  # Could reference reminder_log or prescription
    notes = Column(Text, nullable=True)
    
    # Foreign keys
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    medicine = relationship("Medicine", back_populates="inventory_history")
    
    def __repr__(self) -> str:
        return f"<InventoryHistory(id={self.id}, medicine_id={self.medicine_id}, change={self.change_amount}, type='{self.change_type}')>"
    
    @property
    def is_increase(self) -> bool:
        """Check if this is a stock increase"""
        return self.change_amount > 0
    
    @property
    def is_decrease(self) -> bool:
        """Check if this is a stock decrease"""
        return self.change_amount < 0