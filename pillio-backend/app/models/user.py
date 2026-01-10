from sqlalchemy import Column, String, Boolean, Date
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"
    
    # Authentication fields
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Profile fields
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    
    # Status fields
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Soft delete fields
    is_deleted = Column(Boolean, default=False, nullable=False)
    deletion_reason = Column(String(500), nullable=True)
    
    # Relationships
    medicines = relationship("Medicine", back_populates="user", cascade="all, delete-orphan")
    prescriptions = relationship("Prescription", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.email.split('@')[0]
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', name='{self.full_name}')>"