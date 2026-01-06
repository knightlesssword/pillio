from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Notification(BaseModel):
    __tablename__ = "notifications"
    
    # Notification content
    type = Column(String(50), nullable=False)  # reminder, low_stock, prescription_expiry
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False)
    
    # Reference information
    reference_id = Column(Integer, nullable=True)
    reference_type = Column(String(50), nullable=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, type='{self.type}', title='{self.title}', is_read={self.is_read})>"
    
    @property
    def is_unread(self) -> bool:
        """Check if notification is unread"""
        return not self.is_read