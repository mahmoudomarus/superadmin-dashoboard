from typing import List, Dict, Any, Optional
from app.services.platform_client import PlatformClient
from app.utils.logger import logger

class HostPlatformClient(PlatformClient):
    """Client for Host Dashboard API"""
    
    def __init__(self, base_url: str, api_key: str):
        super().__init__("host_dashboard", base_url, api_key)
    
    async def get_all_properties(
        self, 
        page: int = 1, 
        limit: int = 100,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get all properties from host dashboard"""
        params = {"page": page, "limit": limit}
        if status:
            params["status"] = status
        
        return await self.get(
            "/api/v1/properties",
            params=params,
            cache_key=f"host:properties:page:{page}:status:{status}",
            cache_ttl=300
        )
    
    async def get_property(self, property_id: str) -> Dict[str, Any]:
        """Get single property details"""
        return await self.get(
            f"/api/v1/properties/{property_id}",
            cache_key=f"host:property:{property_id}",
            cache_ttl=300
        )
    
    async def get_all_bookings(
        self,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get all bookings"""
        params = {"page": page, "limit": limit}
        if status:
            params["status"] = status
        
        return await self.get(
            "/api/v1/bookings",
            params=params,
            cache_key=f"host:bookings:page:{page}:status:{status}",
            cache_ttl=60
        )
    
    async def get_booking(self, booking_id: str) -> Dict[str, Any]:
        """Get single booking details"""
        return await self.get(
            f"/api/v1/bookings/{booking_id}",
            cache_key=f"host:booking:{booking_id}",
            cache_ttl=60
        )
    
    async def cancel_booking(self, booking_id: str, reason: str) -> Dict[str, Any]:
        """Cancel a booking"""
        # Invalidate cache
        await redis_client.delete(f"host:booking:{booking_id}")
        await redis_client.delete_pattern("host:bookings:*")
        
        return await self.delete(
            f"/api/v1/bookings/{booking_id}",
            json={"reason": reason}
        )
    
    async def update_property_status(
        self, 
        property_id: str, 
        status: str
    ) -> Dict[str, Any]:
        """Update property status"""
        # Invalidate cache
        await redis_client.delete(f"host:property:{property_id}")
        await redis_client.delete_pattern("host:properties:*")
        
        return await self.patch(
            f"/api/v1/properties/{property_id}",
            json={"status": status}
        )
    
    async def get_host_users(self) -> Dict[str, Any]:
        """Get all host users"""
        return await self.get(
            "/api/v1/users",
            cache_key="host:users",
            cache_ttl=300
        )
    
    async def get_analytics(self, host_id: Optional[str] = None) -> Dict[str, Any]:
        """Get host analytics"""
        endpoint = "/api/v1/analytics/admin/overview"
        if host_id:
            endpoint = f"/api/v1/analytics/host/dashboard?host_id={host_id}"
        
        return await self.get(
            endpoint,
            cache_key=f"host:analytics:{host_id or 'all'}",
            cache_ttl=600
        )

# Import redis_client at the end to avoid circular import
from app.core.redis import redis_client

