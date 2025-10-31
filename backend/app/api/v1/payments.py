from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_admin
from app.services.host_platform import HostPlatformClient
from app.config import settings
from app.core.supabase import get_supabase
from app.utils.logger import logger
from pydantic import BaseModel

router = APIRouter(prefix="/payments", tags=["payments"])

class RefundRequest(BaseModel):
    booking_id: str
    amount: float
    reason: str

@router.post("/refund")
async def refund_payment(
    refund: RefundRequest,
    admin: dict = Depends(get_current_admin)
):
    """Issue a refund"""
    try:
        client = HostPlatformClient(
            settings.HOST_DASHBOARD_URL,
            settings.HOST_DASHBOARD_API_KEY
        )
        
        response = await client.refund_payment(
            refund.booking_id,
            refund.amount,
            refund.reason
        )
        
        # Log admin action
        supabase = get_supabase()
        supabase.table("admin_audit_log").insert({
            "admin_user_id": admin["id"],
            "action_type": "payment_refunded",
            "target_entity_type": "booking",
            "target_entity_id": refund.booking_id,
            "action_details": {
                "amount": refund.amount,
                "reason": refund.reason
            }
        }).execute()
        
        return {
            "success": True,
            "message": "Refund processed",
            "data": response
        }
    except Exception as e:
        logger.error(f"Failed to process refund: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payouts")
async def list_payouts(
    status: str = None,
    admin: dict = Depends(get_current_admin)
):
    """List all payouts"""
    try:
        from app.services.host_supabase import HostSupabaseClient
        
        client = HostSupabaseClient()
        payouts = await client.get_all_payouts(status)
        
        return {
            "success": True,
            "data": payouts,
            "total": len(payouts)
        }
    except ValueError as e:
        return {
            "success": False,
            "error": "Host Dashboard Supabase credentials not configured"
        }
    except Exception as e:
        logger.error(f"Failed to list payouts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events")
async def list_stripe_events(
    limit: int = 100,
    admin: dict = Depends(get_current_admin)
):
    """List Stripe webhook events"""
    try:
        from app.services.host_supabase import HostSupabaseClient
        
        client = HostSupabaseClient()
        events = await client.get_stripe_events(limit)
        
        return {
            "success": True,
            "data": events,
            "total": len(events)
        }
    except ValueError as e:
        return {
            "success": False,
            "error": "Host Dashboard Supabase credentials not configured"
        }
    except Exception as e:
        logger.error(f"Failed to list Stripe events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

