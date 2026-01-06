from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.database import get_db
from app.services.auth_service import AuthService


def get_auth_service(db: AsyncSession = None) -> AuthService:
    """Get auth service instance"""
    if db is None:
        # This is a fallback for cases where we need auth service without db
        # In practice, db should always be provided
        raise ValueError("Database session is required")
    return AuthService(db)


async def get_auth_service_dep(db: AsyncSession = Depends(get_db)) -> AuthService:
    """FastAPI dependency for auth service"""
    return AuthService(db)