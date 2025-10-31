"""Host Dashboard Supabase client for direct database access"""
from supabase import create_client, Client
from typing import Optional
from app.config import settings

class HostSupabaseClient:
    """Direct Supabase client for Host Dashboard database"""
    
    def __init__(self):
        if not settings.HOST_DASHBOARD_SUPABASE_URL or not settings.HOST_DASHBOARD_SUPABASE_KEY:
            raise ValueError("Host Dashboard Supabase credentials not configured")
        
        self.client: Client = create_client(
            settings.HOST_DASHBOARD_SUPABASE_URL,
            settings.HOST_DASHBOARD_SUPABASE_KEY
        )
    
    async def get_all_users(self):
        """Get all host users"""
        response = self.client.table("users").select("*").execute()
        return response.data
    
    async def get_user(self, user_id: str):
        """Get user by ID"""
        response = self.client.table("users").select("*").eq("id", user_id).execute()
        return response.data[0] if response.data else None
    
    async def update_user_status(self, user_id: str, is_active: bool):
        """Update user active status"""
        response = self.client.table("users").update({
            "is_active": is_active
        }).eq("id", user_id).execute()
        return response.data
    
    async def get_all_payouts(self, status: Optional[str] = None):
        """Get all payouts"""
        query = self.client.table("payouts").select("*")
        if status:
            query = query.eq("status", status)
        response = query.execute()
        return response.data
    
    async def get_payout(self, payout_id: str):
        """Get payout by ID"""
        response = self.client.table("payouts").select("*").eq("id", payout_id).execute()
        return response.data[0] if response.data else None
    
    async def get_stripe_events(self, limit: int = 100):
        """Get recent Stripe webhook events"""
        response = self.client.table("stripe_events").select("*").order("created_at", desc=True).limit(limit).execute()
        return response.data
    
    async def get_property_analytics(self, property_id: str = None):
        """Get property analytics"""
        query = self.client.table("property_analytics").select("*")
        if property_id:
            query = query.eq("property_id", property_id)
        response = query.execute()
        return response.data
    
    async def get_reviews(self, property_id: str = None):
        """Get reviews"""
        query = self.client.table("reviews").select("*")
        if property_id:
            query = query.eq("property_id", property_id)
        response = query.execute()
        return response.data

