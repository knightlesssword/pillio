from app.schemas.user import User, UserCreate, UserUpdate, UserLogin
from app.schemas.medicine import Medicine, MedicineCreate, MedicineUpdate
from app.schemas.prescription import (
    Prescription, PrescriptionCreate, PrescriptionUpdate, PrescriptionWithMedicines,
    PrescriptionMedicineCreate, PrescriptionMedicineResponse, PrescriptionFilter,
    PrescriptionUpdateWithMedicines
)
from app.schemas.reminder import Reminder, ReminderCreate, ReminderUpdate, ReminderLogCreate
from app.schemas.inventory_history import InventoryHistory, InventoryHistoryCreate
from app.schemas.notification import Notification, NotificationUpdate
from app.schemas.common import (
    Token, TokenData, PasswordReset, PasswordResetConfirm,
    MessageResponse, PaginatedResponse, DashboardStats, 
    AdherenceReport, ConsumptionReport
)

__all__ = [
    # User schemas
    "User", "UserCreate", "UserUpdate", "UserLogin",
    
    # Medicine schemas
    "Medicine", "MedicineCreate", "MedicineUpdate",
    
    # Prescription schemas
    "Prescription", "PrescriptionCreate", "PrescriptionUpdate", "PrescriptionWithMedicines",
    "PrescriptionMedicineCreate", "PrescriptionMedicineResponse", "PrescriptionFilter",
    "PrescriptionUpdateWithMedicines",
    
    # Reminder schemas
    "Reminder", "ReminderCreate", "ReminderUpdate", "ReminderLogCreate",
    
    # Inventory schemas
    "InventoryHistory", "InventoryHistoryCreate",
    
    # Notification schemas
    "Notification", "NotificationUpdate",
    
    # Common schemas
    "Token", "TokenData", "PasswordReset", "PasswordResetConfirm",
    "MessageResponse", "PaginatedResponse", "DashboardStats",
    "AdherenceReport", "ConsumptionReport"
]
