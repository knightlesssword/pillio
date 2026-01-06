from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.database import get_db
from app.services.auth_service import AuthService


async def get_auth_service_dep(db: AsyncSession = Depends(get_db)) -> AuthService:
    """FastAPI dependency for auth service"""
    return AuthService(db)
