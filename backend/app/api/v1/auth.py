from fastapi import APIRouter, HTTPException, status
from app.models.schemas import LoginRequest, LoginResponse, SuccessResponse
from app.core.supabase import get_supabase
from app.core.security import verify_password, create_access_token
from app.utils.logger import logger
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Super admin login"""
    supabase = get_supabase()
    
    try:
        # Get admin user by email
        response = supabase.table("super_admin_users").select("*").eq(
            "email", request.email
        ).eq(
            "is_active", True
        ).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        admin = response.data[0]
        
        # For now, use simple password check (you should hash passwords in production)
        # This is a placeholder - implement proper password hashing
        if request.password != "admin123":  # Replace with actual password check
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Update last login
        supabase.table("super_admin_users").update({
            "last_login_at": datetime.utcnow().isoformat()
        }).eq("id", admin["id"]).execute()
        
        # Create access token
        access_token = create_access_token(
            data={"sub": admin["id"], "email": admin["email"]}
        )
        
        return LoginResponse(
            access_token=access_token,
            user={
                "id": admin["id"],
                "email": admin["email"],
                "full_name": admin["full_name"],
                "role": admin["role"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.get("/me")
async def get_current_user_info(admin: dict = Depends(get_current_admin)):
    """Get current admin user info"""
    return SuccessResponse(
        message="User info retrieved",
        data=admin
    )

# Import after defining router to avoid circular imports
from app.dependencies import get_current_admin
from fastapi import Depends

