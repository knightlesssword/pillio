"""Export service for user data export functionality."""
from datetime import datetime
from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import logging

from app.models.user import User
from app.models.medicine import Medicine
from app.models.prescription import Prescription
from app.models.prescription_medicine import PrescriptionMedicine
from app.models.reminder import Reminder
from app.models.reminder_log import ReminderLog
from app.models.notification import Notification
from app.models.inventory_history import InventoryHistory

logger = logging.getLogger(__name__)


class ExportService:
    """Service to export all user data in JSON format"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def export_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        Export all data for a user as a structured dictionary.
        
        Args:
            user_id: The ID of the user to export data for
            
        Returns:
            Dictionary containing all user data in export format
        """
        # Get user with all relationships
        user = await self._get_user_with_data(user_id)
        
        if not user:
            raise ValueError(f"User with ID {user_id} not found")

        # Build export data structure
        export_data = {
            "export_metadata": self._get_export_metadata(user),
            "user": self._serialize_user(user),
            "medicines": self._serialize_medicines(user.medicines),
            "prescriptions": self._serialize_prescriptions(user.prescriptions),
            "reminders": self._serialize_reminders(user.reminders),
            "reminder_logs": await self._serialize_reminder_logs(user_id),
            "notifications": self._serialize_notifications(user.notifications),
            "inventory_history": self._serialize_inventory_history(user.medicines),
        }

        return export_data

    def _get_export_metadata(self, user: User) -> Dict[str, Any]:
        """Generate export metadata"""
        return {
            "export_date": datetime.utcnow().isoformat() + "Z",
            "app_name": "Pillio Health Hub",
            "app_version": "1.0.0",
            "user_email": user.email,
            "export_format_version": "1.0"
        }

    def _serialize_user(self, user: User) -> Dict[str, Any]:
        """Serialize user data (excluding sensitive fields)"""
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "date_of_birth": user.date_of_birth.isoformat() if user.date_of_birth else None,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }

    def _serialize_medicines(self, medicines: list) -> list:
        """Serialize medicine list"""
        return [
            {
                "id": med.id,
                "name": med.name,
                "generic_name": med.generic_name,
                "dosage": med.dosage,
                "form": med.form,
                "unit": med.unit,
                "current_stock": med.current_stock,
                "min_stock_alert": med.min_stock_alert,
                "notes": med.notes,
                "created_at": med.created_at.isoformat() if med.created_at else None,
                "updated_at": med.updated_at.isoformat() if med.updated_at else None
            }
            for med in medicines
        ]

    def _serialize_prescriptions(self, prescriptions: list) -> list:
        """Serialize prescription list with prescription medicines"""
        result = []
        for pres in prescriptions:
            pres_data = {
                "id": pres.id,
                "doctor_name": pres.doctor_name,
                "hospital_clinic": pres.hospital_clinic,
                "prescription_date": pres.prescription_date.isoformat() if pres.prescription_date else None,
                "valid_until": pres.valid_until.isoformat() if pres.valid_until else None,
                "notes": pres.notes,
                "image_url": pres.image_url,
                "is_active": pres.is_active,
                "created_at": pres.created_at.isoformat() if pres.created_at else None,
                "updated_at": pres.updated_at.isoformat() if pres.updated_at else None,
                "medicines": [
                    {
                        "id": pm.id,
                        "medicine_name": pm.medicine_name,
                        "dosage": pm.dosage,
                        "frequency": pm.frequency,
                        "duration_days": pm.duration_days,
                        "instructions": pm.instructions
                    }
                    for pm in pres.prescription_medicines
                ]
            }
            result.append(pres_data)
        return result

    def _serialize_reminders(self, reminders: list) -> list:
        """Serialize reminder list"""
        return [
            {
                "id": rem.id,
                "medicine_id": rem.medicine_id,
                "prescription_id": rem.prescription_id,
                "reminder_time": rem.reminder_time.isoformat() if rem.reminder_time else None,
                "frequency": rem.frequency,
                "specific_days": rem.specific_days,
                "interval_days": rem.interval_days,
                "dosage_amount": rem.dosage_amount,
                "dosage_unit": rem.dosage_unit,
                "start_date": rem.start_date.isoformat() if rem.start_date else None,
                "end_date": rem.end_date.isoformat() if rem.end_date else None,
                "is_active": rem.is_active,
                "notes": rem.notes,
                "created_at": rem.created_at.isoformat() if rem.created_at else None,
                "updated_at": rem.updated_at.isoformat() if rem.updated_at else None,
                "medicine": {
                    "id": rem.medicine.id,
                    "name": rem.medicine.name,
                    "dosage": rem.medicine.dosage
                } if rem.medicine else None
            }
            for rem in reminders
        ]

    async def _serialize_reminder_logs(self, user_id: int) -> list:
        """Serialize reminder logs for the user"""
        # Get all reminders for the user first
        reminders_stmt = select(Reminder).where(Reminder.user_id == user_id)
        reminders_result = await self.db.execute(reminders_stmt)
        reminders = reminders_result.scalars().all()
        
        reminder_ids = [rem.id for rem in reminders]
        
        if not reminder_ids:
            return []

        # Get all logs for these reminders
        logs_stmt = select(ReminderLog).where(ReminderLog.reminder_id.in_(reminder_ids))
        logs_result = await self.db.execute(logs_stmt)
        logs = logs_result.scalars().all()
        
        return [
            {
                "id": log.id,
                "reminder_id": log.reminder_id,
                "scheduled_time": log.scheduled_time.isoformat() if log.scheduled_time else None,
                "taken_time": log.taken_time.isoformat() if log.taken_time else None,
                "status": log.status,
                "notes": log.notes,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            for log in logs
        ]

    def _serialize_notifications(self, notifications: list) -> list:
        """Serialize notification list"""
        return [
            {
                "id": notif.id,
                "type": notif.type,
                "title": notif.title,
                "message": notif.message,
                "is_read": notif.is_read,
                "reference_id": notif.reference_id,
                "reference_type": notif.reference_type,
                "created_at": notif.created_at.isoformat() if notif.created_at else None
            }
            for notif in notifications
        ]

    def _serialize_inventory_history(self, medicines: list) -> list:
        """Serialize inventory history for all user medicines"""
        all_history = []
        for med in medicines:
            for history in med.inventory_history:
                all_history.append({
                    "id": history.id,
                    "medicine_id": history.medicine_id,
                    "change_amount": history.change_amount,
                    "change_type": history.change_type,
                    "previous_stock": history.previous_stock,
                    "new_stock": history.new_stock,
                    "reference_id": history.reference_id,
                    "notes": history.notes,
                    "created_at": history.created_at.isoformat() if history.created_at else None
                })
        return all_history

    async def _get_user_with_data(self, user_id: int) -> User:
        """Get user with all related data loaded"""
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.medicines).selectinload(Medicine.inventory_history),
                selectinload(User.prescriptions).selectinload(Prescription.prescription_medicines),
                selectinload(User.reminders).selectinload(Reminder.medicine),
                selectinload(User.notifications)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
