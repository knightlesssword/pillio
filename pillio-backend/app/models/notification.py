from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel


class Notification(BaseModel):
    __tablename__ = "notifications"
    
    # Notification content
    type = Column(String(50), nullable=False)  # reminder, low_stock, prescription_expiry, refill, system
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False)
    
    # Action tracking (for tick/cross functionality)
    action_taken = Column(String(20), nullable=True)  # taken, skipped, snoozed, dismissed, viewed
    action_time = Column(DateTime, nullable=True)
    
    # Reference information
    reference_id = Column(Integer, nullable=True)
    reference_type = Column(String(50), nullable=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, type='{self.type}', title='{self.title}', is_read={self.is_read})>"
    
    @property
    def is_unread(self) -> bool:
        """Check if notification is unread"""
        return not self.is_read
    
    @property
    def has_action(self) -> bool:
        """Check if notification has been actioned"""
        return self.action_taken is not None
