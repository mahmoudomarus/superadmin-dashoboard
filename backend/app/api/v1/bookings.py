from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.dependencies import get_current_admin
from app.services.host_platform import HostPlatformClient
from app.config import settings
from app.core.supabase import get_supabase
from app.utils.logger import logger

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.get("")
async def list_bookings(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    admin: dict = Depends(get_current_admin)
):
    """List all bookings from Host Dashboard"""
    try:
        client = HostPlatformClient(
            settings.HOST_DASHBOARD_URL,
            settings.HOST_DASHBOARD_API_KEY
        )
        
        response = await client.get_all_bookings(status=status, page=page, limit=limit)
        
        return {
            "success": True,
            "data": response.get("data", []),
            "total": response.get("total", 0),
            "page": page,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Failed to list bookings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{booking_id}")
async def get_booking(
    booking_id: str,
    admin: dict = Depends(get_current_admin)
):
    """Get booking details"""
    try:
        client = HostPlatformClient(
            settings.HOST_DASHBOARD_URL,
            settings.HOST_DASHBOARD_API_KEY
        )
        
        response = await client.get_booking(booking_id)
        
        return {
            "success": True,
            "data": response
        }
    except Exception as e:
        logger.error(f"Failed to get booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{booking_id}/cancel")
async def cancel_booking(
    booking_id: str,
    reason: str,
    admin: dict = Depends(get_current_admin)
):
    """Cancel a booking"""
    try:
        client = HostPlatformClient(
            settings.HOST_DASHBOARD_URL,
            settings.HOST_DASHBOARD_API_KEY
        )
        
        response = await client.cancel_booking(booking_id, reason)
        
        # Log admin action
        supabase = get_supabase()
        supabase.table("admin_audit_log").insert({
            "admin_user_id": admin["id"],
            "action_type": "booking_cancelled",
            "target_entity_type": "booking",
            "target_entity_id": booking_id,
            "action_details": {"reason": reason}
        }).execute()
        
        return {
            "success": True,
            "message": "Booking cancelled",
            "data": response
        }
    except Exception as e:
        logger.error(f"Failed to cancel booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))

