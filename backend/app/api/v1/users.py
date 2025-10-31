from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from app.models.schemas import (
    UnifiedUserResponse,
    UpdateUserStatusRequest,
    SuccessResponse,
    PaginatedResponse
)
from app.dependencies import get_current_admin
from app.core.supabase import get_supabase
from app.utils.logger import logger

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=PaginatedResponse)
async def list_users(
    platform: Optional[str] = Query(None),
    user_type: Optional[str] = Query(None),
    account_status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    admin: dict = Depends(get_current_admin)
):
    """List all users across platforms"""
    supabase = get_supabase()
    
    try:
        # Build query
        query = supabase.table("unified_users").select("*", count="exact")
        
        # Apply filters
        if platform:
            query = query.eq("platform_id", platform)
        if user_type:
            query = query.eq("user_type", user_type)
        if account_status:
            query = query.eq("account_status", account_status)
        if search:
            query = query.or_(f"email.ilike.%{search}%,full_name.ilike.%{search}%")
        
        # Pagination
        start = (page - 1) * limit
        end = start + limit - 1
        
        response = query.range(start, end).execute()
        
        total = response.count if hasattr(response, 'count') else len(response.data)
        total_pages = (total + limit - 1) // limit
        
        return PaginatedResponse(
            data=response.data,
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages
        )
    
    except Exception as e:
        logger.error(f"Failed to list users: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve users")

@router.get("/{user_id}")
async def get_user(
    user_id: str,
    admin: dict = Depends(get_current_admin)
):
    """Get user details with cross-platform data"""
    supabase = get_supabase()
    
    try:
        # Get user from unified table
        response = supabase.table("unified_users").select("*").eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = response.data[0]
        
        # Get user's properties
        properties_response = supabase.table("unified_properties").select("*").eq(
            "owner_user_id", user_id
        ).execute()
        
        # Get user's bookings
        bookings_response = supabase.table("unified_bookings").select("*").or_(
            f"guest_user_id.eq.{user_id},host_user_id.eq.{user_id}"
        ).execute()
        
        return SuccessResponse(
            message="User retrieved successfully",
            data={
                "user": user,
                "properties": properties_response.data,
                "bookings": bookings_response.data,
                "stats": {
                    "total_properties": len(properties_response.data),
                    "total_bookings": len(bookings_response.data)
                }
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user")

@router.patch("/{user_id}/status")
async def update_user_status(
    user_id: str,
    request: UpdateUserStatusRequest,
    admin: dict = Depends(get_current_admin)
):
    """Update user account status (suspend, ban, activate)"""
    supabase = get_supabase()
    
    try:
        # Update user status
        response = supabase.table("unified_users").update({
            "account_status": request.status.value
        }).eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Log admin action
        supabase.table("admin_audit_log").insert({
            "admin_user_id": admin["id"],
            "action_type": "user_status_update",
            "target_entity_type": "user",
            "target_entity_id": user_id,
            "action_details": {
                "new_status": request.status.value,
                "reason": request.reason
            }
        }).execute()
        
        return SuccessResponse(
            message=f"User status updated to {request.status.value}",
            data=response.data[0]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user status")

