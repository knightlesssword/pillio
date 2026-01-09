from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
import logging
from pydantic import BaseModel
from app.database import get_db
from app.core.security import get_current_user
from app.services.medicine_service import MedicineService
from app.services.prescription_service import PrescriptionService
from app.models.user import User
from app.models.medicine import Medicine
from app.models.prescription import Prescription
from app.models.prescription_medicine import PrescriptionMedicine
from app.models.inventory_history import InventoryHistory
from app.schemas.medicine import (
    Medicine as MedicineSchema, 
    MedicineCreate, 
    MedicineUpdate,
    MedicineFilter,
    MedicineWithDetails
)
from app.schemas.inventory_history import InventoryHistory as InventoryHistorySchema
from app.schemas.inventory_history import InventoryHistoryWithMedicine
from app.schemas.common import PaginatedResponse, MessageResponse
from app.core.exceptions import (
    MedicineNotFoundException, MedicineAlreadyExistsException,
    InsufficientStockException
)

logger = logging.getLogger(__name__)

router = APIRouter()


def get_medicine_service(db: AsyncSession = Depends(get_db)) -> MedicineService:
    """Dependency to get medicine service"""
    return MedicineService(db)


def get_prescription_service(db: AsyncSession = Depends(get_db)) -> PrescriptionService:
    """Dependency to get prescription service"""
    return PrescriptionService(db)


# Schema for medicine dropdown item
class MedicineDropdownItem(BaseModel):
    id: int
    name: str
    dosage: str
    form: str
    unit: str


# Schema for missing medicine from prescriptions
class MissingMedicineItem(BaseModel):
    id: int
    medicine_name: str
    dosage: str
    frequency: str
    duration_days: int
    instructions: Optional[str] = None
    prescriptions_count: int = 1
    prescription_id: int  # For linking back


@router.post("/", response_model=MedicineSchema, status_code=status.HTTP_201_CREATED)
async def create_medicine(
    medicine_data: MedicineCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    medicine_service: MedicineService = Depends(get_medicine_service)
):
    """
    Create a new medicine
    
    - **name**: Medicine name (required, unique per user)
    - **generic_name**: Generic name (optional)
    - **dosage**: Dosage amount (e.g., "100mg", "500mg")
    - **form**: Medicine form (e.g., "tablet", "capsule", "syrup")
    - **unit**: Unit of measurement (e.g., "tablets", "ml", "mg")
    - **current_stock**: Current stock level (default: 0)
    - **min_stock_alert**: Minimum stock for alerts (default: 5)
    - **notes**: Additional notes (optional)
    """
    try:
        medicine = await medicine_service.create_medicine(
            user_id=current_user.id,
            medicine_data=medicine_data
        )
        logger.info(f"Medicine created: '{medicine.name}' (ID: {medicine.id}) for user {current_user.id}")
        return medicine
    
    except MedicineAlreadyExistsException:
        logger.warning(f"Medicine creation failed: '{medicine_data.name}' already exists for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Medicine '{medicine_data.name}' already exists"
        )
    
    except Exception as e:
        logger.error(f"Error creating medicine: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create medicine"
        )


@router.get("/", response_model=PaginatedResponse[MedicineSchema])
async def get_medicines(
    search: Optional[str] = Query(None, description="Search medicines by name or generic name"),
    form: Optional[str] = Query(None, description="Filter by medicine form"),
    is_low_stock: Optional[bool] = Query(None, description="Filter by low stock status"),
    low_stock_only: bool = Query(False, description="Show only low stock medicines"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    medicine_service: MedicineService = Depends(get_medicine_service)
):
    """
    Get user's medicines with optional filtering and pagination
    """
    try:
        filters = MedicineFilter(
            search=search,
            form=form,
            is_low_stock=is_low_stock,
            low_stock_only=low_stock_only,
            page=page,
            per_page=per_page
        )
        
        medicines, total_count = await medicine_service.get_medicines(
            user_id=current_user.id,
            filters=filters
        )
        
        pages = (total_count + per_page - 1) // per_page
        
        logger.debug(f"Fetched {len(medicines)} medicines for user {current_user.id} (total: {total_count})")
        return PaginatedResponse(
            items=medicines,
            total=total_count,
            page=page,
            per_page=per_page,
            pages=pages
        )
    
    except Exception as e:
        logger.error(f"Error fetching medicines: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch medicines"
        )


@router.get("/search", response_model=list[MedicineSchema])
async def search_medicines(
    q: str = Query(..., min_length=1, description="Search query"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    medicine_service: MedicineService = Depends(get_medicine_service)
):
    """
    Search medicines by name or generic name
    """
    try:
        medicines = await medicine_service.search_medicines(
            user_id=current_user.id,
            query=q
        )
        logger.debug(f"Search for '{q}' returned {len(medicines)} medicines for user {current_user.id}")
        return medicines
    
    except Exception as e:
        logger.error(f"Error searching medicines: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )


@router.get("/for-prescription", response_model=list[MedicineDropdownItem])
async def get_medicines_for_prescription(
    search: Optional[str] = Query(None, description="Search query"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    medicine_service: MedicineService = Depends(get_medicine_service)
):
    """
    Get medicines formatted for prescription dropdown selection.
    Returns simplified list with id, name, dosage, form, and unit.
    """
    try:
        query = select(Medicine).where(Medicine.user_id == current_user.id)
        
        if search:
            search_term = f"%{search.lower()}%"
            query = query.where(
                func.lower(Medicine.name).like(search_term)
            )
        
        query = query.order_by(Medicine.name).limit(50)
        
        result = await db.execute(query)
        medicines = result.scalars().all()
        
        return [
            MedicineDropdownItem(
                id=m.id,
                name=m.name,
                dosage=m.dosage,
                form=m.form,
                unit=m.unit
            )
            for m in medicines
        ]
    
    except Exception as e:
        logger.error(f"Error fetching medicines for prescription: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch medicines"
        )


@router.get("/missing-from-inventory", response_model=list[MissingMedicineItem])
async def get_missing_from_inventory(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get prescription medicines that are not in the user's inventory.
    Useful for identifying medicines that should be added to inventory.
    """
    try:
        # Get prescription medicines where medicine_id is null
        # or where the linked medicine no longer exists
        query = (
            select(PrescriptionMedicine)
            .options(selectinload(PrescriptionMedicine.prescription))
            .join(PrescriptionMedicine.prescription)
            .where(
                and_(
                    PrescriptionMedicine.medicine_id.is_(None),
                    Prescription.user_id == current_user.id,
                    Prescription.is_active == True
                )
            )
        )
        
        result = await db.execute(query)
        prescription_medicines = result.scalars().all()
        
        # Group by unique medicine_name + dosage
        seen = {}
        for pm in prescription_medicines:
            key = (pm.medicine_name.lower(), pm.dosage.lower())
            if key not in seen:
                seen[key] = {
                    "id": pm.id,
                    "medicine_name": pm.medicine_name,
                    "dosage": pm.dosage,
                    "frequency": pm.frequency,
                    "duration_days": pm.duration_days,
                    "instructions": pm.instructions,
                    "prescriptions_count": 1,
                    "prescription_id": pm.prescription_id
                }
            else:
                seen[key]["prescriptions_count"] += 1
        
        return list(seen.values())
    
    except Exception as e:
        logger.error(f"Error fetching missing medicines: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch missing medicines"
        )


@router.post("/from-prescription", response_model=MedicineSchema)
async def create_medicine_from_prescription(
    prescription_medicine_id: int = Query(..., description="Prescription medicine ID to create medicine from"),
    medicine_data: MedicineCreate = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    medicine_service: MedicineService = Depends(get_medicine_service)
):
    """
    Create a medicine in inventory from a prescription medicine.
    Links all matching prescription medicines (same name + dosage) to the new inventory medicine.
    
    The prescription medicine data is used as a template for the new medicine.
    """
    try:
        medicine = await medicine_service.add_prescription_medicine_to_inventory(
            user_id=current_user.id,
            prescription_medicine_id=prescription_medicine_id,
            medicine_data=medicine_data
        )
        
        logger.info(f"Medicine created from prescription: '{medicine.name}' (ID: {medicine.id}) for user {current_user.id}")
        return medicine
    
    except MedicineNotFoundException:
        logger.warning(f"Prescription medicine {prescription_medicine_id} not found or already linked")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prescription medicine not found or already linked to inventory"
        )
    
    except MedicineAlreadyExistsException:
        logger.warning(f"Medicine creation failed: '{medicine_data.name}' already exists for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Medicine '{medicine_data.name}' already exists"
        )
    
    except Exception as e:
        logger.error(f"Error creating medicine from prescription: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create medicine from prescription"
        )


@router.get("/low-stock", response_model=list[MedicineSchema])
async def get_low_stock_medicines(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    medicine_service: MedicineService = Depends(get_medicine_service)
):
    """
    Get medicines with low stock levels
    """
    try:
        medicines = await medicine_service.get_low_stock_medicines(
            user_id=current_user.id
        )
        logger.debug(f"Found {len(medicines)} low stock medicines for user {current_user.id}")
        return medicines
    
    except Exception as e:
        logger.error(f"Error fetching low stock medicines: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch low stock medicines"
        )


@router.get("/by-form/{form}", response_model=list[MedicineSchema])
async def get_medicines_by_form(
    form: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    medicine_service: MedicineService = Depends(get_medicine_service)
):
    """
    Get medicines by form type
    """
    try:
        medicines = await medicine_service.get_medicines_by_form(
            user_id=current_user.id,
            form=form
        )
        logger.debug(f"Found {len(medicines)} medicines of form '{form}' for user {current_user.id}")
        return medicines
    
    except Exception as e:
        logger.error(f"Error fetching medicines by form: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch medicines by form"
        )


@router.get("/statistics")
async def get_medicine_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    medicine_service: MedicineService = Depends(get_medicine_service)
):
    """
    Get medicine statistics for the current user
    """
    try:
        stats = await medicine_service.get_medicine_statistics(
            user_id=current_user.id
        )
        logger.debug(f"Medicine statistics for user {current_user.id}: {stats}")
        return stats
    
    except Exception as e:
        logger.error(f"Error fetching medicine statistics: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch statistics"
        )


@router.get("/inventory-history", response_model=PaginatedResponse[InventoryHistoryWithMedicine])
async def get_all_inventory_history(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    change_type: Optional[str] = Query(None, description="Filter by change type (added, consumed, adjusted, expired)"),
    start_date: Optional[date] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all inventory history records for the current user with pagination and filtering.
    """
    try:
        logger.debug(f"Fetching inventory history - page={page}, per_page={per_page}, start_date={start_date}, end_date={end_date}, change_type={change_type}, user_id={current_user.id}")
        
        # Build query to get all inventory history joined with medicines
        query = (
            select(InventoryHistory)
            .options(selectinload(InventoryHistory.medicine))
            .join(Medicine, InventoryHistory.medicine_id == Medicine.id)
            .where(Medicine.user_id == current_user.id)
        )
        
        # Apply change type filter if provided
        if change_type:
            query = query.where(InventoryHistory.change_type == change_type)
        
        # Apply date range filter if provided
        if start_date:
            query = query.where(InventoryHistory.created_at >= start_date)
        if end_date:
            # Convert end_date to datetime with end of day to include all records from that date
            from datetime import datetime, time
            end_datetime = datetime.combine(end_date, time.max)
            query = query.where(InventoryHistory.created_at <= end_datetime)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total_count = result.scalar() or 0
        
        # Apply ordering and pagination
        query = query.order_by(InventoryHistory.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        
        result = await db.execute(query)
        history_records = result.scalars().all()
        
        logger.debug(f"Fetched {len(history_records)} inventory history records for user {current_user.id} (total: {total_count})")
        # Convert to response schema with medicine name
        items = []
        for record in history_records:
            item = {
                "id": record.id,
                "medicine_id": record.medicine_id,
                "change_amount": record.change_amount,
                "change_type": record.change_type,
                "previous_stock": record.previous_stock,
                "new_stock": record.new_stock,
                "reference_id": record.reference_id,
                "notes": record.notes,
                "created_at": record.created_at,
                "medicine_name": record.medicine.name if record.medicine else "Unknown"
            }
            items.append(InventoryHistoryWithMedicine(**item))
        
        pages = (total_count + per_page - 1) // per_page if total_count > 0 else 0
        
        logger.debug(f"Fetched {len(items)} inventory history records for user {current_user.id}")
        return PaginatedResponse(
            items=items,
            total=total_count,
            page=page,
            per_page=per_page,
            pages=pages
        )
    
    except Exception as e:
        logger.error(f"Error fetching all inventory history: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch inventory history"
        )


# Dynamic routes - must come after all static routes to avoid path conflicts

@router.get("/{medicine_id}", response_model=MedicineWithDetails)
async def get_medicine(
    medicine_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    medicine_service: MedicineService = Depends(get_medicine_service)
):
    """
    Get specific medicine by ID
    """
    try:
        medicine = await medicine_service.get_medicine_by_id(
            medicine_id=medicine_id,
            user_id=current_user.id
        )
        
        if not medicine:
            logger.warning(f"Medicine {medicine_id} not found for user {current_user.id}")
            raise MedicineNotFoundException(medicine_id)
        
        logger.debug(f"Medicine {medicine_id} fetched for user {current_user.id}")
        return medicine
    
    except MedicineNotFoundException:
        raise
    
    except Exception as e:
        logger.error(f"Error fetching medicine {medicine_id}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch medicine"
        )


@router.put("/{medicine_id}", response_model=MedicineSchema)
async def update_medicine(
    medicine_id: int,
    medicine_update: MedicineUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    medicine_service: MedicineService = Depends(get_medicine_service)
):
    """
    Update medicine information
    
    - **name**: Medicine name (optional)
    - **generic_name**: Generic name (optional)
    - **dosage**: Dosage amount (optional)
    - **form**: Medicine form (optional)
    - **unit**: Unit of measurement (optional)
    - **current_stock**: Current stock level (optional)
    - **min_stock_alert**: Minimum stock for alerts (optional)
    - **notes**: Additional notes (optional)
    """
    try:
        medicine = await medicine_service.update_medicine(
            medicine_id=medicine_id,
            user_id=current_user.id,
            medicine_update=medicine_update
        )
        
        logger.info(f"Medicine {medicine_id} updated for user {current_user.id}")
        return medicine
    
    except MedicineNotFoundException:
        logger.warning(f"Medicine update failed: Medicine {medicine_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine with ID {medicine_id} not found"
        )
    
    except Exception as e:
        logger.error(f"Error updating medicine {medicine_id}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update medicine"
        )


@router.delete("/{medicine_id}")
async def delete_medicine(
    medicine_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    medicine_service: MedicineService = Depends(get_medicine_service)
):
    """
    Delete a medicine
    """
    try:
        success = await medicine_service.delete_medicine(
            medicine_id=medicine_id,
            user_id=current_user.id
        )
        
        if not success:
            logger.warning(f"Medicine deletion failed: Medicine {medicine_id} not found")
            raise MedicineNotFoundException(medicine_id)
        
        logger.info(f"Medicine {medicine_id} deleted for user {current_user.id}")
        return MessageResponse(
            message="Medicine deleted successfully",
            success=True
        )
    
    except MedicineNotFoundException:
        logger.warning(f"Medicine deletion failed: Medicine {medicine_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine with ID {medicine_id} not found"
        )
    
    except Exception as e:
        logger.error(f"Error deleting medicine {medicine_id}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete medicine"
        )


@router.post("/{medicine_id}/adjust-stock", response_model=MedicineSchema)
async def adjust_stock(
    medicine_id: int,
    adjustment: int = Query(..., description="Stock adjustment (positive for add, negative for remove)"),
    reason: str = Query("manual", description="Reason for adjustment"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    medicine_service: MedicineService = Depends(get_medicine_service)
):
    """
    Adjust medicine stock level
    
    - **adjustment**: Stock adjustment (positive for add, negative for remove)
    - **reason**: Reason for adjustment
    """
    try:
        medicine = await medicine_service.adjust_stock(
            medicine_id=medicine_id,
            user_id=current_user.id,
            adjustment=adjustment,
            reason=reason
        )
        
        logger.info(f"Stock adjusted for medicine {medicine_id}: {adjustment} ({reason})")
        return medicine
    
    except MedicineNotFoundException:
        logger.warning(f"Stock adjustment failed: Medicine {medicine_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine with ID {medicine_id} not found"
        )
    
    except InsufficientStockException as e:
        logger.warning(f"Stock adjustment failed: Insufficient stock for medicine {medicine_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"Error adjusting stock for medicine {medicine_id}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to adjust stock"
        )


@router.get("/{medicine_id}/history", response_model=list[InventoryHistorySchema])
async def get_medicine_history(
    medicine_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    medicine_service: MedicineService = Depends(get_medicine_service)
):
    """
    Get inventory history for a specific medicine
    """
    try:
        # First check if medicine exists and belongs to user
        medicine = await medicine_service.get_medicine_by_id(
            medicine_id=medicine_id,
            user_id=current_user.id
        )
        
        if not medicine:
            logger.warning(f"Medicine history fetch failed: Medicine {medicine_id} not found")
            raise MedicineNotFoundException(medicine_id)
        
        # Get inventory history
        result = await db.execute(
            select(InventoryHistory)
            .options(selectinload(InventoryHistory.medicine))
            .where(InventoryHistory.medicine_id == medicine_id)
            .order_by(InventoryHistory.created_at.desc())
        )
        
        history_records = result.scalars().all()
        logger.debug(f"Fetched {len(history_records)} history records for medicine {medicine_id}")
        return list(history_records)
    
    except MedicineNotFoundException:
        raise
    
    except Exception as e:
        logger.error(f"Error fetching medicine history for {medicine_id}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch medicine history"
        )
