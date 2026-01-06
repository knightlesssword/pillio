from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import AsyncGenerator
import logging
from sqlalchemy.exc import SQLAlchemyError
from app.config import settings

logger = logging.getLogger(__name__)

# Create async engine
try:
    engine = create_async_engine(
        settings.get_database_url(),
        echo=settings.debug,
        future=True,
    )
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

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
            logger.debug("Database session created")
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            try:
                await session.close()
                logger.debug("Database session closed")
            except Exception as e:
                logger.error(f"Error closing database session: {e}")


async def create_db_and_tables():
    """
    Create all database tables
    This should be called at startup
    """
    logger.info("Creating database tables...")
    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except SQLAlchemyError as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating database tables: {e}")
        raise


async def drop_db_and_tables():
    """
    Drop all database tables
    Use with caution - this will delete all data
    """
    logger.warning("Dropping all database tables...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("Database tables dropped successfully")
    except SQLAlchemyError as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error dropping database tables: {e}")
        raise
