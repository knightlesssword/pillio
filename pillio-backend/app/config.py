from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pillio"
    
    # Security
    secret_key: str = "your-super-secret-jwt-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # API
    api_v1_str: str = "/api/v1"
    project_name: str = "Pillio"
    debug: bool = True
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:8080"]
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # File Upload
    upload_dir: str = "uploads"
    max_file_size: int = 5242880  # 5MB
    allowed_file_types: str = "jpg,jpeg,png,pdf"
    allowed_image_types: str = "jpg,jpeg,png"
    
    # Notifications
    reminder_check_interval: int = 60  # seconds
    low_stock_threshold: int = 5
    
    # Email (optional)
    smtp_tls: bool = True
    smtp_port: int = 587
    smtp_host: str = "smtp.gmail.com"
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    emails_from_email: Optional[str] = None
    emails_from_name: str = "Pillio"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def get_database_url(self) -> str:
        """Get database URL for async operations"""
        return self.database_url
    
    def get_allowed_file_extensions(self) -> List[str]:
        """Get list of allowed file extensions"""
        return [ext.strip() for ext in self.allowed_file_types.split(",")]
    
    def get_allowed_image_extensions(self) -> List[str]:
        """Get list of allowed image extensions"""
        return [ext.strip() for ext in self.allowed_image_types.split(",")]
    
    def ensure_upload_dir_exists(self) -> None:
        """Create upload directory if it doesn't exist"""
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)


# Create a global instance
settings = Settings()