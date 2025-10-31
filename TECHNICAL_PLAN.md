# Krib Super Admin Platform - Technical Implementation Plan

## 1. ARCHITECTURE DECISIONS

### 1.1 Core Stack
- **Frontend**: Next.js 14 (TypeScript) + Tailwind CSS + shadcn/ui
- **Backend**: FastAPI (Python 3.11)
- **Database**: Supabase PostgreSQL (new dedicated project)
- **Deployment**: Vercel (frontend) + Render (backend)
- **Auth**: Supabase Auth + RLS policies
- **Cache**: Redis (Upstash) for API response caching

### 1.2 Why These Choices
- Next.js 14: Matches existing ecosystem, server components for performance
- FastAPI: Consistent with other platforms, async support, auto-docs
- Supabase: Centralized auth, real-time subscriptions, RLS for security
- Redis: Cache cross-platform API calls, reduce load on downstream services

---

## 2. DATABASE SCHEMA

### 2.1 Core Tables

```sql
-- Super admin users (separate from platform users)
CREATE TABLE super_admin_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL, -- 'super_admin', 'admin', 'analyst'
    permissions JSONB NOT NULL DEFAULT '{}',
    last_login_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Platform registry
CREATE TABLE platforms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL, -- 'host_dashboard', 'agent_dashboard', 'customer_platform'
    display_name TEXT NOT NULL,
    api_base_url TEXT NOT NULL,
    api_key TEXT NOT NULL, -- encrypted
    status TEXT DEFAULT 'active', -- 'active', 'maintenance', 'offline'
    health_check_endpoint TEXT,
    last_health_check TIMESTAMPTZ,
    supabase_project_id TEXT,
    supabase_url TEXT,
    supabase_service_key TEXT, -- encrypted
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Unified user registry (aggregates users from all platforms)
CREATE TABLE unified_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL,
    platform_id UUID REFERENCES platforms(id),
    platform_user_id UUID NOT NULL, -- user ID in source platform
    user_type TEXT NOT NULL, -- 'host', 'agent', 'customer', 'guest'
    full_name TEXT,
    phone TEXT,
    verification_status TEXT,
    account_status TEXT, -- 'active', 'suspended', 'banned'
    platform_specific_data JSONB,
    last_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(platform_id, platform_user_id)
);

-- Unified properties (aggregates from host + agent platforms)
CREATE TABLE unified_properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform_id UUID REFERENCES platforms(id),
    platform_property_id UUID NOT NULL,
    owner_user_id UUID REFERENCES unified_users(id),
    title TEXT,
    property_type TEXT,
    listing_type TEXT, -- 'short_term', 'long_term'
    city TEXT,
    price NUMERIC,
    price_currency TEXT DEFAULT 'AED',
    status TEXT,
    is_featured BOOLEAN DEFAULT false,
    platform_specific_data JSONB,
    last_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(platform_id, platform_property_id)
);

-- Unified bookings
CREATE TABLE unified_bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform_id UUID REFERENCES platforms(id),
    platform_booking_id UUID NOT NULL,
    property_id UUID REFERENCES unified_properties(id),
    guest_user_id UUID REFERENCES unified_users(id),
    host_user_id UUID REFERENCES unified_users(id),
    check_in DATE,
    check_out DATE,
    total_price NUMERIC,
    status TEXT,
    payment_status TEXT,
    platform_specific_data JSONB,
    last_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(platform_id, platform_booking_id)
);

-- Financial transactions (aggregates all revenue)
CREATE TABLE unified_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform_id UUID REFERENCES platforms(id),
    booking_id UUID REFERENCES unified_bookings(id),
    transaction_type TEXT NOT NULL, -- 'booking_payment', 'refund', 'payout'
    amount_total NUMERIC NOT NULL,
    amount_platform_fee NUMERIC NOT NULL,
    amount_host_payout NUMERIC,
    currency TEXT DEFAULT 'AED',
    payment_provider TEXT, -- 'stripe'
    payment_provider_id TEXT,
    status TEXT, -- 'pending', 'completed', 'failed'
    platform_specific_data JSONB,
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Admin actions audit log
CREATE TABLE admin_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_user_id UUID REFERENCES super_admin_users(id),
    action_type TEXT NOT NULL, -- 'user_suspend', 'property_feature', 'booking_cancel', etc.
    target_platform UUID REFERENCES platforms(id),
    target_entity_type TEXT, -- 'user', 'property', 'booking'
    target_entity_id UUID,
    action_details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Verification queue (agents awaiting approval)
CREATE TABLE verification_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform_id UUID REFERENCES platforms(id),
    user_id UUID REFERENCES unified_users(id),
    verification_type TEXT NOT NULL, -- 'agent_registration', 'host_verification'
    status TEXT DEFAULT 'pending', -- 'pending', 'in_review', 'approved', 'rejected'
    documents JSONB,
    reviewed_by UUID REFERENCES super_admin_users(id),
    reviewed_at TIMESTAMPTZ,
    review_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- System notifications
CREATE TABLE admin_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_user_id UUID REFERENCES super_admin_users(id),
    type TEXT NOT NULL, -- 'new_verification', 'payment_failed', 'system_alert'
    title TEXT NOT NULL,
    message TEXT,
    data JSONB,
    is_read BOOLEAN DEFAULT false,
    priority TEXT DEFAULT 'normal', -- 'low', 'normal', 'high', 'critical'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Analytics snapshots (cached aggregated data)
CREATE TABLE analytics_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_type TEXT NOT NULL, -- 'daily_metrics', 'weekly_report', 'monthly_revenue'
    platform_id UUID REFERENCES platforms(id), -- NULL for cross-platform
    date DATE NOT NULL,
    metrics JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(snapshot_type, platform_id, date)
);
```

### 2.2 Indexes
```sql
CREATE INDEX idx_unified_users_email ON unified_users(email);
CREATE INDEX idx_unified_users_platform ON unified_users(platform_id, platform_user_id);
CREATE INDEX idx_unified_properties_owner ON unified_properties(owner_user_id);
CREATE INDEX idx_unified_bookings_dates ON unified_bookings(check_in, check_out);
CREATE INDEX idx_unified_transactions_platform ON unified_transactions(platform_id, created_at);
CREATE INDEX idx_admin_audit_log_admin ON admin_audit_log(admin_user_id, created_at);
CREATE INDEX idx_verification_queue_status ON verification_queue(status, created_at);
```

### 2.3 RLS Policies
```sql
-- Super admins can read all data
CREATE POLICY "Super admins read all" ON unified_users FOR SELECT
USING (EXISTS (
    SELECT 1 FROM super_admin_users 
    WHERE id = auth.uid() AND is_active = true
));

-- Admins can only read based on permissions
CREATE POLICY "Admins read based on permissions" ON unified_users FOR SELECT
USING (EXISTS (
    SELECT 1 FROM super_admin_users 
    WHERE id = auth.uid() 
    AND is_active = true
    AND permissions->>'can_view_users' = 'true'
));

-- All admin actions must be logged
CREATE POLICY "Log all admin actions" ON admin_audit_log FOR INSERT
WITH CHECK (admin_user_id = auth.uid());
```

---

## 3. BACKEND ARCHITECTURE

### 3.1 Project Structure
```
backend/
├── app/
│   ├── main.py                      # FastAPI app
│   ├── config.py                    # Settings (env vars)
│   ├── dependencies.py              # Auth dependencies
│   │
│   ├── api/
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py             # Super admin auth
│   │   │   ├── users.py            # User management
│   │   │   ├── properties.py      # Property management
│   │   │   ├── bookings.py        # Booking management
│   │   │   ├── verification.py    # Agent/host verification
│   │   │   ├── analytics.py       # Analytics & reports
│   │   │   ├── financial.py       # Financial oversight
│   │   │   └── platforms.py       # Platform health & config
│   │
│   ├── services/
│   │   ├── platform_client.py      # Base class for platform APIs
│   │   ├── host_platform.py        # Host dashboard client
│   │   ├── agent_platform.py       # Agent dashboard client
│   │   ├── customer_platform.py    # Customer platform client
│   │   ├── sync_service.py         # Data synchronization
│   │   ├── cache_service.py        # Redis caching
│   │   ├── encryption_service.py   # Encrypt API keys
│   │   └── analytics_service.py    # Analytics aggregation
│   │
│   ├── models/
│   │   ├── schemas.py              # Pydantic models
│   │   ├── enums.py                # Enums
│   │   └── responses.py            # Response models
│   │
│   ├── core/
│   │   ├── supabase.py            # Supabase client
│   │   ├── redis.py               # Redis client
│   │   └── security.py            # Auth helpers
│   │
│   └── utils/
│       ├── logger.py              # Logging
│       ├── validators.py          # Input validation
│       └── formatters.py          # Data formatters
│
├── requirements.txt
├── Dockerfile
└── render.yaml
```

### 3.2 Key Service Implementations

#### Platform Client Base Class
```python
# app/services/platform_client.py
from typing import Optional, Dict, Any
import httpx
from app.core.redis import redis_client
from app.utils.logger import logger

class PlatformClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0
        )
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        cache_key: Optional[str] = None,
        cache_ttl: int = 300,
        **kwargs
    ) -> Dict[Any, Any]:
        # Check cache first
        if cache_key and method == "GET":
            cached = await redis_client.get(cache_key)
            if cached:
                return cached
        
        # Make request
        response = await self.client.request(method, endpoint, **kwargs)
        response.raise_for_status()
        data = response.json()
        
        # Cache if GET
        if cache_key and method == "GET":
            await redis_client.set(cache_key, data, ex=cache_ttl)
        
        return data
    
    async def get(self, endpoint: str, **kwargs) -> Dict[Any, Any]:
        return await self._request("GET", endpoint, **kwargs)
    
    async def post(self, endpoint: str, **kwargs) -> Dict[Any, Any]:
        return await self._request("POST", endpoint, **kwargs)
    
    async def health_check(self) -> bool:
        try:
            await self.get("/api/health")
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
```

#### Host Platform Client
```python
# app/services/host_platform.py
from app.services.platform_client import PlatformClient

class HostPlatformClient(PlatformClient):
    async def get_all_properties(self, page: int = 1, limit: int = 100):
        return await self.get(
            "/api/v1/properties",
            params={"page": page, "limit": limit},
            cache_key=f"host:properties:page:{page}",
            cache_ttl=300
        )
    
    async def get_property(self, property_id: str):
        return await self.get(
            f"/api/v1/properties/{property_id}",
            cache_key=f"host:property:{property_id}",
            cache_ttl=300
        )
    
    async def get_all_bookings(self):
        return await self.get("/api/v1/bookings")
    
    async def cancel_booking(self, booking_id: str, reason: str):
        return await self.delete(
            f"/api/v1/bookings/{booking_id}",
            json={"reason": reason}
        )
```

#### Agent Platform Client
```python
# app/services/agent_platform.py
from app.services.platform_client import PlatformClient

class AgentPlatformClient(PlatformClient):
    async def get_pending_verifications(self):
        return await self.get("/api/admin/verification/pending")
    
    async def get_user_verification_details(self, user_id: str):
        return await self.get(f"/api/admin/verification/user/{user_id}")
    
    async def approve_agent(self, user_id: str, notes: str):
        return await self.post(
            f"/api/admin/verification/user/{user_id}/action",
            json={"action": "approve", "notes": notes}
        )
    
    async def reject_agent(self, user_id: str, reason: str):
        return await self.post(
            f"/api/admin/verification/user/{user_id}/action",
            json={"action": "reject", "rejection_reason": reason}
        )
```

#### Sync Service (Critical)
```python
# app/services/sync_service.py
from typing import List
from app.services.host_platform import HostPlatformClient
from app.services.agent_platform import AgentPlatformClient
from app.core.supabase import supabase_client
from app.utils.logger import logger

class SyncService:
    def __init__(self):
        self.host_client = None  # Initialize with platform configs
        self.agent_client = None
    
    async def sync_all_platforms(self):
        """Full sync of all platforms"""
        await self.sync_host_platform()
        await self.sync_agent_platform()
        await self.sync_customer_platform()
    
    async def sync_host_platform(self):
        """Sync host dashboard data"""
        logger.info("Syncing host platform...")
        
        # Get platform config
        platform = await self._get_platform_config("host_dashboard")
        self.host_client = HostPlatformClient(
            platform["api_base_url"], 
            platform["api_key"]
        )
        
        # Sync properties
        properties = await self.host_client.get_all_properties()
        await self._upsert_properties(platform["id"], properties["data"])
        
        # Sync bookings
        bookings = await self.host_client.get_all_bookings()
        await self._upsert_bookings(platform["id"], bookings["data"])
        
        logger.info("Host platform sync complete")
    
    async def _get_platform_config(self, platform_name: str):
        """Get platform configuration from database"""
        result = await supabase_client.table("platforms").select("*").eq("name", platform_name).single().execute()
        return result.data
    
    async def _upsert_properties(self, platform_id: str, properties: List[dict]):
        """Upsert properties into unified_properties"""
        for prop in properties:
            await supabase_client.table("unified_properties").upsert({
                "platform_id": platform_id,
                "platform_property_id": prop["id"],
                "owner_user_id": await self._get_unified_user_id(platform_id, prop["user_id"]),
                "title": prop["title"],
                "property_type": prop["property_type"],
                "listing_type": "short_term",
                "city": prop.get("address", {}).get("city"),
                "price": prop["base_price_per_night"],
                "status": prop["status"],
                "platform_specific_data": prop,
                "last_synced_at": "NOW()"
            }).execute()
```

### 3.3 API Endpoints

```python
# app/api/v1/users.py
from fastapi import APIRouter, Depends
from app.dependencies import get_current_admin
from app.services.sync_service import SyncService

router = APIRouter(prefix="/users", tags=["users"])

@router.get("")
async def list_users(
    platform: Optional[str] = None,
    user_type: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    admin: dict = Depends(get_current_admin)
):
    """List all users across platforms"""
    query = supabase_client.table("unified_users").select("*")
    
    if platform:
        query = query.eq("platform_id", platform)
    if user_type:
        query = query.eq("user_type", user_type)
    
    result = await query.range((page-1)*limit, page*limit-1).execute()
    return {"data": result.data, "page": page, "limit": limit}

@router.get("/{user_id}")
async def get_user(
    user_id: str,
    admin: dict = Depends(get_current_admin)
):
    """Get user details with cross-platform data"""
    user = await supabase_client.table("unified_users").select("*").eq("id", user_id).single().execute()
    
    # Fetch from source platform
    platform_client = get_platform_client(user.data["platform_id"])
    platform_data = await platform_client.get_user(user.data["platform_user_id"])
    
    return {
        "unified_data": user.data,
        "platform_data": platform_data
    }

@router.patch("/{user_id}/status")
async def update_user_status(
    user_id: str,
    status: str,
    reason: Optional[str] = None,
    admin: dict = Depends(get_current_admin)
):
    """Suspend/ban/activate user"""
    # Update in unified database
    await supabase_client.table("unified_users").update({
        "account_status": status
    }).eq("id", user_id).execute()
    
    # Log admin action
    await log_admin_action(admin["id"], "user_status_update", user_id, {
        "new_status": status,
        "reason": reason
    })
    
    # Sync to source platform (if supported)
    # ...
    
    return {"success": True}
```

---

## 4. FRONTEND ARCHITECTURE

### 4.1 Project Structure
```
frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── layout.tsx
│   │
│   ├── (dashboard)/
│   │   ├── layout.tsx              # Main dashboard layout
│   │   ├── page.tsx                # Dashboard home
│   │   │
│   │   ├── users/
│   │   │   ├── page.tsx           # User list
│   │   │   └── [id]/
│   │   │       └── page.tsx       # User detail
│   │   │
│   │   ├── properties/
│   │   │   ├── page.tsx           # Property list
│   │   │   └── [id]/
│   │   │       └── page.tsx       # Property detail
│   │   │
│   │   ├── bookings/
│   │   │   ├── page.tsx
│   │   │   └── [id]/
│   │   │       └── page.tsx
│   │   │
│   │   ├── verification/
│   │   │   ├── page.tsx           # Verification queue
│   │   │   └── [id]/
│   │   │       └── page.tsx       # Verification review
│   │   │
│   │   ├── financial/
│   │   │   ├── page.tsx           # Revenue dashboard
│   │   │   ├── transactions/
│   │   │   └── payouts/
│   │   │
│   │   ├── analytics/
│   │   │   ├── page.tsx           # Analytics overview
│   │   │   ├── users/
│   │   │   ├── revenue/
│   │   │   └── properties/
│   │   │
│   │   └── platforms/
│   │       ├── page.tsx           # Platform health
│   │       └── [id]/
│   │           └── page.tsx       # Platform config
│   │
│   └── api/
│       └── [...]/                  # API routes (if needed)
│
├── components/
│   ├── ui/                         # shadcn components
│   ├── dashboard/
│   │   ├── sidebar.tsx
│   │   ├── header.tsx
│   │   ├── stats-card.tsx
│   │   └── platform-status.tsx
│   │
│   ├── users/
│   │   ├── user-table.tsx
│   │   ├── user-filters.tsx
│   │   └── user-actions.tsx
│   │
│   ├── verification/
│   │   ├── verification-queue.tsx
│   │   ├── document-viewer.tsx
│   │   └── approval-form.tsx
│   │
│   └── analytics/
│       ├── revenue-chart.tsx
│       ├── user-growth-chart.tsx
│       └── metrics-grid.tsx
│
├── lib/
│   ├── api/
│   │   ├── client.ts              # API client
│   │   ├── users.ts
│   │   ├── properties.ts
│   │   └── analytics.ts
│   │
│   ├── supabase/
│   │   ├── client.ts              # Supabase client
│   │   └── auth.ts
│   │
│   └── utils/
│       ├── format.ts
│       └── validation.ts
│
├── hooks/
│   ├── use-user.ts
│   ├── use-analytics.ts
│   └── use-platform-status.ts
│
├── types/
│   ├── api.ts
│   ├── user.ts
│   └── platform.ts
│
└── middleware.ts                   # Auth middleware
```

### 4.2 Key Components

#### Dashboard Layout
```typescript
// app/(dashboard)/layout.tsx
import { Sidebar } from "@/components/dashboard/sidebar"
import { Header } from "@/components/dashboard/header"
import { PlatformStatus } from "@/components/dashboard/platform-status"

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <PlatformStatus />
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
```

#### Platform Status Component
```typescript
// components/dashboard/platform-status.tsx
"use client"

import { useQuery } from "@tanstack/react-query"
import { getPlatformStatus } from "@/lib/api/platforms"

export function PlatformStatus() {
  const { data } = useQuery({
    queryKey: ["platform-status"],
    queryFn: getPlatformStatus,
    refetchInterval: 30000, // Poll every 30s
  })

  return (
    <div className="border-b bg-slate-50 px-6 py-2">
      <div className="flex gap-4 text-sm">
        {data?.platforms.map((platform) => (
          <div key={platform.id} className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${
              platform.status === 'active' ? 'bg-green-500' : 'bg-red-500'
            }`} />
            <span>{platform.display_name}</span>
            <span className="text-gray-500">{platform.response_time}ms</span>
          </div>
        ))}
      </div>
    </div>
  )
}
```

---

## 5. DATA SYNCHRONIZATION STRATEGY

### 5.1 Sync Methods

**1. Scheduled Sync (Primary)**
- Cron job every 5 minutes
- Full sync every hour
- Incremental sync for recent changes

**2. Webhook-Based Sync (Secondary)**
- Platforms send webhooks on events
- Real-time updates for critical events
- Fallback to scheduled sync if webhook fails

**3. On-Demand Sync**
- Manual trigger from admin dashboard
- Triggered before viewing specific data
- Used for verification queue

### 5.2 Implementation

```python
# app/services/sync_service.py (continued)

class SyncService:
    async def incremental_sync(self, since: datetime):
        """Sync only changes since timestamp"""
        for platform in await self._get_active_platforms():
            try:
                # Get changes since last sync
                changes = await platform_client.get_changes(since)
                await self._apply_changes(platform.id, changes)
            except Exception as e:
                logger.error(f"Incremental sync failed for {platform.name}: {e}")
    
    async def sync_verification_queue(self):
        """Sync pending agent verifications"""
        agent_platform = await self._get_platform_config("agent_dashboard")
        client = AgentPlatformClient(agent_platform["api_base_url"], agent_platform["api_key"])
        
        pending = await client.get_pending_verifications()
        
        for verification in pending["data"]:
            # Check if already in queue
            existing = await supabase_client.table("verification_queue").select("*").eq(
                "platform_id", agent_platform["id"]
            ).eq(
                "user_id", verification["user_id"]
            ).execute()
            
            if not existing.data:
                # Add to queue
                await supabase_client.table("verification_queue").insert({
                    "platform_id": agent_platform["id"],
                    "user_id": await self._get_or_create_unified_user(
                        agent_platform["id"], 
                        verification["user_id"],
                        verification["user_data"]
                    ),
                    "verification_type": "agent_registration",
                    "status": "pending",
                    "documents": verification["documents"]
                }).execute()
```

---

## 6. AUTHENTICATION & SECURITY

### 6.1 Super Admin Auth Flow

```typescript
// lib/supabase/auth.ts
import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export async function signIn(email: string, password: string) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  })
  
  if (error) throw error
  
  // Verify user is super admin
  const { data: adminData } = await supabase
    .from('super_admin_users')
    .select('*')
    .eq('id', data.user.id)
    .eq('is_active', true)
    .single()
  
  if (!adminData) {
    await supabase.auth.signOut()
    throw new Error('Unauthorized')
  }
  
  return { user: data.user, admin: adminData }
}
```

### 6.2 Middleware Protection

```typescript
// middleware.ts
import { createMiddlewareClient } from '@supabase/auth-helpers-nextjs'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function middleware(req: NextRequest) {
  const res = NextResponse.next()
  const supabase = createMiddlewareClient({ req, res })

  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    return NextResponse.redirect(new URL('/login', req.url))
  }

  // Verify super admin
  const { data } = await supabase
    .from('super_admin_users')
    .select('role, is_active')
    .eq('id', session.user.id)
    .single()

  if (!data?.is_active) {
    return NextResponse.redirect(new URL('/login', req.url))
  }

  return res
}

export const config = {
  matcher: ['/((?!login|api|_next/static|_next/image|favicon.ico).*)'],
}
```

### 6.3 API Key Encryption

```python
# app/services/encryption_service.py
from cryptography.fernet import Fernet
from app.config import settings

class EncryptionService:
    def __init__(self):
        self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())
    
    def encrypt_api_key(self, api_key: str) -> str:
        return self.cipher.encrypt(api_key.encode()).decode()
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        return self.cipher.decrypt(encrypted_key.encode()).decode()
```

---

## 7. DEPLOYMENT PLAN

### 7.1 Infrastructure Setup

**Supabase Project**
1. Create new Supabase project: `krib-superadmin`
2. Run database migrations
3. Set up RLS policies
4. Configure auth settings

**Redis (Upstash)**
1. Create Redis instance
2. Configure connection
3. Set TTL policies

**Backend (Render)**
1. Create new web service
2. Connect GitHub repo
3. Set environment variables
4. Configure health checks

**Frontend (Vercel)**
1. Import GitHub repo
2. Set environment variables
3. Configure build settings
4. Set up custom domain

### 7.2 Environment Variables

**Backend (.env)**
```bash
# Database
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
DATABASE_URL=

# Redis
REDIS_URL=

# Security
ENCRYPTION_KEY=
JWT_SECRET=

# Platform APIs
HOST_DASHBOARD_URL=https://krib-host-dahsboard-backend.onrender.com
HOST_DASHBOARD_API_KEY=
AGENT_DASHBOARD_URL=https://krib-real-estate-agent-dahaboard-backend.onrender.com
AGENT_DASHBOARD_API_KEY=
CUSTOMER_PLATFORM_URL=https://krib-backend.onrender.com
CUSTOMER_PLATFORM_API_KEY=

# Platform Supabase Access
HOST_DASHBOARD_SUPABASE_URL=
HOST_DASHBOARD_SUPABASE_KEY=
AGENT_DASHBOARD_SUPABASE_URL=
AGENT_DASHBOARD_SUPABASE_KEY=
CUSTOMER_PLATFORM_SUPABASE_URL=
CUSTOMER_PLATFORM_SUPABASE_KEY=
```

**Frontend (.env.local)**
```bash
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_API_URL=
```

---

## 8. CRITICAL IMPLEMENTATION ISSUES

### Issue 1: Cross-Platform User Identification
**Problem**: Same email might exist across platforms with different UUIDs
**Solution**: 
- Use email as primary identifier
- Create mapping table
- Implement user merge functionality

### Issue 2: Real-Time Sync Consistency
**Problem**: Data might be outdated between syncs
**Solution**:
- Implement webhook endpoints on all platforms
- Use Redis pub/sub for real-time updates
- Add "last synced" timestamp to UI
- Show warning if data is stale (>5 min)

### Issue 3: Platform API Authentication
**Problem**: Each platform uses different auth
**Solution**:
- Store encrypted API keys per platform
- Implement refresh logic for expired tokens
- Fallback to service role keys

### Issue 4: Document Viewing from Agent Platform
**Problem**: Documents are in private S3 bucket
**Solution**:
- Request signed URLs from agent platform API
- Cache signed URLs (expire in 1 hour)
- Implement direct S3 access with agent platform's credentials

### Issue 5: Financial Data Aggregation
**Problem**: Stripe transactions exist in multiple places
**Solution**:
- Create unified transactions table
- Sync from each platform's transaction log
- Implement reconciliation job to detect discrepancies

---

## 9. IMPLEMENTATION PHASES

### Phase 1: Foundation (Week 1)
- [ ] Set up Supabase project
- [ ] Create database schema
- [ ] Set up backend project structure
- [ ] Set up frontend project structure
- [ ] Implement authentication
- [ ] Deploy initial versions

### Phase 2: Platform Integration (Week 2)
- [ ] Implement platform clients
- [ ] Build sync service
- [ ] Set up Redis caching
- [ ] Create platform health monitoring
- [ ] Test API integrations

### Phase 3: User Management (Week 3)
- [ ] Build user list page
- [ ] Build user detail page
- [ ] Implement user actions (suspend, ban)
- [ ] Build unified user sync
- [ ] Add search and filters

### Phase 4: Verification System (Week 3-4)
- [ ] Build verification queue
- [ ] Build document viewer
- [ ] Implement approval workflow
- [ ] Integrate with agent platform API
- [ ] Add email notifications

### Phase 5: Property & Booking Management (Week 4-5)
- [ ] Build property list
- [ ] Build property detail
- [ ] Build booking list
- [ ] Implement booking cancellation
- [ ] Add bulk operations

### Phase 6: Financial Dashboard (Week 5-6)
- [ ] Build revenue dashboard
- [ ] Build transaction list
- [ ] Implement payout management
- [ ] Add financial reports
- [ ] Stripe integration

### Phase 7: Analytics (Week 6-7)
- [ ] Build analytics service
- [ ] Create dashboard widgets
- [ ] Implement chart components
- [ ] Add export functionality
- [ ] Create scheduled reports

### Phase 8: Polish & Launch (Week 7-8)
- [ ] Add audit logging UI
- [ ] Implement notifications
- [ ] Performance optimization
- [ ] Security audit
- [ ] Documentation
- [ ] Production deployment

---

## 10. MONITORING & MAINTENANCE

### Health Checks
- Backend: `/api/health`
- Platform connectivity checks every 30s
- Database connection monitoring
- Redis connection monitoring

### Logging
- Structured JSON logging
- Log levels: DEBUG, INFO, WARNING, ERROR
- Log aggregation (consider Datadog or Sentry)
- Admin action audit trail

### Alerts
- Platform offline > 5 min
- Sync failed > 3 times
- Failed authentication attempts > 10/hour
- Database connection issues

---

## 11. COST ESTIMATION

### Infrastructure
- Supabase (Pro): $25/month
- Render (Pro): $25/month
- Vercel (Pro): $20/month
- Upstash Redis: $10/month
- **Total**: ~$80/month

### Scaling Considerations
- Add Redis replica for high availability
- Upgrade Render to scale instances
- Consider CDN for static assets

