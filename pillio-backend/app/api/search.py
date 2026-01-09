from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
import logging
from pydantic import BaseModel
from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.medicine import Medicine
from app.models.reminder import Reminder
from app.models.prescription import Prescription

logger = logging.getLogger(__name__)

router = APIRouter()


# Response schemas
class SearchResultItem(BaseModel):
    id: str
    type: str
    title: str
    subtitle: str
    route: str


class SearchResponse(BaseModel):
    results: list[SearchResultItem]
    total: int


@router.get("/search", response_model=SearchResponse)
async def universal_search(
    q: str = Query(..., min_length=1, description="Search query"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Universal search across medicines, reminders, and prescriptions.
    """
    try:
        search_term = f"%{q.lower()}%"
        results: list[SearchResultItem] = []

        # Search medicines
        medicines_query = select(Medicine).where(
            Medicine.user_id == current_user.id,
            or_(
                func.lower(Medicine.name).like(search_term),
                func.lower(Medicine.generic_name).like(search_term),
            )
        ).limit(5)

        medicines_result = await db.execute(medicines_query)
        medicines = medicines_result.scalars().all()

        for medicine in medicines:
            results.append(SearchResultItem(
                id=str(medicine.id),
                type="medicine",
                title=medicine.name,
                subtitle=f"{medicine.dosage} • {medicine.form} • Stock: {medicine.current_stock}",
                # route=f"/medicines?edit={medicine.id}"
                route=f"/medicines"
            ))

        # Search reminders (join with Medicine to get medicine name)
        reminders_query = (
            select(Reminder)
            .options(selectinload(Reminder.medicine))
            .join(Medicine, Reminder.medicine_id == Medicine.id)
            .where(
                Reminder.user_id == current_user.id,
                or_(
                    func.lower(Medicine.name).like(search_term),
                    func.lower(Reminder.notes).like(search_term),
                )
            )
            .limit(5)
        )

        reminders_result = await db.execute(reminders_query)
        reminders = reminders_result.scalars().all()

        for reminder in reminders:
            medicine_name = reminder.medicine.name if reminder.medicine else "Unknown"
            results.append(SearchResultItem(
                id=str(reminder.id),
                type="reminder",
                title=medicine_name,
                subtitle=f"{reminder.reminder_time} • {reminder.frequency}",
                route="/reminders"
            ))

        # Search prescriptions
        prescriptions_query = select(Prescription).where(
            Prescription.user_id == current_user.id,
            or_(
                func.lower(Prescription.doctor_name).like(search_term),
                func.lower(Prescription.notes).like(search_term),
            )
        ).limit(5)

        prescriptions_result = await db.execute(prescriptions_query)
        prescriptions = prescriptions_result.scalars().all()

        for prescription in prescriptions:
            results.append(SearchResultItem(
                id=str(prescription.id),
                type="prescription",
                title=f"Prescription from Dr. {prescription.doctor_name}",
                subtitle=f"Date: {prescription.prescription_date}",
                route=f"/prescriptions/" #{prescription.id}"
            ))

        logger.debug(f"Universal search for '{q}' returned {len(results)} results for user {current_user.id}")

        return SearchResponse(
            results=results,
            total=len(results)
        )

    except Exception as e:
        logger.error(f"Error in universal search: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )
