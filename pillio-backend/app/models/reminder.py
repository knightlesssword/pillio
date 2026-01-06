from sqlalchemy import Column, String, Time, Date, Boolean, Text, Integer, ARRAY, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Reminder(BaseModel):
    __tablename__ = "reminders"
    
    # Reminder scheduling
    reminder_time = Column(Time, nullable=False)
    frequency = Column(String(50), nullable=False)  # daily, weekly, custom
    specific_days = Column(ARRAY(Integer), nullable=True)  # [0,1,2,3,4,5,6] for days of week
    
    # Dosage information
    dosage_amount = Column(String(20), nullable=True)  # e.g., "1", "2", "0.5"
    dosage_unit = Column(String(50), nullable=True)    # tablet, capsule, ml, etc.
    
    # Date range
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    
    # Status and notes
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="reminders")
    medicine = relationship("Medicine", back_populates="reminders")
    prescription = relationship("Prescription", back_populates="reminders")
    reminder_logs = relationship("ReminderLog", back_populates="reminder", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Reminder(id={self.id}, medicine='{self.medicine.name}', time='{self.reminder_time}')>"
    
    @property
    def is_expired(self) -> bool:
        """Check if reminder is expired"""
        if not self.end_date:
            return False
        from datetime import date
        return self.end_date < date.today()
    
    @property
    def next_occurrence(self) -> str:
        """Get next occurrence date/time description"""
        from datetime import datetime, date, time
        today = date.today()
        
        if self.end_date and today > self.end_date:
            return "Expired"
        
        # Calculate next occurrence based on frequency
        now = datetime.now()
        next_time = datetime.combine(today, self.reminder_time)
        
        if next_time <= now:
            if self.frequency == "daily":
                next_time = datetime.combine(today, self.reminder_time)
                if next_time <= now:
                    next_time = next_time.replace(day=today.day + 1)
            elif self.frequency == "weekly" and self.specific_days:
                days_ahead = 0
                current_day = today.weekday()
                for day in sorted(self.specific_days):
                    if day > current_day:
                        days_ahead = day - current_day
                        break
                else:
                    days_ahead = 7 - current_day + self.specific_days[0]
                next_time = datetime.combine(today, self.reminder_time)
                next_time = next_time.replace(day=today.day + days_ahead)
        
        return next_time.strftime("%Y-%m-%d %H:%M")