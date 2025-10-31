from supabase import create_client, Client
from app.config import settings

class SupabaseClient:
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
    
    def get_client(self) -> Client:
        return self.client

supabase_admin = SupabaseClient()

def get_supabase() -> Client:
    return supabase_admin.get_client()

