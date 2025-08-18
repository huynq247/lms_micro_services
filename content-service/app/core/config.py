from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    """Content Service settings with flexible configuration"""
    
    # Environment info
    environment: str = "development"
    service_name: str = "content-service"
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8002
    debug: bool = True
    allowed_hosts: List[str] = ["*"]
    
    # MongoDB configuration
    mongodb_url: str = "mongodb://admin:Mypassword123@113.161.118.17:27017/content_db?authSource=admin"
    mongodb_db_name: str = "content_db"
    
    # Auth Service integration
    auth_service_url: str = "http://localhost:8001"
    jwt_secret_key: str = "your-super-secret-jwt-key-content-service-2024"
    jwt_algorithm: str = "HS256"
    
    # URL validation settings
    max_image_size_mb: int = 10
    max_video_size_mb: int = 100
    allowed_image_formats: str = "jpg,jpeg,png,gif,webp"
    allowed_video_formats: str = "mp4,avi,mov,wmv,flv,webm"
    
    @property
    def image_formats_list(self) -> List[str]:
        return [fmt.strip() for fmt in self.allowed_image_formats.split(",")]
    
    @property
    def video_formats_list(self) -> List[str]:
        return [fmt.strip() for fmt in self.allowed_video_formats.split(",")]
    
    # Redis cache (for future scaling)
    redis_url: Optional[str] = "redis://admin:Mypassword123@113.161.118.17:26379/1"
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    # Request timeout settings
    request_timeout: int = 30
    url_validation_timeout: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False

def get_settings() -> Settings:
    """Factory function for settings"""
    return Settings()

settings = get_settings()
