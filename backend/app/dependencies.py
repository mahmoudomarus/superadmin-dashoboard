from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_access_token
from app.core.supabase import get_supabase
from app.utils.logger import logger

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    
    # Decode token
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    return {"id": user_id, "email": payload.get("email")}

async def get_current_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Verify user is a super admin"""
    supabase = get_supabase()
    
    # Get admin details
    response = supabase.table("super_admin_users").select("*").eq(
        "id", current_user["id"]
    ).eq(
        "is_active", True
    ).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    admin = response.data[0]
    return {
        "id": admin["id"],
        "email": admin["email"],
        "role": admin["role"],
        "permissions": admin.get("permissions", {})
    }

async def require_permission(permission: str):
    """Dependency to require specific permission"""
    async def permission_checker(admin: dict = Depends(get_current_admin)):
        # Super admins have all permissions
        if admin["role"] == "super_admin":
            return admin
        
        # Check specific permission
        permissions = admin.get("permissions", {})
        if not permissions.get(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        
        return admin
    
    return permission_checker

