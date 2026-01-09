from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging
from app.config import settings
from app.database import create_db_and_tables
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.medicines import router as medicines_router
from app.api.prescriptions import router as prescriptions_router
from app.api.reminders import router as reminders_router
from app.api.search import router as search_router
from app.core.exceptions import (
    AuthException, PermissionException, ValidationException,
    NotFoundException, ConflictException, BadRequestException
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Pillio API...")
    
    try:
        # Create database tables
        await create_db_and_tables()
        logger.info("Database tables created successfully")
        
        # Ensure upload directory exists
        settings.ensure_upload_dir_exists()
        logger.info("Upload directory ready")
        
        logger.info(f"Pillio API started successfully on {settings.host}:{settings.port}")
        
    except Exception as e:
        logger.error(f"Failed to start Pillio API: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Pillio API...")


# Create FastAPI application
app = FastAPI(
    title=settings.project_name,
    description="Medicine Management API - Track medications, schedules, and prescriptions",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(AuthException)
async def auth_exception_handler(request, exc: AuthException):
    logger.warning(f"Auth exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(PermissionException)
async def permission_exception_handler(request, exc: PermissionException):
    logger.warning(f"Permission exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(ValidationException)
async def validation_exception_handler(request, exc: ValidationException):
    logger.warning(f"Validation exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request, exc: NotFoundException):
    logger.warning(f"Not found exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(ConflictException)
async def conflict_exception_handler(request, exc: ConflictException):
    logger.warning(f"Conflict exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(BadRequestException)
async def bad_request_exception_handler(request, exc: BadRequestException):
    logger.warning(f"Bad request exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


# Include API routers
app.include_router(
    auth_router,
    prefix=f"{settings.api_v1_str}/auth",
    tags=["Authentication"]
)

app.include_router(
    users_router,
    prefix=f"{settings.api_v1_str}/users",
    tags=["Users"]
)

app.include_router(
    medicines_router,
    prefix=f"{settings.api_v1_str}/medicines",
    tags=["Medicines"]
)

app.include_router(
    prescriptions_router,
    prefix=f"{settings.api_v1_str}/prescriptions",
    tags=["Prescriptions"]
)

app.include_router(
    reminders_router,
    prefix=f"{settings.api_v1_str}/reminders",
    tags=["Reminders"]
)

app.include_router(
    search_router,
    prefix=f"{settings.api_v1_str}",
    tags=["Search"]
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.project_name,
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": f"Welcome to {settings.project_name} API",
        "version": "1.0.0",
        "docs": "/docs" if settings.debug else "Documentation disabled in production",
        "health": "/health"
    }


# Global exception handler for unexpected errors
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    logger.error(f"Unexpected error: {type(exc).__name__}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )
