from typing import List, Optional, Tuple
from datetime import datetime
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from app.models.prescription import Prescription
from app.models.prescription_medicine import PrescriptionMedicine
from app.schemas.prescription import (
    PrescriptionCreate, PrescriptionUpdate, PrescriptionFilter,
    PrescriptionMedicineCreate
)
from app.core.exceptions import PrescriptionNotFoundException

logger = logging.getLogger(__name__)


class PrescriptionService:
    """Service for handling prescription-related operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_prescription(
        self,
        user_id: int,
        prescription_data: PrescriptionCreate
    ) -> Prescription:
        """
        Create a new prescription with multiple medicines
        
        Args:
            user_id: User ID
            prescription_data: Prescription creation data with medicines list
            
        Returns:
            Created prescription object with medicines
            
        Raises:
            Exception: If database error occurs
        """
        logger.info(f"Creating prescription for user ID: {user_id}, doctor: {prescription_data.doctor_name}")
        
        try:
            # Create the prescription
            prescription = Prescription(
                user_id=user_id,
                doctor_name=prescription_data.doctor_name,
                hospital_clinic=prescription_data.hospital_clinic,
                prescription_date=prescription_data.prescription_date,
                valid_until=prescription_data.valid_until,
                notes=prescription_data.notes,
                is_active=prescription_data.is_active,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.db.add(prescription)
            await self.db.flush()  # Get the prescription ID
            
            # Create prescription medicines
            for medicine_data in prescription_data.medicines:
                prescription_medicine = PrescriptionMedicine(
                    prescription_id=prescription.id,
                    medicine_id=medicine_data.medicine_id,
                    medicine_name=medicine_data.medicine_name,
                    dosage=medicine_data.dosage,
                    frequency=medicine_data.frequency,
                    duration_days=medicine_data.duration_days,
                    instructions=medicine_data.instructions,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                self.db.add(prescription_medicine)
            
            await self.db.commit()
            await self.db.refresh(prescription)
            
            result = await self.db.execute(
                select(Prescription)
                .options(selectinload(Prescription.prescription_medicines))
                .where(Prescription.id == prescription.id)
            )
            prescription = result.scalar_one()
            
            logger.info(f"Prescription created successfully (ID: {prescription.id}) with {len(prescription.prescription_medicines)} medicines")
            return prescription
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error creating prescription: {e}")
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error creating prescription: {e}")
            raise
    
    async def get_prescription_by_id(
        self,
        prescription_id: int,
        user_id: int
    ) -> Optional[Prescription]:
        """
        Get prescription by ID for specific user with medicines
        
        Args:
            prescription_id: Prescription ID
            user_id: User ID
            
        Returns:
            Prescription object with medicines or None
        """
        try:
            result = await self.db.execute(
                select(Prescription)
                .options(
                    selectinload(Prescription.prescription_medicines)
                )
                .where(and_(Prescription.id == prescription_id, Prescription.user_id == user_id))
            )
            prescription = result.scalar_one_or_none()
            
            if prescription:
                logger.debug(f"Prescription found by ID: {prescription_id}")
            else:
                logger.debug(f"No prescription found with ID: {prescription_id} for user {user_id}")
            
            return prescription
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting prescription by ID {prescription_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting prescription by ID {prescription_id}: {e}")
            return None
    
    async def get_prescriptions(
        self,
        user_id: int,
        filters: Optional[PrescriptionFilter] = None
    ) -> Tuple[List[Prescription], int]:
        """
        Get prescriptions for a user with optional filtering
        
        Args:
            user_id: User ID
            filters: Optional filtering parameters
            
        Returns:
            Tuple of (prescriptions_list, total_count)
        """
        logger.debug(f"Fetching prescriptions for user {user_id} with filters: {filters}")
        
        try:
            if filters is None:
                filters = PrescriptionFilter()
            
            # Build base query
            query = select(Prescription).where(Prescription.user_id == user_id)
            
            # Apply filters
            if filters.is_active is not None:
                query = query.where(Prescription.is_active == filters.is_active)
            
            if filters.doctor_name:
                search_term = f"%{filters.doctor_name.lower()}%"
                query = query.where(func.lower(Prescription.doctor_name).like(search_term))
            
            if filters.search:
                # Search in doctor name or medicine names
                search_term = f"%{filters.search.lower()}%"
                query = query.where(
                    or_(
                        func.lower(Prescription.doctor_name).like(search_term),
                        func.lower(Prescription.hospital_clinic).like(search_term)
                    )
                )
            
            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total_count = await self.db.scalar(count_query) or 0
            
            # Apply pagination
            offset = (filters.page - 1) * filters.per_page
            query = query.offset(offset).limit(filters.per_page)
            
            # Order by prescription date descending (newest first)
            query = query.order_by(Prescription.prescription_date.desc())
            
            # Execute query with medicines loaded
            result = await self.db.execute(
                query.options(selectinload(Prescription.prescription_medicines))
            )
            prescriptions = result.scalars().all()
            
            logger.debug(f"Fetched {len(prescriptions)} prescriptions for user {user_id} (total: {total_count})")
            return list(prescriptions), total_count
            
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching prescriptions for user {user_id}: {e}")
            return [], 0
        except Exception as e:
            logger.error(f"Unexpected error fetching prescriptions for user {user_id}: {e}")
            return [], 0
    
    async def update_prescription(
        self,
        prescription_id: int,
        user_id: int,
        prescription_update: PrescriptionUpdate
    ) -> Optional[Prescription]:
        """
        Update a prescription
        
        Args:
            prescription_id: Prescription ID
            user_id: User ID
            prescription_update: Update data
            
        Returns:
            Updated prescription object
            
        Raises:
            PrescriptionNotFoundException: If prescription not found
        """
        logger.info(f"Updating prescription {prescription_id} for user {user_id}")
        
        try:
            prescription = await self.get_prescription_by_id(prescription_id, user_id)
            if not prescription:
                logger.warning(f"Prescription update failed: Prescription {prescription_id} not found")
                raise PrescriptionNotFoundException(prescription_id)
            
            # Update fields
            update_data = prescription_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(prescription, field):
                    setattr(prescription, field, value)
            
            await self.db.commit()
            await self.db.refresh(prescription)
            
            result = await self.db.execute(
                select(Prescription)
                .options(selectinload(Prescription.prescription_medicines))
                .where(Prescription.id == prescription.id)
            )
            prescription = result.scalar_one()
            
            logger.info(f"Prescription {prescription_id} updated successfully")
            return prescription
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error updating prescription {prescription_id}: {e}")
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error updating prescription {prescription_id}: {e}")
            raise
    
    async def update_prescription_with_medicines(
        self,
        prescription_id: int,
        user_id: int,
        prescription_update: PrescriptionUpdate,
        medicines: Optional[List[PrescriptionMedicineCreate]] = None
    ) -> Optional[Prescription]:
        """
        Update a prescription with optional medicines update
        
        Args:
            prescription_id: Prescription ID
            user_id: User ID
            prescription_update: Update data
            medicines: Optional list of medicines to replace existing ones
            
        Returns:
            Updated prescription object
            
        Raises:
            PrescriptionNotFoundException: If prescription not found
        """
        logger.info(f"Updating prescription {prescription_id} with medicines for user {user_id}")
        
        try:
            prescription = await self.get_prescription_by_id(prescription_id, user_id)
            if not prescription:
                logger.warning(f"Prescription update failed: Prescription {prescription_id} not found")
                raise PrescriptionNotFoundException(prescription_id)
            
            # Update prescription fields
            update_data = prescription_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(prescription, field):
                    setattr(prescription, field, value)
            
            # Update medicines if provided
            if medicines is not None:
                # Delete existing medicines
                for pm in prescription.prescription_medicines:
                    await self.db.delete(pm)
                
                # Add new medicines
                for medicine_data in medicines:
                    prescription_medicine = PrescriptionMedicine(
                        prescription_id=prescription.id,
                        medicine_id=medicine_data.medicine_id,
                        medicine_name=medicine_data.medicine_name,
                        dosage=medicine_data.dosage,
                        frequency=medicine_data.frequency,
                        duration_days=medicine_data.duration_days,
                        instructions=medicine_data.instructions
                    )
                    self.db.add(prescription_medicine)
            
            await self.db.commit()
            await self.db.refresh(prescription)
            
            result = await self.db.execute(
                select(Prescription)
                .options(selectinload(Prescription.prescription_medicines))
                .where(Prescription.id == prescription.id)
            )
            prescription = result.scalar_one()
            
            logger.info(f"Prescription {prescription_id} updated successfully")
            return prescription
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error updating prescription {prescription_id}: {e}")
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error updating prescription {prescription_id}: {e}")
            raise
    
    async def delete_prescription(self, prescription_id: int, user_id: int) -> bool:
        """
        Delete a prescription
        
        Args:
            prescription_id: Prescription ID
            user_id: User ID
            
        Returns:
            True if deleted successfully
            
        Raises:
            PrescriptionNotFoundException: If prescription not found
        """
        logger.info(f"Deleting prescription {prescription_id} for user {user_id}")
        
        try:
            prescription = await self.get_prescription_by_id(prescription_id, user_id)
            if not prescription:
                logger.warning(f"Prescription deletion failed: Prescription {prescription_id} not found")
                raise PrescriptionNotFoundException(prescription_id)
            
            # Delete will cascade to prescription_medicines due to cascade="all, delete-orphan"
            await self.db.delete(prescription)
            await self.db.commit()
            
            logger.info(f"Prescription {prescription_id} deleted successfully")
            return True
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error deleting prescription {prescription_id}: {e}")
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error deleting prescription {prescription_id}: {e}")
            raise
    
    async def add_medicine_to_prescription(
        self,
        prescription_id: int,
        user_id: int,
        medicine_data: PrescriptionMedicineCreate
    ) -> PrescriptionMedicine:
        """
        Add a medicine to an existing prescription
        
        Args:
            prescription_id: Prescription ID
            user_id: User ID
            medicine_data: Medicine data to add
            
        Returns:
            Created PrescriptionMedicine object
            
        Raises:
            PrescriptionNotFoundException: If prescription not found
        """
        logger.info(f"Adding medicine to prescription {prescription_id}")
        
        try:
            prescription = await self.get_prescription_by_id(prescription_id, user_id)
            if not prescription:
                logger.warning(f"Prescription not found: {prescription_id}")
                raise PrescriptionNotFoundException(prescription_id)
            
            prescription_medicine = PrescriptionMedicine(
                prescription_id=prescription_id,
                medicine_id=medicine_data.medicine_id,
                medicine_name=medicine_data.medicine_name,
                dosage=medicine_data.dosage,
                frequency=medicine_data.frequency,
                duration_days=medicine_data.duration_days,
                instructions=medicine_data.instructions
            )
            
            self.db.add(prescription_medicine)
            await self.db.commit()
            await self.db.refresh(prescription_medicine)
            
            logger.info(f"Medicine added to prescription {prescription_id} (ID: {prescription_medicine.id})")
            return prescription_medicine
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error adding medicine to prescription {prescription_id}: {e}")
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error adding medicine to prescription {prescription_id}: {e}")
            raise
    
    async def remove_medicine_from_prescription(
        self,
        prescription_id: int,
        prescription_medicine_id: int,
        user_id: int
    ) -> bool:
        """
        Remove a medicine from a prescription
        
        Args:
            prescription_id: Prescription ID
            prescription_medicine_id: PrescriptionMedicine ID
            user_id: User ID
            
        Returns:
            True if deleted successfully
            
        Raises:
            PrescriptionNotFoundException: If prescription not found
        """
        logger.info(f"Removing medicine {prescription_medicine_id} from prescription {prescription_id}")
        
        try:
            # Verify prescription exists
            prescription = await self.get_prescription_by_id(prescription_id, user_id)
            if not prescription:
                raise PrescriptionNotFoundException(prescription_id)
            
            # Find the specific medicine
            result = await self.db.execute(
                select(PrescriptionMedicine).where(
                    and_(
                        PrescriptionMedicine.id == prescription_medicine_id,
                        PrescriptionMedicine.prescription_id == prescription_id
                    )
                )
            )
            prescription_medicine = result.scalar_one_or_none()
            
            if not prescription_medicine:
                logger.warning(f"Prescription medicine {prescription_medicine_id} not found in prescription {prescription_id}")
                return False
            
            await self.db.delete(prescription_medicine)
            await self.db.commit()
            
            logger.info(f"Medicine {prescription_medicine_id} removed from prescription {prescription_id}")
            return True
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error removing medicine from prescription {prescription_id}: {e}")
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error removing medicine from prescription {prescription_id}: {e}")
            raise
    
    async def get_expiring_prescriptions(
        self,
        user_id: int,
        days_ahead: int = 30
    ) -> List[Prescription]:
        """
        Get prescriptions expiring within specified days
        
        Args:
            user_id: User ID
            days_ahead: Number of days to look ahead
            
        Returns:
            List of expiring prescriptions
        """
        try:
            from datetime import date, timedelta
            
            today = date.today()
            future_date = today + timedelta(days=days_ahead)
            
            result = await self.db.execute(
                select(Prescription)
                .options(selectinload(Prescription.prescription_medicines))
                .where(
                    and_(
                        Prescription.user_id == user_id,
                        Prescription.is_active == True,
                        Prescription.valid_until.isnot(None),
                        Prescription.valid_until >= today,
                        Prescription.valid_until <= future_date
                    )
                )
                .order_by(Prescription.valid_until)
            )
            
            prescriptions = list(result.scalars().all())
            logger.debug(f"Found {len(prescriptions)} prescriptions expiring within {days_ahead} days")
            return prescriptions
            
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching expiring prescriptions for user {user_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching expiring prescriptions for user {user_id}: {e}")
            return []
    
    async def get_expired_prescriptions(self, user_id: int) -> List[Prescription]:
        """
        Get expired prescriptions
        
        Args:
            user_id: User ID
            
        Returns:
            List of expired prescriptions
        """
        try:
            from datetime import date
            
            today = date.today()
            
            result = await self.db.execute(
                select(Prescription)
                .options(selectinload(Prescription.prescription_medicines))
                .where(
                    and_(
                        Prescription.user_id == user_id,
                        Prescription.is_active == True,
                        Prescription.valid_until.isnot(None),
                        Prescription.valid_until < today
                    )
                )
                .order_by(Prescription.valid_until.desc())
            )
            
            prescriptions = list(result.scalars().all())
            logger.debug(f"Found {len(prescriptions)} expired prescriptions for user {user_id}")
            return prescriptions
            
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching expired prescriptions for user {user_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching expired prescriptions for user {user_id}: {e}")
            return []
