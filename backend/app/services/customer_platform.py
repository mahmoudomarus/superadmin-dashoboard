from typing import List, Dict, Any, Optional
from app.services.platform_client import PlatformClient
from app.utils.logger import logger

class CustomerPlatformClient(PlatformClient):
    """Client for Customer AI Platform API"""
    
    def __init__(self, base_url: str, api_key: str):
        super().__init__("customer_platform", base_url, api_key)
    
    async def get_all_users(self) -> Dict[str, Any]:
        """Get all customer users"""
        return await self.get(
            "/api/users",
            cache_key="customer:users",
            cache_ttl=300
        )
    
    async def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get single user details"""
        return await self.get(
            f"/api/users/{user_id}",
            cache_key=f"customer:user:{user_id}",
            cache_ttl=300
        )
    
    async def get_all_bookings(
        self,
        page: int = 1,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get all customer bookings"""
        return await self.get(
            "/api/bookings",
            params={"page": page, "limit": limit},
            cache_key=f"customer:bookings:page:{page}",
            cache_ttl=60
        )
    
    async def get_ai_conversations(
        self,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get AI conversation history"""
        endpoint = "/api/conversations"
        cache_key = "customer:conversations"
        
        if user_id:
            endpoint += f"?user_id={user_id}"
            cache_key += f":user:{user_id}"
        
        return await self.get(
            endpoint,
            cache_key=cache_key,
            cache_ttl=60
        )
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Get customer platform analytics"""
        return await self.get(
            "/api/analytics",
            cache_key="customer:analytics",
            cache_ttl=600
        )

# Import redis_client at the end to avoid circular import
from app.core.redis import redis_client

