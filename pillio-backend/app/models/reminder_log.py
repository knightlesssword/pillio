from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class ReminderLog(BaseModel):
    __tablename__ = "reminder_logs"
    
    # Reminder tracking
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    taken_time = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), nullable=False)  # taken, skipped, missed
    notes = Column(Text, nullable=True)
    
    # Foreign keys
    reminder_id = Column(Integer, ForeignKey("reminders.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    reminder = relationship("Reminder", back_populates="reminder_logs")
    
    def __repr__(self) -> str:
        return f"<ReminderLog(id={self.id}, reminder_id={self.reminder_id}, status='{self.status}')>"
    
    @property
    def is_taken_on_time(self) -> bool:
        """Check if reminder was taken on time"""
        if self.status != "taken" or not self.taken_time:
            return False
        # Consider it on time if taken within 15 minutes of scheduled time
        time_diff = abs((self.taken_time - self.scheduled_time).total_seconds())
        return time_diff <= 900  # 15 minutes
    
    @property
    def delay_minutes(self) -> int:
        """Get delay in minutes if taken late"""
        if self.status != "taken" or not self.taken_time:
            return 0
        return int((self.taken_time - self.scheduled_time).total_seconds() / 60)