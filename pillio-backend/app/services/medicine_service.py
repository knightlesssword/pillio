from typing import List, Optional, Tuple
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from app.models.medicine import Medicine
from app.models.prescription_medicine import PrescriptionMedicine
from app.models.inventory_history import InventoryHistory
from app.schemas.medicine import MedicineCreate, MedicineUpdate, MedicineFilter
from app.core.exceptions import (
    MedicineNotFoundException, MedicineAlreadyExistsException,
    InsufficientStockException
)

logger = logging.getLogger(__name__)


class MedicineService:
    """Service for handling medicine-related operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_medicine(
        self, 
        user_id: int, 
        medicine_data: MedicineCreate
    ) -> Medicine:
        """
        Create a new medicine for a user
        
        Args:
            user_id: User ID
            medicine_data: Medicine creation data
            
        Returns:
            Created medicine object
            
        Raises:
            MedicineAlreadyExistsException: If medicine already exists for user
        """
        logger.info(f"Creating medicine '{medicine_data.name}' for user ID: {user_id}")
        
        try:
            # Check if medicine with same name already exists for user
            existing_medicine = await self.get_medicine_by_name_and_user(
                user_id, medicine_data.name
            )
            
            if existing_medicine:
                logger.warning(f"Medicine creation failed: '{medicine_data.name}' already exists for user {user_id}")
                raise MedicineAlreadyExistsException(medicine_data.name)
            
            # Create new medicine
            medicine = Medicine(
                user_id=user_id,
                name=medicine_data.name,
                generic_name=medicine_data.generic_name,
                dosage=medicine_data.dosage,
                form=medicine_data.form,
                unit=medicine_data.unit,
                current_stock=medicine_data.current_stock,
                min_stock_alert=medicine_data.min_stock_alert,
                notes=medicine_data.notes
            )
            
            self.db.add(medicine)
            await self.db.commit()
            await self.db.refresh(medicine)
            
            # If initial stock > 0, create inventory history record
            if medicine_data.current_stock > 0:
                await self.create_inventory_history(
                    medicine_id=medicine.id,
                    change_amount=medicine_data.current_stock,
                    change_type="added",
                    previous_stock=0,
                    new_stock=medicine_data.current_stock,
                    notes="Initial stock"
                )
            
            logger.info(f"Medicine '{medicine_data.name}' created successfully (ID: {medicine.id})")
            return medicine
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error creating medicine: {e}")
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error creating medicine: {e}")
            raise
    
    async def get_medicine_by_id(self, medicine_id: int, user_id: int) -> Optional[Medicine]:
        """Get medicine by ID for specific user"""
        try:
            result = await self.db.execute(
                select(Medicine)
                .options(selectinload(Medicine.user))
                .where(and_(Medicine.id == medicine_id, Medicine.user_id == user_id))
            )
            medicine = result.scalar_one_or_none()
            
            if medicine:
                logger.debug(f"Medicine found by ID: {medicine_id}")
            else:
                logger.debug(f"No medicine found with ID: {medicine_id} for user {user_id}")
            
            return medicine
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting medicine by ID {medicine_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting medicine by ID {medicine_id}: {e}")
            return None
    
    async def get_medicine_by_name_and_user(self, user_id: int, name: str) -> Optional[Medicine]:
        """Get medicine by name for specific user"""
        try:
            result = await self.db.execute(
                select(Medicine)
                .where(and_(Medicine.user_id == user_id, Medicine.name == name))
            )
            return result.scalar_one_or_none()
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting medicine by name '{name}': {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting medicine by name '{name}': {e}")
            return None
    
    async def get_medicines(
        self, 
        user_id: int, 
        filters: Optional[MedicineFilter] = None
    ) -> Tuple[List[Medicine], int]:
        """
        Get medicines for a user with optional filtering
        
        Args:
            user_id: User ID
            filters: Optional filtering parameters
            
        Returns:
            Tuple of (medicines_list, total_count)
        """
        logger.debug(f"Fetching medicines for user {user_id} with filters: {filters}")
        
        try:
            if filters is None:
                filters = MedicineFilter()
            
            # Build base query
            query = select(Medicine).where(Medicine.user_id == user_id)
            
            # Apply filters
            if filters.search:
                search_term = f"%{filters.search.lower()}%"
                query = query.where(
                    or_(
                        func.lower(Medicine.name).like(search_term),
                        func.lower(Medicine.generic_name).like(search_term)
                    )
                )
            
            if filters.form:
                query = query.where(Medicine.form == filters.form)
            
            if filters.is_low_stock is not None:
                if filters.is_low_stock:
                    query = query.where(Medicine.current_stock <= Medicine.min_stock_alert)
                else:
                    query = query.where(Medicine.current_stock > Medicine.min_stock_alert)
            
            if filters.low_stock_only:
                query = query.where(Medicine.current_stock <= Medicine.min_stock_alert)
            
            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total_count = await self.db.scalar(count_query) or 0
            
            # Apply pagination
            offset = (filters.page - 1) * filters.per_page
            query = query.offset(offset).limit(filters.per_page)
            
            # Order by name
            query = query.order_by(Medicine.name)
            
            # Execute query
            result = await self.db.execute(query)
            medicines = result.scalars().all()
            
            logger.debug(f"Fetched {len(medicines)} medicines for user {user_id} (total: {total_count})")
            return list(medicines), total_count
            
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching medicines for user {user_id}: {e}")
            return [], 0
        except Exception as e:
            logger.error(f"Unexpected error fetching medicines for user {user_id}: {e}")
            return [], 0
    
    async def update_medicine(
        self, 
        medicine_id: int, 
        user_id: int, 
        medicine_update: MedicineUpdate
    ) -> Optional[Medicine]:
        """
        Update a medicine
        
        Args:
            medicine_id: Medicine ID
            user_id: User ID
            medicine_update: Update data
            
        Returns:
            Updated medicine object
            
        Raises:
            MedicineNotFoundException: If medicine not found
        """
        logger.info(f"Updating medicine {medicine_id} for user {user_id}")
        
        try:
            medicine = await self.get_medicine_by_id(medicine_id, user_id)
            if not medicine:
                logger.warning(f"Medicine update failed: Medicine {medicine_id} not found")
                raise MedicineNotFoundException(medicine_id)
            
            # Store old values for history
            old_stock = medicine.current_stock
            old_name = medicine.name
            
            # Update fields
            update_data = medicine_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(medicine, field):
                    setattr(medicine, field, value)
            
            await self.db.commit()
            await self.db.refresh(medicine)
            
            # Create history record if stock changed
            if "current_stock" in update_data and old_stock != medicine.current_stock:
                change_amount = medicine.current_stock - old_stock
                change_type = "added" if change_amount > 0 else "consumed"
                
                await self.create_inventory_history(
                    medicine_id=medicine.id,
                    change_amount=change_amount,
                    change_type=change_type,
                    previous_stock=old_stock,
                    new_stock=medicine.current_stock,
                    notes=f"Stock updated via API"
                )
            
            logger.info(f"Medicine {medicine_id} updated successfully")
            return medicine
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error updating medicine {medicine_id}: {e}")
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error updating medicine {medicine_id}: {e}")
            raise
    
    async def delete_medicine(self, medicine_id: int, user_id: int) -> bool:
        """
        Delete a medicine
        
        Args:
            medicine_id: Medicine ID
            user_id: User ID
            
        Returns:
            True if deleted successfully
            
        Raises:
            MedicineNotFoundException: If medicine not found
        """
        logger.info(f"Deleting medicine {medicine_id} for user {user_id}")
        
        try:
            medicine = await self.get_medicine_by_id(medicine_id, user_id)
            if not medicine:
                logger.warning(f"Medicine deletion failed: Medicine {medicine_id} not found")
                raise MedicineNotFoundException(medicine_id)
            
            await self.db.delete(medicine)
            await self.db.commit()
            
            logger.info(f"Medicine {medicine_id} deleted successfully")
            return True
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error deleting medicine {medicine_id}: {e}")
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error deleting medicine {medicine_id}: {e}")
            raise
    
    async def adjust_stock(
        self, 
        medicine_id: int, 
        user_id: int, 
        adjustment: int, 
        reason: str = "manual"
    ) -> Medicine:
        """
        Adjust medicine stock level
        
        Args:
            medicine_id: Medicine ID
            user_id: User ID
            adjustment: Stock adjustment (positive for add, negative for remove)
            reason: Reason for adjustment
            
        Returns:
            Updated medicine object
            
        Raises:
            MedicineNotFoundException: If medicine not found
            InsufficientStockException: If not enough stock
        """
        logger.info(f"Adjusting stock for medicine {medicine_id}: {adjustment} ({reason})")
        
        try:
            medicine = await self.get_medicine_by_id(medicine_id, user_id)
            if not medicine:
                logger.warning(f"Stock adjustment failed: Medicine {medicine_id} not found")
                raise MedicineNotFoundException(medicine_id)
            
            old_stock = medicine.current_stock
            new_stock = old_stock + adjustment
            
            # Check if adjustment would result in negative stock
            if new_stock < 0:
                logger.warning(f"Stock adjustment failed: Insufficient stock for medicine {medicine_id}")
                raise InsufficientStockException(old_stock, abs(adjustment))
            
            # Update stock
            medicine.current_stock = new_stock
            await self.db.commit()
            await self.db.refresh(medicine)
            
            # Create inventory history record
            change_type = "added" if adjustment > 0 else "consumed"
            await self.create_inventory_history(
                medicine_id=medicine.id,
                change_amount=adjustment,
                change_type=change_type,
                previous_stock=old_stock,
                new_stock=new_stock,
                notes=f"Stock {change_type} - {reason}"
            )
            
            logger.info(f"Stock adjusted for medicine {medicine_id}: {old_stock} -> {new_stock}")
            return medicine
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error adjusting stock for medicine {medicine_id}: {e}")
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error adjusting stock for medicine {medicine_id}: {e}")
            raise
    
    async def get_low_stock_medicines(self, user_id: int) -> List[Medicine]:
        """Get medicines with low stock levels"""
        try:
            result = await self.db.execute(
                select(Medicine)
                .where(
                    and_(
                        Medicine.user_id == user_id,
                        Medicine.current_stock <= Medicine.min_stock_alert
                    )
                )
                .order_by(Medicine.current_stock)
            )
            medicines = list(result.scalars().all())
            logger.debug(f"Found {len(medicines)} low stock medicines for user {user_id}")
            return medicines
            
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching low stock medicines for user {user_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching low stock medicines for user {user_id}: {e}")
            return []
    
    async def get_medicines_by_form(self, user_id: int, form: str) -> List[Medicine]:
        """Get medicines by form type"""
        try:
            result = await self.db.execute(
                select(Medicine)
                .where(and_(Medicine.user_id == user_id, Medicine.form == form))
                .order_by(Medicine.name)
            )
            return list(result.scalars().all())
            
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching medicines by form '{form}' for user {user_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching medicines by form '{form}' for user {user_id}: {e}")
            return []
    
    async def search_medicines(self, user_id: int, query: str) -> List[Medicine]:
        """Search medicines by name or generic name"""
        try:
            search_term = f"%{query.lower()}%"
            result = await self.db.execute(
                select(Medicine)
                .where(
                    and_(
                        Medicine.user_id == user_id,
                        or_(
                            func.lower(Medicine.name).like(search_term),
                            func.lower(Medicine.generic_name).like(search_term)
                        )
                    )
                )
                .order_by(Medicine.name)
            )
            return list(result.scalars().all())
            
        except SQLAlchemyError as e:
            logger.error(f"Database error searching medicines for user {user_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error searching medicines for user {user_id}: {e}")
            return []
    
    async def get_medicine_statistics(self, user_id: int) -> dict:
        """Get medicine statistics for user"""
        try:
            # Total medicines
            total_medicines = await self.db.scalar(
                select(func.count(Medicine.id)).where(Medicine.user_id == user_id)
            ) or 0
            
            # Low stock medicines
            low_stock_count = await self.db.scalar(
                select(func.count(Medicine.id)).where(
                    and_(
                        Medicine.user_id == user_id,
                        Medicine.current_stock <= Medicine.min_stock_alert
                    )
                )
            ) or 0
            
            # Medicines by form
            medicines_by_form = await self.db.execute(
                select(Medicine.form, func.count(Medicine.id))
                .where(Medicine.user_id == user_id)
                .group_by(Medicine.form)
            )
            
            form_counts = {row[0]: row[1] for row in medicines_by_form.fetchall()}
            
            # Total stock value (assuming average cost, this would need enhancement)
            total_stock_items = await self.db.scalar(
                select(func.sum(Medicine.current_stock)).where(Medicine.user_id == user_id)
            ) or 0
            
            stats = {
                "total_medicines": total_medicines,
                "low_stock_count": low_stock_count,
                "medicines_by_form": form_counts,
                "total_stock_items": total_stock_items,
                "low_stock_percentage": round((low_stock_count / total_medicines * 100) if total_medicines > 0 else 0, 2)
            }
            
            logger.debug(f"Medicine statistics for user {user_id}: {stats}")
            return stats
            
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching medicine statistics for user {user_id}: {e}")
            return {"error": "Failed to fetch statistics"}
        except Exception as e:
            logger.error(f"Unexpected error fetching medicine statistics for user {user_id}: {e}")
            return {"error": "Failed to fetch statistics"}
    
    async def create_inventory_history(
        self,
        medicine_id: int,
        change_amount: int,
        change_type: str,
        previous_stock: int,
        new_stock: int,
        notes: Optional[str] = None,
        reference_id: Optional[int] = None
    ) -> InventoryHistory:
        """Create inventory history record"""
        try:
            history = InventoryHistory(
                medicine_id=medicine_id,
                change_amount=change_amount,
                change_type=change_type,
                previous_stock=previous_stock,
                new_stock=new_stock,
                notes=notes,
                reference_id=reference_id
            )
            
            self.db.add(history)
            await self.db.commit()
            await self.db.refresh(history)
            
            logger.debug(f"Inventory history created for medicine {medicine_id}: {change_type} {change_amount}")
            return history
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error creating inventory history for medicine {medicine_id}: {e}")
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error creating inventory history for medicine {medicine_id}: {e}")
            raise
    
    async def add_prescription_medicine_to_inventory(
        self,
        user_id: int,
        prescription_medicine_id: int,
        medicine_data: MedicineCreate
    ) -> Medicine:
        """
        Create a medicine in inventory from a prescription medicine.
        Links all matching prescription medicines to the new inventory medicine.
        
        Args:
            user_id: User ID
            prescription_medicine_id: The prescription medicine ID to base the new medicine on
            medicine_data: Medicine creation data
            
        Returns:
            Created medicine object
        """
        logger.info(f"Creating medicine from prescription medicine {prescription_medicine_id} for user {user_id}")
        
        try:
            # Get the prescription medicine to get original details
            result = await self.db.execute(
                select(PrescriptionMedicine).where(
                    and_(
                        PrescriptionMedicine.id == prescription_medicine_id,
                        PrescriptionMedicine.medicine_id.is_(None)
                    )
                )
            )
            prescription_medicine = result.scalar_one_or_none()
            
            if not prescription_medicine:
                logger.warning(f"Prescription medicine {prescription_medicine_id} not found or already linked")
                raise MedicineNotFoundException(prescription_medicine_id)
            
            # Create medicine in inventory
            medicine = await self.create_medicine(user_id, medicine_data)
            
            # Find all prescription medicines with same name + dosage for this user
            # and link them to the new medicine
            from app.models.prescription import Prescription
            
            # Get all prescriptions for this user that have matching medicines
            result = await self.db.execute(
                select(PrescriptionMedicine)
                .join(Prescription)
                .where(
                    and_(
                        Prescription.user_id == user_id,
                        PrescriptionMedicine.medicine_id.is_(None),
                        func.lower(PrescriptionMedicine.medicine_name) == func.lower(prescription_medicine.medicine_name),
                        func.lower(PrescriptionMedicine.dosage) == func.lower(prescription_medicine.dosage)
                    )
                )
            )
            matching_medicines = result.scalars().all()
            
            # Link all matching prescription medicines to the new inventory medicine
            for pm in matching_medicines:
                pm.medicine_id = medicine.id
            
            await self.db.commit()
            
            logger.info(f"Medicine created from prescription (ID: {medicine.id}) and linked to {len(matching_medicines)} prescription medicines")
            return medicine
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error creating medicine from prescription: {e}")
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error creating medicine from prescription: {e}")
            raise
