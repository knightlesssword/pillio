from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import AsyncGenerator
from app.config import settings

# Create async engine
engine = create_async_engine(
    settings.get_database_url(),
    echo=settings.debug,
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Create declarative base for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session
    Usage: 
    @app.get("/endpoint")
    async def endpoint(db: AsyncSession = Depends(get_db)):
        # Your code here
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_db_and_tables():
    """
    Create all database tables
    This should be called at startup
    """
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def drop_db_and_tables():
    """
    Drop all database tables
    Use with caution - this will delete all data
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)