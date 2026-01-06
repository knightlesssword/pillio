from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.core.security import get_current_user
from app.services.medicine_service import MedicineService
from app.models.user import User
from app.schemas.medicine import (
    Medicine as MedicineSchema, 
    MedicineCreate, 
    MedicineUpdate,
    MedicineFilter,
    MedicineWithDetails,
    MedicineWithHistory
)
from app.schemas.inventory_history import InventoryHistory as InventoryHistorySchema
from app.schemas.common import PaginatedResponse, MessageResponse
from app.core.exceptions import (
    MedicineNotFoundException, MedicineAlreadyExistsException,
    InsufficientStockException
)

router = APIRouter()


def get_medicine_service(db: AsyncSession = Depends(get_db)) -> MedicineService:
    """Dependency to get medicine service"""
    return MedicineService(db)


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
        return medicine
    
    except MedicineAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Medicine '{medicine_data.name}' already exists"
        )
    
    except Exception as e:
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
        
        return PaginatedResponse(
            items=medicines,
            total=total_count,
            page=page,
            per_page=per_page,
            pages=pages
        )
    
    except Exception as e:
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
        return medicines
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
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
        return medicines
    
    except Exception as e:
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
        return medicines
    
    except Exception as e:
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
        return stats
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch statistics"
        )


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
            raise MedicineNotFoundException(medicine_id)
        
        return medicine
    
    except MedicineNotFoundException:
        raise
    
    except Exception as e:
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
        
        return medicine
    
    except MedicineNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine with ID {medicine_id} not found"
        )
    
    except Exception as e:
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
            raise MedicineNotFoundException(medicine_id)
        
        return MessageResponse(
            message="Medicine deleted successfully",
            success=True
        )
    
    except MedicineNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine with ID {medicine_id} not found"
        )
    
    except Exception as e:
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
        
        return medicine
    
    except MedicineNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine with ID {medicine_id} not found"
        )
    
    except InsufficientStockException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
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
            raise MedicineNotFoundException(medicine_id)
        
        # Get inventory history
        from app.models.inventory_history import InventoryHistory
        from sqlalchemy.orm import selectinload
        
        result = await db.execute(
            select(InventoryHistory)
            .options(selectinload(InventoryHistory.medicine))
            .where(InventoryHistory.medicine_id == medicine_id)
            .order_by(InventoryHistory.created_at.desc())
        )
        
        history_records = result.scalars().all()
        return list(history_records)
    
    except MedicineNotFoundException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch medicine history"
        )