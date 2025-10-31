from typing import List, Dict, Any, Optional
from datetime import datetime
from app.services.host_platform import HostPlatformClient
from app.services.agent_platform import AgentPlatformClient
from app.services.customer_platform import CustomerPlatformClient
from app.core.supabase import get_supabase
from app.core.redis import redis_client
from app.utils.logger import logger
from app.config import settings

class SyncService:
    """Service to synchronize data from all platforms"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.host_client: Optional[HostPlatformClient] = None
        self.agent_client: Optional[AgentPlatformClient] = None
        self.customer_client: Optional[CustomerPlatformClient] = None
    
    async def initialize_clients(self):
        """Initialize platform clients"""
        # Get platform configurations from database
        platforms_response = self.supabase.table("platforms").select("*").execute()
        
        for platform in platforms_response.data:
            if platform["name"] == "host_dashboard":
                self.host_client = HostPlatformClient(
                    platform["api_base_url"],
                    platform["api_key"]
                )
            elif platform["name"] == "agent_dashboard":
                self.agent_client = AgentPlatformClient(
                    platform["api_base_url"],
                    platform["api_key"]
                )
            elif platform["name"] == "customer_platform":
                self.customer_client = CustomerPlatformClient(
                    platform["api_base_url"],
                    platform["api_key"]
                )
    
    async def sync_all_platforms(self):
        """Full sync of all platforms"""
        logger.info("Starting full platform sync...")
        
        await self.initialize_clients()
        
        try:
            await self.sync_host_platform()
            await self.sync_agent_platform()
            await self.sync_customer_platform()
            logger.info("Full platform sync completed successfully")
        except Exception as e:
            logger.error(f"Platform sync failed: {e}")
            raise
    
    async def sync_host_platform(self):
        """Sync host dashboard data"""
        if not self.host_client:
            logger.warning("Host client not initialized")
            return
        
        logger.info("Syncing host platform...")
        
        # Get platform ID
        platform_response = self.supabase.table("platforms").select("id").eq("name", "host_dashboard").single().execute()
        platform_id = platform_response.data["id"]
        
        # Sync users
        try:
            users_data = await self.host_client.get_host_users()
            await self._sync_users(platform_id, users_data.get("data", []), "host")
        except Exception as e:
            logger.error(f"Failed to sync host users: {e}")
        
        # Sync properties
        try:
            page = 1
            while True:
                properties_data = await self.host_client.get_all_properties(page=page, limit=100)
                properties = properties_data.get("data", [])
                
                if not properties:
                    break
                
                await self._sync_properties(platform_id, properties, "short_term")
                page += 1
        except Exception as e:
            logger.error(f"Failed to sync host properties: {e}")
        
        # Sync bookings
        try:
            bookings_data = await self.host_client.get_all_bookings()
            await self._sync_bookings(platform_id, bookings_data.get("data", []))
        except Exception as e:
            logger.error(f"Failed to sync host bookings: {e}")
        
        logger.info("Host platform sync completed")
    
    async def sync_agent_platform(self):
        """Sync agent dashboard data"""
        if not self.agent_client:
            logger.warning("Agent client not initialized")
            return
        
        logger.info("Syncing agent platform...")
        
        # Get platform ID
        platform_response = self.supabase.table("platforms").select("id").eq("name", "agent_dashboard").single().execute()
        platform_id = platform_response.data["id"]
        
        # Sync agents
        try:
            agents_data = await self.agent_client.get_all_agents()
            await self._sync_users(platform_id, agents_data.get("data", []), "agent")
        except Exception as e:
            logger.error(f"Failed to sync agents: {e}")
        
        # Sync properties
        try:
            page = 1
            while True:
                properties_data = await self.agent_client.get_all_properties(page=page, limit=100)
                properties = properties_data.get("data", [])
                
                if not properties:
                    break
                
                await self._sync_properties(platform_id, properties, "long_term")
                page += 1
        except Exception as e:
            logger.error(f"Failed to sync agent properties: {e}")
        
        # Sync verification queue
        try:
            await self.sync_verification_queue()
        except Exception as e:
            logger.error(f"Failed to sync verification queue: {e}")
        
        logger.info("Agent platform sync completed")
    
    async def sync_customer_platform(self):
        """Sync customer platform data"""
        if not self.customer_client:
            logger.warning("Customer client not initialized")
            return
        
        logger.info("Syncing customer platform...")
        
        # Get platform ID
        platform_response = self.supabase.table("platforms").select("id").eq("name", "customer_platform").single().execute()
        platform_id = platform_response.data["id"]
        
        # Sync customers
        try:
            users_data = await self.customer_client.get_all_users()
            await self._sync_users(platform_id, users_data.get("data", []), "customer")
        except Exception as e:
            logger.error(f"Failed to sync customers: {e}")
        
        # Sync bookings
        try:
            bookings_data = await self.customer_client.get_all_bookings()
            await self._sync_bookings(platform_id, bookings_data.get("data", []))
        except Exception as e:
            logger.error(f"Failed to sync customer bookings: {e}")
        
        logger.info("Customer platform sync completed")
    
    async def sync_verification_queue(self):
        """Sync agent verification queue"""
        logger.info("Syncing verification queue...")
        
        if not self.agent_client:
            return
        
        # Get platform ID
        platform_response = self.supabase.table("platforms").select("id").eq("name", "agent_dashboard").single().execute()
        platform_id = platform_response.data["id"]
        
        # Get pending verifications
        pending_response = await self.agent_client.get_pending_verifications()
        pending_verifications = pending_response.get("data", [])
        
        for verification in pending_verifications:
            try:
                # Get or create unified user
                user_id = await self._get_or_create_unified_user(
                    platform_id,
                    verification["id"],
                    verification.get("email", ""),
                    "agent",
                    {
                        "first_name": verification.get("first_name"),
                        "last_name": verification.get("last_name"),
                        "phone": verification.get("phone"),
                        "verification_status": verification.get("verification_status")
                    }
                )
                
                # Check if already in queue
                existing = self.supabase.table("verification_queue").select("*").eq(
                    "platform_id", platform_id
                ).eq(
                    "platform_user_id", verification["id"]
                ).execute()
                
                if not existing.data:
                    # Add to queue
                    self.supabase.table("verification_queue").insert({
                        "platform_id": platform_id,
                        "user_id": user_id,
                        "platform_user_id": verification["id"],
                        "verification_type": "agent_registration",
                        "status": "pending",
                        "documents": verification.get("documents", {}),
                        "created_at": verification.get("created_at", datetime.utcnow().isoformat())
                    }).execute()
                else:
                    # Update existing
                    self.supabase.table("verification_queue").update({
                        "status": self._map_verification_status(verification.get("verification_status")),
                        "documents": verification.get("documents", {}),
                        "updated_at": datetime.utcnow().isoformat()
                    }).eq("id", existing.data[0]["id"]).execute()
            
            except Exception as e:
                logger.error(f"Failed to sync verification for user {verification.get('id')}: {e}")
        
        logger.info(f"Synced {len(pending_verifications)} pending verifications")
    
    async def _sync_users(self, platform_id: str, users: List[Dict], user_type: str):
        """Sync users to unified_users table"""
        for user in users:
            try:
                await self._get_or_create_unified_user(
                    platform_id,
                    user["id"],
                    user.get("email", ""),
                    user_type,
                    user
                )
            except Exception as e:
                logger.error(f"Failed to sync user {user.get('id')}: {e}")
    
    async def _sync_properties(self, platform_id: str, properties: List[Dict], listing_type: str):
        """Sync properties to unified_properties table"""
        for prop in properties:
            try:
                # Get owner user ID
                owner_id = await self._get_unified_user_id(platform_id, prop.get("user_id"))
                
                # Upsert property
                property_data = {
                    "platform_id": platform_id,
                    "platform_property_id": prop["id"],
                    "owner_user_id": owner_id,
                    "title": prop.get("title", ""),
                    "property_type": prop.get("property_type", ""),
                    "listing_type": listing_type,
                    "city": prop.get("address", {}).get("city") or prop.get("city", ""),
                    "price": float(prop.get("base_price_per_night") or prop.get("price", 0)),
                    "price_currency": prop.get("price_currency", "AED"),
                    "status": prop.get("status", "active"),
                    "is_featured": prop.get("is_featured", False),
                    "platform_specific_data": prop,
                    "last_synced_at": datetime.utcnow().isoformat()
                }
                
                self.supabase.table("unified_properties").upsert(
                    property_data,
                    on_conflict="platform_id,platform_property_id"
                ).execute()
                
            except Exception as e:
                logger.error(f"Failed to sync property {prop.get('id')}: {e}")
    
    async def _sync_bookings(self, platform_id: str, bookings: List[Dict]):
        """Sync bookings to unified_bookings table"""
        for booking in bookings:
            try:
                # Get property ID
                property_response = self.supabase.table("unified_properties").select("id").eq(
                    "platform_id", platform_id
                ).eq(
                    "platform_property_id", booking.get("property_id")
                ).execute()
                
                if not property_response.data:
                    logger.warning(f"Property not found for booking {booking.get('id')}")
                    continue
                
                property_id = property_response.data[0]["id"]
                
                # Get guest and host user IDs
                guest_id = await self._get_unified_user_id(platform_id, booking.get("guest_id"))
                host_id = await self._get_unified_user_id(platform_id, booking.get("host_id"))
                
                # Upsert booking
                booking_data = {
                    "platform_id": platform_id,
                    "platform_booking_id": booking["id"],
                    "property_id": property_id,
                    "guest_user_id": guest_id,
                    "host_user_id": host_id,
                    "check_in": booking.get("check_in"),
                    "check_out": booking.get("check_out"),
                    "total_price": float(booking.get("total_price", 0)),
                    "status": booking.get("status", "pending"),
                    "payment_status": booking.get("payment_status", "pending"),
                    "platform_specific_data": booking,
                    "last_synced_at": datetime.utcnow().isoformat()
                }
                
                self.supabase.table("unified_bookings").upsert(
                    booking_data,
                    on_conflict="platform_id,platform_booking_id"
                ).execute()
                
            except Exception as e:
                logger.error(f"Failed to sync booking {booking.get('id')}: {e}")
    
    async def _get_or_create_unified_user(
        self,
        platform_id: str,
        platform_user_id: str,
        email: str,
        user_type: str,
        platform_data: Dict
    ) -> str:
        """Get or create unified user record"""
        # Check if user exists
        existing = self.supabase.table("unified_users").select("id").eq(
            "platform_id", platform_id
        ).eq(
            "platform_user_id", platform_user_id
        ).execute()
        
        if existing.data:
            return existing.data[0]["id"]
        
        # Create new user
        user_data = {
            "email": email,
            "platform_id": platform_id,
            "platform_user_id": platform_user_id,
            "user_type": user_type,
            "full_name": f"{platform_data.get('first_name', '')} {platform_data.get('last_name', '')}".strip() or platform_data.get('name', ''),
            "phone": platform_data.get("phone", ""),
            "verification_status": platform_data.get("verification_status", ""),
            "account_status": "active",
            "platform_specific_data": platform_data,
            "last_synced_at": datetime.utcnow().isoformat()
        }
        
        response = self.supabase.table("unified_users").insert(user_data).execute()
        return response.data[0]["id"]
    
    async def _get_unified_user_id(self, platform_id: str, platform_user_id: str) -> Optional[str]:
        """Get unified user ID from platform user ID"""
        if not platform_user_id:
            return None
        
        response = self.supabase.table("unified_users").select("id").eq(
            "platform_id", platform_id
        ).eq(
            "platform_user_id", platform_user_id
        ).execute()
        
        if response.data:
            return response.data[0]["id"]
        
        return None
    
    def _map_verification_status(self, platform_status: str) -> str:
        """Map platform verification status to unified status"""
        status_map = {
            "pending": "pending",
            "under_review": "in_review",
            "approved": "approved",
            "rejected": "rejected",
            "resubmission_required": "pending"
        }
        return status_map.get(platform_status, "pending")

sync_service = SyncService()

