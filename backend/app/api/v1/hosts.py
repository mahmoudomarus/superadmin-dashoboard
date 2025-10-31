from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_admin
from app.core.supabase import get_supabase
from app.config import settings
from app.utils.logger import logger

router = APIRouter(prefix="/hosts", tags=["hosts"])

@router.get("")
async def list_hosts(
    admin: dict = Depends(get_current_admin)
):
    """List all hosts from Host Dashboard Supabase"""
    try:
        supabase = get_supabase()
        
        # This will use super admin's own Supabase
        # For Host Dashboard data, need direct Supabase connection
        # Will implement after getting HOST_DASHBOARD_SUPABASE credentials
        
        return {
            "success": True,
            "message": "Host list endpoint - requires HOST_DASHBOARD_SUPABASE_URL and KEY",
            "data": []
        }
    except Exception as e:
        logger.error(f"Failed to list hosts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{host_id}")
async def get_host(
    host_id: str,
    admin: dict = Depends(get_current_admin)
):
    """Get host details"""
    try:
        # Will implement with direct Supabase connection
        return {
            "success": True,
            "message": "Host details endpoint - requires HOST_DASHBOARD_SUPABASE_URL and KEY",
            "data": {}
        }
    except Exception as e:
        logger.error(f"Failed to get host: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{host_id}/analytics")
async def get_host_analytics(
    host_id: str,
    admin: dict = Depends(get_current_admin)
):
    """Get host analytics"""
    try:
        from app.services.host_platform import HostPlatformClient
        
        client = HostPlatformClient(
            settings.HOST_DASHBOARD_URL,
            settings.HOST_DASHBOARD_API_KEY
        )
        
        response = await client.get_analytics(host_id)
        
        return {
            "success": True,
            "data": response
        }
    except Exception as e:
        logger.error(f"Failed to get host analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

