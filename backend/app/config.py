from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Krib Super Admin"
    VERSION: str = "1.0.0"
    
    # Database
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    DATABASE_URL: Optional[str] = None
    
    # Redis
    REDIS_URL: str
    
    # Security
    SECRET_KEY: str
    ENCRYPTION_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Platform APIs - Host Dashboard
    HOST_DASHBOARD_URL: str = "https://krib-host-dahsboard-backend.onrender.com"
    HOST_DASHBOARD_API_KEY: str
    HOST_DASHBOARD_SUPABASE_URL: Optional[str] = None
    HOST_DASHBOARD_SUPABASE_KEY: Optional[str] = None
    
    # Platform APIs - Agent Dashboard
    AGENT_DASHBOARD_URL: str = "https://krib-real-estate-agent-dahaboard-backend.onrender.com"
    AGENT_DASHBOARD_API_KEY: str
    AGENT_DASHBOARD_SUPABASE_URL: str = "https://lnhhdaiyhphkmhikcagj.supabase.co"
    AGENT_DASHBOARD_SUPABASE_KEY: str
    
    # Platform APIs - Customer Platform
    CUSTOMER_PLATFORM_URL: str = "https://krib-backend.onrender.com"
    CUSTOMER_PLATFORM_API_KEY: str
    CUSTOMER_PLATFORM_SUPABASE_URL: Optional[str] = None
    CUSTOMER_PLATFORM_SUPABASE_KEY: Optional[str] = None
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

