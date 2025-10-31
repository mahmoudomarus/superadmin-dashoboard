from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.schemas import (
    VerificationQueueItem,
    ApproveVerificationRequest,
    RejectVerificationRequest,
    RequestResubmissionRequest,
    SuccessResponse
)
from app.dependencies import get_current_admin
from app.core.supabase import get_supabase
from app.services.agent_platform import AgentPlatformClient
from app.config import settings
from app.utils.logger import logger

router = APIRouter(prefix="/verification", tags=["verification"])

@router.get("/queue", response_model=List[VerificationQueueItem])
async def get_verification_queue(
    status: str = "pending",
    admin: dict = Depends(get_current_admin)
):
    """Get verification queue"""
    supabase = get_supabase()
    
    try:
        query = supabase.table("verification_queue").select("*")
        
        if status != "all":
            query = query.eq("status", status)
        
        response = query.order("created_at", desc=True).execute()
        
        return response.data
    
    except Exception as e:
        logger.error(f"Failed to get verification queue: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve verification queue")

@router.get("/{verification_id}")
async def get_verification_details(
    verification_id: str,
    admin: dict = Depends(get_current_admin)
):
    """Get detailed verification information"""
    supabase = get_supabase()
    
    try:
        # Get verification record
        response = supabase.table("verification_queue").select("*").eq(
            "id", verification_id
        ).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Verification not found")
        
        verification = response.data[0]
        
        # Get user details
        user_response = supabase.table("unified_users").select("*").eq(
            "id", verification["user_id"]
        ).execute()
        
        # Get platform details
        platform_response = supabase.table("platforms").select("*").eq(
            "id", verification["platform_id"]
        ).execute()
        
        platform = platform_response.data[0] if platform_response.data else None
        
        # If agent platform, fetch additional details
        if platform and platform["name"] == "agent_dashboard":
            try:
                agent_client = AgentPlatformClient(
                    platform["api_base_url"],
                    platform["api_key"]
                )
                platform_details = await agent_client.get_user_verification_details(
                    verification["platform_user_id"]
                )
            except Exception as e:
                logger.error(f"Failed to fetch platform details: {e}")
                platform_details = None
        else:
            platform_details = None
        
        return SuccessResponse(
            message="Verification details retrieved",
            data={
                "verification": verification,
                "user": user_response.data[0] if user_response.data else None,
                "platform": platform,
                "platform_details": platform_details
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get verification details: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve verification details")

@router.post("/{verification_id}/approve")
async def approve_verification(
    verification_id: str,
    request: ApproveVerificationRequest,
    admin: dict = Depends(get_current_admin)
):
    """Approve agent/host verification"""
    supabase = get_supabase()
    
    try:
        # Get verification record
        response = supabase.table("verification_queue").select("*").eq(
            "id", verification_id
        ).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Verification not found")
        
        verification = response.data[0]
        
        # Get platform details
        platform_response = supabase.table("platforms").select("*").eq(
            "id", verification["platform_id"]
        ).execute()
        
        platform = platform_response.data[0]
        
        # Approve on source platform
        if platform["name"] == "agent_dashboard":
            agent_client = AgentPlatformClient(
                platform["api_base_url"],
                platform["api_key"]
            )
            await agent_client.approve_agent(
                verification["platform_user_id"],
                request.notes,
                admin["id"]
            )
        
        # Update verification queue
        supabase.table("verification_queue").update({
            "status": "approved",
            "reviewed_by": admin["id"],
            "reviewed_at": "NOW()",
            "review_notes": request.notes
        }).eq("id", verification_id).execute()
        
        # Update unified user
        supabase.table("unified_users").update({
            "verification_status": "approved",
            "account_status": "active"
        }).eq("id", verification["user_id"]).execute()
        
        # Log admin action
        supabase.table("admin_audit_log").insert({
            "admin_user_id": admin["id"],
            "action_type": "verification_approved",
            "target_platform": verification["platform_id"],
            "target_entity_type": "verification",
            "target_entity_id": verification_id,
            "action_details": {"notes": request.notes}
        }).execute()
        
        return SuccessResponse(
            message="Verification approved successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve verification: {e}")
        raise HTTPException(status_code=500, detail="Failed to approve verification")

@router.post("/{verification_id}/reject")
async def reject_verification(
    verification_id: str,
    request: RejectVerificationRequest,
    admin: dict = Depends(get_current_admin)
):
    """Reject agent/host verification"""
    supabase = get_supabase()
    
    try:
        # Get verification record
        response = supabase.table("verification_queue").select("*").eq(
            "id", verification_id
        ).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Verification not found")
        
        verification = response.data[0]
        
        # Get platform details
        platform_response = supabase.table("platforms").select("*").eq(
            "id", verification["platform_id"]
        ).execute()
        
        platform = platform_response.data[0]
        
        # Reject on source platform
        if platform["name"] == "agent_dashboard":
            agent_client = AgentPlatformClient(
                platform["api_base_url"],
                platform["api_key"]
            )
            await agent_client.reject_agent(
                verification["platform_user_id"],
                request.reason,
                request.notes or "",
                admin["id"]
            )
        
        # Update verification queue
        supabase.table("verification_queue").update({
            "status": "rejected",
            "reviewed_by": admin["id"],
            "reviewed_at": "NOW()",
            "review_notes": request.notes
        }).eq("id", verification_id).execute()
        
        # Update unified user
        supabase.table("unified_users").update({
            "verification_status": "rejected",
            "account_status": "suspended"
        }).eq("id", verification["user_id"]).execute()
        
        # Log admin action
        supabase.table("admin_audit_log").insert({
            "admin_user_id": admin["id"],
            "action_type": "verification_rejected",
            "target_platform": verification["platform_id"],
            "target_entity_type": "verification",
            "target_entity_id": verification_id,
            "action_details": {
                "reason": request.reason,
                "notes": request.notes
            }
        }).execute()
        
        return SuccessResponse(
            message="Verification rejected"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reject verification: {e}")
        raise HTTPException(status_code=500, detail="Failed to reject verification")

@router.get("/statistics")
async def get_verification_statistics(
    admin: dict = Depends(get_current_admin)
):
    """Get verification statistics"""
    supabase = get_supabase()
    
    try:
        # Get counts by status
        response = supabase.table("verification_queue").select("status").execute()
        
        stats = {
            "total": len(response.data),
            "pending": 0,
            "in_review": 0,
            "approved": 0,
            "rejected": 0
        }
        
        for item in response.data:
            status = item.get("status", "pending")
            if status in stats:
                stats[status] += 1
        
        return SuccessResponse(
            message="Statistics retrieved",
            data=stats
        )
    
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")

