from typing import Optional, Dict, Any, List
import httpx
from app.core.redis import redis_client
from app.utils.logger import logger

class PlatformClient:
    """Base class for platform API clients"""
    
    def __init__(self, name: str, base_url: str, api_key: str):
        self.name = name
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0,
            follow_redirects=True
        )
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        cache_key: Optional[str] = None,
        cache_ttl: int = 300,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request with caching"""
        
        # Check cache for GET requests
        if cache_key and method.upper() == "GET":
            cached = await redis_client.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for {cache_key}")
                return cached
        
        # Make request
        try:
            url = endpoint if endpoint.startswith('http') else f"{self.base_url}{endpoint}"
            logger.info(f"{method} {url}")
            
            response = await self.client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            data = response.json()
            
            # Cache successful GET requests
            if cache_key and method.upper() == "GET":
                await redis_client.set(cache_key, data, ex=cache_ttl)
            
            return data
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error for {self.name} - {endpoint}: {e.response.status_code} {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Request failed for {self.name} - {endpoint}: {str(e)}")
            raise
    
    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """GET request"""
        return await self._request("GET", endpoint, **kwargs)
    
    async def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """POST request"""
        return await self._request("POST", endpoint, **kwargs)
    
    async def put(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """PUT request"""
        return await self._request("PUT", endpoint, **kwargs)
    
    async def patch(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """PATCH request"""
        return await self._request("PATCH", endpoint, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """DELETE request"""
        return await self._request("DELETE", endpoint, **kwargs)
    
    async def health_check(self) -> bool:
        """Check platform health"""
        try:
            await self.get("/api/health", cache_key=f"{self.name}:health", cache_ttl=30)
            return True
        except Exception as e:
            logger.error(f"Health check failed for {self.name}: {e}")
            return False
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

