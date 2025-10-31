from typing import List, Dict, Any, Optional
from app.services.platform_client import PlatformClient
from app.utils.logger import logger

class AgentPlatformClient(PlatformClient):
    """Client for Real Estate Agent Dashboard API"""
    
    def __init__(self, base_url: str, api_key: str):
        super().__init__("agent_dashboard", base_url, api_key)
    
    async def get_pending_verifications(self) -> Dict[str, Any]:
        """Get all users pending verification"""
        return await self.get(
            "/api/admin/verification/pending",
            cache_key="agent:verification:pending",
            cache_ttl=60
        )
    
    async def get_user_verification_details(self, user_id: str) -> Dict[str, Any]:
        """Get detailed verification info for a user"""
        return await self.get(
            f"/api/admin/verification/user/{user_id}",
            cache_key=f"agent:verification:user:{user_id}",
            cache_ttl=60
        )
    
    async def approve_agent(self, user_id: str, notes: str, admin_id: str) -> Dict[str, Any]:
        """Approve an agent"""
        # Invalidate cache
        await redis_client.delete(f"agent:verification:user:{user_id}")
        await redis_client.delete("agent:verification:pending")
        await redis_client.delete("agent:verification:statistics")
        
        return await self.post(
            f"/api/admin/verification/user/{user_id}/action",
            json={
                "action": "approve",
                "notes": notes,
                "admin_id": admin_id
            }
        )
    
    async def reject_agent(
        self, 
        user_id: str, 
        reason: str, 
        notes: str,
        admin_id: str
    ) -> Dict[str, Any]:
        """Reject an agent"""
        # Invalidate cache
        await redis_client.delete(f"agent:verification:user:{user_id}")
        await redis_client.delete("agent:verification:pending")
        await redis_client.delete("agent:verification:statistics")
        
        return await self.post(
            f"/api/admin/verification/user/{user_id}/action",
            json={
                "action": "reject",
                "rejection_reason": reason,
                "notes": notes,
                "admin_id": admin_id
            }
        )
    
    async def request_resubmission(
        self, 
        user_id: str, 
        reason: str,
        admin_id: str
    ) -> Dict[str, Any]:
        """Request document resubmission"""
        # Invalidate cache
        await redis_client.delete(f"agent:verification:user:{user_id}")
        await redis_client.delete("agent:verification:pending")
        
        return await self.post(
            f"/api/admin/verification/user/{user_id}/action",
            json={
                "action": "request_resubmission",
                "notes": reason,
                "admin_id": admin_id
            }
        )
    
    async def get_verification_statistics(self) -> Dict[str, Any]:
        """Get verification statistics"""
        return await self.get(
            "/api/admin/verification/statistics",
            cache_key="agent:verification:statistics",
            cache_ttl=300
        )
    
    async def get_audit_log(self, user_id: str) -> Dict[str, Any]:
        """Get verification audit log for a user"""
        return await self.get(
            f"/api/admin/verification/audit-log/{user_id}",
            cache_key=f"agent:audit:{user_id}",
            cache_ttl=300
        )
    
    async def get_all_properties(
        self, 
        page: int = 1, 
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get all agent properties"""
        return await self.get(
            "/api/properties",
            params={"page": page, "limit": limit},
            cache_key=f"agent:properties:page:{page}",
            cache_ttl=300
        )
    
    async def get_all_agents(self) -> Dict[str, Any]:
        """Get all registered agents"""
        return await self.get(
            "/api/admin/agents",
            cache_key="agent:agents:all",
            cache_ttl=300
        )

# Import redis_client at the end to avoid circular import
from app.core.redis import redis_client

