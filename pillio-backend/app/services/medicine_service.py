from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from app.models.medicine import Medicine
from app.models.user import User
from app.models.inventory_history import InventoryHistory
from app.schemas.medicine import MedicineCreate, MedicineUpdate, MedicineFilter
from app.core.exceptions import (
    MedicineNotFoundException, MedicineAlreadyExistsException,
    InsufficientStockException, LowStockThresholdException
)


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
        # Check if medicine with same name already exists for user
        existing_medicine = await self.get_medicine_by_name_and_user(
            user_id, medicine_data.name
        )
        
        if existing_medicine:
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
        
        return medicine
    
    async def get_medicine_by_id(self, medicine_id: int, user_id: int) -> Optional[Medicine]:
        """Get medicine by ID for specific user"""
        result = await self.db.execute(
            select(Medicine)
            .options(selectinload(Medicine.user))
            .where(and_(Medicine.id == medicine_id, Medicine.user_id == user_id))
        )
        return result.scalar_one_or_none()
    
    async def get_medicine_by_name_and_user(self, user_id: int, name: str) -> Optional[Medicine]:
        """Get medicine by name for specific user"""
        result = await self.db.execute(
            select(Medicine)
            .where(and_(Medicine.user_id == user_id, Medicine.name == name))
        )
        return result.scalar_one_or_none()
    
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
        
        return list(medicines), total_count
    
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
        medicine = await self.get_medicine_by_id(medicine_id, user_id)
        if not medicine:
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
        
        return medicine
    
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
        medicine = await self.get_medicine_by_id(medicine_id, user_id)
        if not medicine:
            raise MedicineNotFoundException(medicine_id)
        
        await self.db.delete(medicine)
        await self.db.commit()
        
        return True
    
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
        medicine = await self.get_medicine_by_id(medicine_id, user_id)
        if not medicine:
            raise MedicineNotFoundException(medicine_id)
        
        old_stock = medicine.current_stock
        new_stock = old_stock + adjustment
        
        # Check if adjustment would result in negative stock
        if new_stock < 0:
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
        
        return medicine
    
    async def get_low_stock_medicines(self, user_id: int) -> List[Medicine]:
        """Get medicines with low stock levels"""
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
        return list(result.scalars().all())
    
    async def get_medicines_by_form(self, user_id: int, form: str) -> List[Medicine]:
        """Get medicines by form type"""
        result = await self.db.execute(
            select(Medicine)
            .where(and_(Medicine.user_id == user_id, Medicine.form == form))
            .order_by(Medicine.name)
        )
        return list(result.scalars().all())
    
    async def search_medicines(self, user_id: int, query: str) -> List[Medicine]:
        """Search medicines by name or generic name"""
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
    
    async def get_medicine_statistics(self, user_id: int) -> dict:
        """Get medicine statistics for user"""
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
        
        return {
            "total_medicines": total_medicines,
            "low_stock_count": low_stock_count,
            "medicines_by_form": form_counts,
            "total_stock_items": total_stock_items,
            "low_stock_percentage": round((low_stock_count / total_medicines * 100) if total_medicines > 0 else 0, 2)
        }
    
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
        
        return history