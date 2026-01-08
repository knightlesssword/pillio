from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import logging
from app.database import get_db
from app.core.security import get_current_user
from app.services.prescription_service import PrescriptionService
from app.models.user import User
from app.schemas.prescription import (
    Prescription as PrescriptionSchema,
    PrescriptionCreate,
    PrescriptionUpdate,
    PrescriptionUpdateWithMedicines,
    PrescriptionWithMedicines,
    PrescriptionFilter,
    PrescriptionMedicineCreate,
    PrescriptionMedicineResponse
)
from app.schemas.common import PaginatedResponse, MessageResponse
from app.core.exceptions import PrescriptionNotFoundException

logger = logging.getLogger(__name__)

router = APIRouter()


def get_prescription_service(db: AsyncSession = Depends(get_db)) -> PrescriptionService:
    """Dependency to get prescription service"""
    return PrescriptionService(db)


@router.post("/", response_model=PrescriptionWithMedicines, status_code=status.HTTP_201_CREATED)
async def create_prescription(
    prescription_data: PrescriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    prescription_service: PrescriptionService = Depends(get_prescription_service)
):
    """
    Create a new prescription with multiple medicines
    
    - **doctor_name**: Name of the prescribing doctor (required)
    - **hospital_clinic**: Hospital or clinic name (optional)
    - **prescription_date**: Date of prescription (required)
    - **valid_until**: Expiry date of prescription (optional)
    - **notes**: Additional notes (optional)
    - **medicines**: List of medicines (at least one required)
    """
    try:
        prescription = await prescription_service.create_prescription(
            user_id=current_user.id,
            prescription_data=prescription_data
        )
        logger.info(f"Prescription created: '{prescription.doctor_name}' (ID: {prescription.id}) for user {current_user.id}")
        return prescription
        
    except Exception as e:
        logger.error(f"Error creating prescription: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create prescription"
        )


@router.get("/", response_model=PaginatedResponse[PrescriptionWithMedicines])
async def get_prescriptions(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    doctor_name: Optional[str] = Query(None, description="Filter by doctor name"),
    search: Optional[str] = Query(None, description="Search in doctor name or hospital"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    prescription_service: PrescriptionService = Depends(get_prescription_service)
):
    """
    Get user's prescriptions with optional filtering and pagination
    """
    try:
        filters = PrescriptionFilter(
            is_active=is_active,
            doctor_name=doctor_name,
            search=search,
            page=page,
            per_page=per_page
        )
        
        prescriptions, total_count = await prescription_service.get_prescriptions(
            user_id=current_user.id,
            filters=filters
        )
        
        pages = (total_count + per_page - 1) // per_page if total_count > 0 else 0
        
        logger.debug(f"Fetched {len(prescriptions)} prescriptions for user {current_user.id} (total: {total_count})")
        return PaginatedResponse(
            items=prescriptions,
            total=total_count,
            page=page,
            per_page=per_page,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"Error fetching prescriptions: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch prescriptions"
        )


@router.get("/expiring", response_model=list[PrescriptionWithMedicines])
async def get_expiring_prescriptions(
    days_ahead: int = Query(30, ge=1, le=365, description="Number of days to look ahead"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    prescription_service: PrescriptionService = Depends(get_prescription_service)
):
    """
    Get prescriptions expiring within specified days
    """
    try:
        prescriptions = await prescription_service.get_expiring_prescriptions(
            user_id=current_user.id,
            days_ahead=days_ahead
        )
        return prescriptions
        
    except Exception as e:
        logger.error(f"Error fetching expiring prescriptions: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch expiring prescriptions"
        )


@router.get("/expired", response_model=list[PrescriptionWithMedicines])
async def get_expired_prescriptions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    prescription_service: PrescriptionService = Depends(get_prescription_service)
):
    """
    Get all expired prescriptions
    """
    try:
        prescriptions = await prescription_service.get_expired_prescriptions(
            user_id=current_user.id
        )
        return prescriptions
        
    except Exception as e:
        logger.error(f"Error fetching expired prescriptions: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch expired prescriptions"
        )


@router.get("/{prescription_id}", response_model=PrescriptionWithMedicines)
async def get_prescription(
    prescription_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    prescription_service: PrescriptionService = Depends(get_prescription_service)
):
    """
    Get specific prescription by ID
    """
    try:
        prescription = await prescription_service.get_prescription_by_id(
            prescription_id=prescription_id,
            user_id=current_user.id
        )
        
        if not prescription:
            logger.warning(f"Prescription {prescription_id} not found for user {current_user.id}")
            raise PrescriptionNotFoundException(prescription_id)
        
        logger.debug(f"Prescription {prescription_id} fetched for user {current_user.id}")
        return prescription
        
    except PrescriptionNotFoundException:
        raise
        
    except Exception as e:
        logger.error(f"Error fetching prescription {prescription_id}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch prescription"
        )


@router.put("/{prescription_id}", response_model=PrescriptionWithMedicines)
async def update_prescription(
    prescription_id: int,
    prescription_update: PrescriptionUpdateWithMedicines,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    prescription_service: PrescriptionService = Depends(get_prescription_service)
):
    """
    Update prescription with optional medicines update
    """
    try:
        prescription = await prescription_service.update_prescription_with_medicines(
            prescription_id=prescription_id,
            user_id=current_user.id,
            prescription_update=prescription_update,
            medicines=prescription_update.medicines
        )
        
        logger.info(f"Prescription {prescription_id} updated for user {current_user.id}")
        return prescription
        
    except PrescriptionNotFoundException:
        raise
        
    except Exception as e:
        logger.error(f"Error updating prescription {prescription_id}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update prescription"
        )


@router.delete("/{prescription_id}")
async def delete_prescription(
    prescription_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    prescription_service: PrescriptionService = Depends(get_prescription_service)
):
    """
    Delete a prescription
    """
    try:
        success = await prescription_service.delete_prescription(
            prescription_id=prescription_id,
            user_id=current_user.id
        )
        
        if not success:
            logger.warning(f"Prescription deletion failed: Prescription {prescription_id} not found")
            raise PrescriptionNotFoundException(prescription_id)
        
        logger.info(f"Prescription {prescription_id} deleted for user {current_user.id}")
        return MessageResponse(
            message="Prescription deleted successfully",
            success=True
        )
        
    except PrescriptionNotFoundException:
        raise
        
    except Exception as e:
        logger.error(f"Error deleting prescription {prescription_id}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete prescription"
        )


@router.post("/{prescription_id}/medicines", response_model=PrescriptionMedicineResponse)
async def add_medicine_to_prescription(
    prescription_id: int,
    medicine_data: PrescriptionMedicineCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    prescription_service: PrescriptionService = Depends(get_prescription_service)
):
    """
    Add a medicine to an existing prescription
    """
    try:
        prescription_medicine = await prescription_service.add_medicine_to_prescription(
            prescription_id=prescription_id,
            user_id=current_user.id,
            medicine_data=medicine_data
        )
        
        logger.info(f"Medicine added to prescription {prescription_id}: {prescription_medicine.medicine_name}")
        return prescription_medicine
        
    except PrescriptionNotFoundException:
        raise
        
    except Exception as e:
        logger.error(f"Error adding medicine to prescription {prescription_id}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add medicine to prescription"
        )


@router.delete("/{prescription_id}/medicines/{prescription_medicine_id}")
async def remove_medicine_from_prescription(
    prescription_id: int,
    prescription_medicine_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    prescription_service: PrescriptionService = Depends(get_prescription_service)
):
    """
    Remove a medicine from a prescription
    """
    try:
        success = await prescription_service.remove_medicine_from_prescription(
            prescription_id=prescription_id,
            prescription_medicine_id=prescription_medicine_id,
            user_id=current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medicine not found in prescription"
            )
        
        logger.info(f"Medicine {prescription_medicine_id} removed from prescription {prescription_id}")
        return MessageResponse(
            message="Medicine removed from prescription successfully",
            success=True
        )
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Error removing medicine from prescription {prescription_id}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove medicine from prescription"
        )
