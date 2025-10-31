from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_admin
from app.config import settings
from app.utils.logger import logger

router = APIRouter(prefix="/hosts", tags=["hosts"])

@router.get("")
async def list_hosts(
    admin: dict = Depends(get_current_admin)
):
    """List all hosts from Host Dashboard Supabase"""
    try:
        from app.services.host_supabase import HostSupabaseClient
        
        client = HostSupabaseClient()
        hosts = await client.get_all_users()
        
        return {
            "success": True,
            "data": hosts,
            "total": len(hosts)
        }
    except ValueError as e:
        return {
            "success": False,
            "error": "Host Dashboard Supabase credentials not configured",
            "message": "Set HOST_DASHBOARD_SUPABASE_URL and HOST_DASHBOARD_SUPABASE_KEY in Render env vars"
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
        from app.services.host_supabase import HostSupabaseClient
        
        client = HostSupabaseClient()
        host = await client.get_user(host_id)
        
        if not host:
            raise HTTPException(status_code=404, detail="Host not found")
        
        return {
            "success": True,
            "data": host
        }
    except ValueError as e:
        return {
            "success": False,
            "error": "Host Dashboard Supabase credentials not configured"
        }
    except Exception as e:
        logger.error(f"Failed to get host: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{host_id}/status")
async def update_host_status(
    host_id: str,
    is_active: bool,
    admin: dict = Depends(get_current_admin)
):
    """Update host active status"""
    try:
        from app.services.host_supabase import HostSupabaseClient
        from app.core.supabase import get_supabase
        
        client = HostSupabaseClient()
        host = await client.update_user_status(host_id, is_active)
        
        # Log admin action
        supabase = get_supabase()
        supabase.table("admin_audit_log").insert({
            "admin_user_id": admin["id"],
            "action_type": "host_status_update",
            "target_entity_type": "host",
            "target_entity_id": host_id,
            "action_details": {"is_active": is_active}
        }).execute()
        
        return {
            "success": True,
            "message": f"Host status updated to {'active' if is_active else 'inactive'}",
            "data": host
        }
    except Exception as e:
        logger.error(f"Failed to update host status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{host_id}/payouts")
async def get_host_payouts(
    host_id: str,
    admin: dict = Depends(get_current_admin)
):
    """Get host payouts"""
    try:
        from app.services.host_platform import HostPlatformClient
        
        client = HostPlatformClient(
            settings.HOST_DASHBOARD_URL,
            settings.HOST_DASHBOARD_API_KEY
        )
        
        response = await client.get_host_payouts(host_id)
        
        return {
            "success": True,
            "data": response
        }
    except Exception as e:
        logger.error(f"Failed to get host payouts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

