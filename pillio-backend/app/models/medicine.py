from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Medicine(BaseModel):
    __tablename__ = "medicines"
    
    # Basic medicine information
    name = Column(String(255), nullable=False, index=True)
    generic_name = Column(String(255), nullable=True, index=True)
    dosage = Column(String(100), nullable=False)  # e.g., "100mg", "500mg", "10ml"
    form = Column(String(50), nullable=False)     # tablet, capsule, syrup, injection, etc.
    unit = Column(String(50), nullable=False)     # pills, ml, mg, etc.
    
    # Stock management
    current_stock = Column(Integer, default=0, nullable=False)
    min_stock_alert = Column(Integer, default=5, nullable=False)
    
    # Additional information
    notes = Column(Text, nullable=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="medicines")
    prescriptions = relationship("Prescription", back_populates="medicine")
    reminders = relationship("Reminder", back_populates="medicine")
    inventory_history = relationship("InventoryHistory", back_populates="medicine", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Medicine(id={self.id}, name='{self.name}', stock={self.current_stock})>"
    
    @property
    def is_low_stock(self) -> bool:
        """Check if medicine is low in stock"""
        return self.current_stock <= self.min_stock_alert
    
    @property
    def stock_level(self) -> str:
        """Get stock level status"""
        if self.current_stock <= self.min_stock_alert:
            return "critical"
        elif self.current_stock <= self.min_stock_alert * 2:
            return "low"
        elif self.current_stock <= self.min_stock_alert * 5:
            return "medium"
        else:
            return "good"