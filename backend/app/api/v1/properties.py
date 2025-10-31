from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.dependencies import get_current_admin
from app.services.host_platform import HostPlatformClient
from app.config import settings
from app.core.supabase import get_supabase
from app.utils.logger import logger

router = APIRouter(prefix="/properties", tags=["properties"])

@router.get("")
async def list_properties(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    admin: dict = Depends(get_current_admin)
):
    """List all properties from Host Dashboard"""
    try:
        client = HostPlatformClient(
            settings.HOST_DASHBOARD_URL,
            settings.HOST_DASHBOARD_API_KEY
        )
        
        response = await client.get_all_properties(page=page, limit=limit, status=status)
        
        return {
            "success": True,
            "data": response.get("data", []),
            "total": response.get("total", 0),
            "page": page,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Failed to list properties: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{property_id}")
async def get_property(
    property_id: str,
    admin: dict = Depends(get_current_admin)
):
    """Get property details"""
    try:
        client = HostPlatformClient(
            settings.HOST_DASHBOARD_URL,
            settings.HOST_DASHBOARD_API_KEY
        )
        
        response = await client.get_property(property_id)
        
        return {
            "success": True,
            "data": response
        }
    except Exception as e:
        logger.error(f"Failed to get property: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{property_id}/status")
async def update_property_status(
    property_id: str,
    status: str,
    admin: dict = Depends(get_current_admin)
):
    """Update property status (suspend/activate)"""
    try:
        client = HostPlatformClient(
            settings.HOST_DASHBOARD_URL,
            settings.HOST_DASHBOARD_API_KEY
        )
        
        response = await client.update_property_status(property_id, status)
        
        # Log admin action
        supabase = get_supabase()
        supabase.table("admin_audit_log").insert({
            "admin_user_id": admin["id"],
            "action_type": "property_status_update",
            "target_entity_type": "property",
            "target_entity_id": property_id,
            "action_details": {"new_status": status}
        }).execute()
        
        return {
            "success": True,
            "message": f"Property status updated to {status}",
            "data": response
        }
    except Exception as e:
        logger.error(f"Failed to update property status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

