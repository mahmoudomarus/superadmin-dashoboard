# 🏠 Krib Host Dashboard - Project Overview & Architecture

**Project Name:** Krib Host Dashboard (Short-Term Rental Platform)  
**Purpose:** Property management platform for short-term rental hosts in Dubai, UAE  
**Role in Ecosystem:** One of three platforms managed by central Super Admin  
**Date:** October 20, 2025

---

## 🎯 **Project Role in Ecosystem**

This is **Platform #1 of 3** in the Krib real estate ecosystem:

```
┌─────────────────────────────────────────────────────────┐
│              KRIB SUPER ADMIN DASHBOARD                 │
│         (Master Control for All Platforms)              │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  Platform 1  │   │  Platform 2  │   │  Platform 3  │
│              │   │              │   │              │
│ HOST         │   │ REAL ESTATE  │   │ CUSTOMER     │
│ DASHBOARD    │   │ AGENT        │   │ AI AGENT     │
│              │   │ (Long-term)  │   │ (Booking)    │
│ Short-term   │   │              │   │              │
│ Rentals      │   │ Rentals      │   │ Assistant    │
└──────────────┘   └──────────────┘   └──────────────┘
```

### **This Project's Specific Role:**

**Krib Host Dashboard** enables property owners to:
- List short-term rental properties (Dubai apartments, villas, etc.)
- Manage bookings (1 night to 30 days)
- Track earnings and receive payouts via Stripe
- Communicate with guests
- Provide property availability to AI booking agents

**NOT Handled by This Project:**
- Long-term rentals (6+ months) → Real Estate Agent Platform
- Customer-facing booking interface → Customer AI Agent Platform

---

## 🏗️ **System Architecture Overview**

### **Technology Stack:**

```
┌─────────────────────────────────────────────────────┐
│                    FRONTEND                          │
│  • React 18 + TypeScript                           │
│  • Vite (Build tool)                               │
│  • Tailwind CSS (Styling)                          │
│  • Hosted on: Vercel                               │
│  • URL: https://krib-host-dashboard.vercel.app     │
└─────────────────────────────────────────────────────┘
                         │
                         │ REST API
                         ▼
┌─────────────────────────────────────────────────────┐
│                    BACKEND                           │
│  • Python 3.11 + FastAPI                           │
│  • Uvicorn (ASGI server)                           │
│  • Pydantic (Data validation)                      │
│  • Hosted on: Render                               │
│  • URL: https://krib-host-dahsboard-backend.       │
│         onrender.com                                │
└─────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   DATABASE   │ │   STORAGE    │ │   SERVICES   │
│              │ │              │ │              │
│  Supabase    │ │  Supabase    │ │  Stripe      │
│  PostgreSQL  │ │  Storage     │ │  OpenAI      │
│              │ │  (Images)    │ │  Anthropic   │
└──────────────┘ └──────────────┘ └──────────────┘
```

---

## 📊 **Database Structure (Supabase PostgreSQL)**

### **Core Tables:**

#### **1. `users` Table**
Stores all platform users (hosts, admins, guests)
```sql
Key Fields:
- id (UUID) - Primary key
- email (unique) - User email
- role - 'host', 'admin', 'guest'
- name - Full name
- phone - Contact number
- stripe_account_id - For host payouts
- created_at - Registration date
```

**Current Count:** ~50+ users (mostly hosts)

---

#### **2. `properties` Table**
All listed properties (short-term rentals)
```sql
Key Fields:
- id (UUID) - Primary key
- user_id (UUID) - Host reference
- title - Property name
- description - Full description
- property_type - 'apartment', 'villa', 'studio', etc.
- bedrooms, bathrooms, max_guests
- base_price_per_night - Nightly rate in AED
- address (JSONB) - Full address with coordinates
- amenities (JSONB) - Array of amenities
- images (JSONB) - Array of image URLs
- status - 'active', 'inactive', 'pending'
- created_at, updated_at
```

**Current Count:** 174 properties (171 active)  
**Locations:** Dubai (all areas - Marina, Downtown, JBR, etc.)  
**Price Range:** AED 100-2000/night

---

#### **3. `bookings` Table**
All booking reservations
```sql
Key Fields:
- id (UUID) - Primary key
- property_id (UUID) - Property reference
- guest_id (UUID) - Guest user reference
- host_id (UUID) - Host user reference
- check_in, check_out - Dates
- number_of_guests - Guest count
- status - 'pending', 'confirmed', 'cancelled', 'completed'
- total_price - Total booking amount
- payment_status - 'pending', 'paid', 'refunded'
- stripe_payment_intent_id - Stripe payment reference
- special_requests - Guest notes
- created_at, updated_at
```

**Booking Lifecycle:**
1. Created → pending
2. Payment → confirmed
3. Check-in → active
4. Check-out → completed

---

#### **4. `availability` Table**
Property availability calendar
```sql
Key Fields:
- id (UUID)
- property_id (UUID)
- date - Specific date
- available (boolean)
- price_override - Custom price for date
- booking_id (UUID) - If booked
```

---

#### **5. `reviews` Table**
Guest reviews for properties
```sql
Key Fields:
- id (UUID)
- property_id, booking_id
- guest_id, host_id
- rating (1-5)
- comment
- response - Host response
- created_at
```

---

#### **6. `notifications` Table**
User notifications
```sql
Key Fields:
- id (UUID)
- user_id - Recipient
- type - 'booking', 'payment', 'review', etc.
- title, message
- read (boolean)
- created_at
```

---

#### **7. `webhook_subscriptions` Table**
External webhook registrations
```sql
Key Fields:
- id (UUID)
- subscriber_id - API key/service name
- url - Webhook endpoint
- events - Array of subscribed events
- active (boolean)
- secret - Webhook signature secret
```

---

#### **8. `stripe_transactions` Table** (Planned - Stripe Integration)
Financial transaction tracking
```sql
Key Fields:
- id (UUID)
- booking_id
- stripe_payment_intent_id
- amount_total - Full amount
- amount_platform_fee - 10% platform fee
- amount_host_payout - Host earnings
- status
- created_at
```

---

## 🔌 **API Structure**

### **Base URL:**
```
https://krib-host-dahsboard-backend.onrender.com
```

### **API Endpoints (Organized by Domain):**

#### **Authentication** (`/api/auth`)
```
POST   /register          - User registration
POST   /login             - User login
POST   /logout            - User logout
GET    /me                - Get current user
PUT    /profile           - Update profile
POST   /password/reset    - Password reset
```

#### **Properties** (`/api/v1/properties`)
```
GET    /                  - List all properties (paginated)
POST   /                  - Create property (host only)
GET    /{id}              - Get property details
PUT    /{id}              - Update property (host only)
DELETE /{id}              - Delete property (host only)
GET    /{id}/availability - Check availability
PUT    /{id}/availability - Update availability
POST   /{id}/images       - Upload property images
```

#### **Bookings** (`/api/v1/bookings`)
```
GET    /                  - List user's bookings
POST   /                  - Create booking
GET    /{id}              - Get booking details
PUT    /{id}              - Update booking
DELETE /{id}              - Cancel booking
POST   /{id}/confirm      - Confirm booking
POST   /{id}/complete     - Mark as completed
```

#### **External API** (`/api/v1/external`) - For AI Agents
```
GET    /properties/search           - Search properties
GET    /properties/{id}             - Property details
GET    /properties/{id}/availability - Check availability
GET    /properties/{id}/pricing     - Calculate pricing
POST   /bookings                    - Create booking
GET    /hosts/{id}/pending-bookings - Host's pending bookings
PUT    /bookings/{id}/status        - Update booking status
POST   /webhook-subscriptions       - Subscribe to webhooks
```

**Authentication:** Bearer token with API key
```
Authorization: Bearer krib_prod_c4323aa1d8896254316e396995bf7f6fffacdaa8985ec09da4067da37f1e6ae8
```

#### **Notifications** (`/api/v1/notifications`)
```
GET    /                  - List notifications
PUT    /{id}/read         - Mark as read
DELETE /{id}              - Delete notification
```

#### **Reviews** (`/api/v1/reviews`)
```
GET    /property/{id}     - Get property reviews
POST   /                  - Create review
PUT    /{id}              - Update review
DELETE /{id}              - Delete review
POST   /{id}/response     - Host response
```

#### **Analytics** (`/api/v1/analytics`)
```
GET    /host/dashboard    - Host dashboard stats
GET    /host/earnings     - Earnings overview
GET    /host/occupancy    - Occupancy rates
GET    /admin/overview    - Admin overview (admin only)
```

#### **Stripe** (`/api/v1/stripe`) - Payments (Planned)
```
POST   /host/create-account      - Create Stripe Connect
GET    /host/onboarding-link     - Get onboarding URL
POST   /payments/create-intent   - Create payment
POST   /payments/confirm         - Confirm payment
POST   /webhooks                 - Stripe webhook handler
```

#### **Uploads** (`/api/v1/upload`)
```
POST   /image             - Upload single image
POST   /images            - Upload multiple images
```

#### **Webhooks** (`/api/v1/webhooks`)
```
POST   /                  - Receive external webhooks
GET    /subscriptions     - List webhook subscriptions
POST   /subscriptions     - Create subscription
DELETE /subscriptions/{id} - Delete subscription
```

---

## 🔐 **Authentication & Authorization**

### **User Roles:**

1. **Guest** (Default)
   - Can: Browse properties, make bookings, leave reviews
   - Cannot: Create properties, access host dashboard

2. **Host**
   - Can: All guest permissions + create/manage properties, view earnings
   - Cannot: Access admin functions

3. **Admin**
   - Can: All permissions, manage users, view all data, platform settings
   - Super Admin will have: Cross-platform admin access

### **Authentication Methods:**

1. **Email/Password** (Supabase Auth)
   - Standard email + password login
   - Password reset via email

2. **OAuth** (Planned)
   - Google Sign-In
   - Apple Sign-In

3. **API Key** (External Services)
   - Bearer token authentication
   - Used by AI agents to access properties

### **Session Management:**
- JWT tokens via Supabase
- Token expiry: 1 hour
- Refresh tokens: 7 days
- Secure HTTP-only cookies

---

## 💰 **Revenue & Financial Model**

### **Revenue Streams:**

1. **Platform Commission: 10%**
   - Charged on every booking
   - Example: AED 1,000 booking → AED 100 platform fee

2. **Host Subscription** (Future)
   - Premium features for hosts
   - Enhanced listings
   - Priority support

### **Current Financial State:**
- **Properties:** 174 listed
- **Platform Fee:** 10% per booking
- **Payment Processing:** Stripe (2.9% + AED 1)
- **Host Payouts:** Via Stripe Connect (pending implementation)

### **Money Flow:**
```
Guest Payment (AED 1,000)
    ↓
Platform Receives (via Stripe)
    ↓
Deduct Platform Fee (10% = AED 100)
    ↓
Deduct Stripe Fee (~3% = AED 30)
    ↓
Transfer to Host (AED 870)
    ↓
Host Bank Account (1-2 business days)
```

---

## 📈 **Current Platform Statistics**

### **Properties:**
- **Total:** 174 properties
- **Active:** 171 properties
- **Inactive:** 3 properties
- **Locations:** Dubai (all major areas)
- **Types:** Apartments (60%), Villas (20%), Studios (15%), Penthouses (5%)

### **Users:**
- **Total Users:** ~50+
- **Hosts:** ~30
- **Guests:** ~20
- **Admins:** 2

### **Pricing:**
- **Average:** AED 450/night
- **Minimum:** AED 100/night
- **Maximum:** AED 2,000/night

### **Bookings:**
- **Status:** Growing (test data currently)
- **Average Stay:** 3-4 nights
- **Peak Season:** November - April

---

## 🔗 **External Integrations**

### **1. Supabase** (Database + Auth + Storage)
```
Project: host-dashoard-02
Region: East US (North Virginia)
Database: PostgreSQL 15
Storage: S3-compatible
```

**What It Provides:**
- PostgreSQL database hosting
- User authentication system
- File storage for property images
- Real-time subscriptions
- Row-level security (RLS)

**Connection:**
- REST API
- JavaScript client
- Direct PostgreSQL connection

---

### **2. Stripe** (Payments - Planned)
```
Mode: Test
Account Type: Standard (Platform)
```

**What It Will Provide:**
- Payment processing from guests
- Connect accounts for hosts
- Automated payouts
- Refund handling
- Webhook notifications

---

### **3. OpenAI** (AI Features)
```
Model: GPT-4
Use Cases:
- Property description generation
- Title suggestions
- Guest message responses
```

---

### **4. Anthropic Claude** (AI Features)
```
Model: Claude 3.5 Sonnet
Use Cases:
- Smart search
- Booking recommendations
```

---

### **5. Unsplash** (Property Images)
```
Purpose: Stock property photos
Usage: Default images for properties
API: Unsplash API
```

---

### **6. External AI Agents** (API Integration)
```
Authentication: API Key (Bearer token)
Access Level: Read properties, create bookings
Rate Limit: 200 requests/minute
Current Integrations: 1 AI booking agent
```

---

## 🌐 **Deployment & Infrastructure**

### **Frontend (Vercel):**
```
Platform: Vercel
Build: Vite
Framework: React 18
Deploy: Git push (auto-deploy)
Domain: krib-host-dashboard.vercel.app
CDN: Vercel Edge Network
SSL: Automatic (Let's Encrypt)
```

### **Backend (Render):**
```
Platform: Render
Service Type: Web Service
Runtime: Python 3.11
Server: Uvicorn (ASGI)
Deploy: Git push (auto-deploy from main branch)
Region: US East
Auto-scaling: Enabled
Health Check: /api/health
```

**Environment Variables (Render):**
```bash
# Database
SUPABASE_URL
SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY

# Storage
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
S3_BUCKET_NAME
S3_ENDPOINT_URL

# AI Services
OPENAI_API_KEY
ANTHROPIC_API_KEY

# Security
SECRET_KEY (auto-generated)
JWT_SECRET_KEY (auto-generated)
WEBHOOK_SECRET_KEY (auto-generated)

# External API
ENVIRONMENT=production
KRIB_AI_AGENT_API_KEY
HOST_DASHBOARD_WEBHOOK_SECRET

# Stripe (Planned)
STRIPE_SECRET_KEY
STRIPE_PUBLISHABLE_KEY
STRIPE_WEBHOOK_SECRET
```

### **Database (Supabase):**
```
Type: PostgreSQL 15
Hosting: Supabase Cloud
Region: US East
Backups: Daily automatic
Connection: Pooled (pgBouncer)
Max Connections: 100
```

### **Storage (Supabase Storage):**
```
Type: S3-compatible
Bucket: krib_host
CDN: Supabase CDN
Max File Size: 50MB
Allowed: Images (JPEG, PNG, WebP)
Public Access: Read-only
```

---

## 🔔 **Notifications & Webhooks**

### **Internal Notifications:**
Users receive notifications for:
- New bookings
- Booking confirmations
- Payment confirmations
- Review submissions
- Cancellations
- Messages

**Delivery Methods:**
- In-app notifications
- Email (via Supabase)
- Push notifications (planned)

### **External Webhooks:**
External systems can subscribe to events:

**Available Events:**
```
booking.created
booking.confirmed
booking.cancelled
booking.completed
property.created
property.updated
property.deleted
review.created
payment.succeeded
payment.failed
```

**Webhook Format:**
```json
{
  "event": "booking.created",
  "timestamp": "2025-10-20T12:00:00Z",
  "data": {
    "booking_id": "uuid",
    "property_id": "uuid",
    "check_in": "2025-11-01",
    "check_out": "2025-11-05",
    "total_price": 1860.0
  }
}
```

---

## 🔒 **Security Features**

### **Current Implementation:**

1. **Authentication:**
   - Supabase JWT tokens
   - Secure password hashing (bcrypt)
   - Token expiration (1 hour)

2. **Authorization:**
   - Role-based access control (RBAC)
   - Row-level security (RLS) in Supabase
   - API endpoint protection

3. **API Security:**
   - Rate limiting (100-200 req/min)
   - API key authentication for external services
   - CORS configuration
   - Request validation (Pydantic)

4. **Data Protection:**
   - HTTPS everywhere (TLS 1.3)
   - Environment variables for secrets
   - No sensitive data in logs
   - SQL injection prevention (parameterized queries)

5. **Payment Security (Planned):**
   - PCI DSS compliant (via Stripe)
   - No card data stored locally
   - Webhook signature verification

---

## 📊 **Logging & Monitoring**

### **Current Setup:**

**Backend Logging:**
- Python logging module
- Log levels: DEBUG, INFO, WARNING, ERROR
- Render logs dashboard

**Monitoring:**
- Render health checks (`/api/health`)
- Response time tracking
- Error rate monitoring

**Planned:**
- Sentry (Error tracking)
- LogRocket (User session replay)
- Grafana (Custom dashboards)

---

## 🎯 **What Super Admin Needs to Control**

### **User Management:**
- [ ] View all users (hosts, guests, admins)
- [ ] Create/edit/delete user accounts
- [ ] Change user roles
- [ ] Reset passwords
- [ ] Ban/suspend users
- [ ] View user activity logs

### **Property Management:**
- [ ] View all properties (across all hosts)
- [ ] Approve/reject new listings
- [ ] Edit property details
- [ ] Deactivate properties
- [ ] Bulk property operations
- [ ] Property performance metrics

### **Booking Management:**
- [ ] View all bookings (system-wide)
- [ ] Cancel bookings (with refunds)
- [ ] Resolve disputes
- [ ] Modify booking details
- [ ] Booking analytics
- [ ] Revenue reports

### **Financial Management:**
- [ ] View platform earnings
- [ ] Host payout management
- [ ] Transaction history
- [ ] Refund processing
- [ ] Financial reports (daily/monthly/yearly)
- [ ] Stripe dashboard access

### **Content Moderation:**
- [ ] Review property listings
- [ ] Moderate reviews
- [ ] Remove inappropriate content
- [ ] Verify host identities

### **Platform Settings:**
- [ ] Platform fee configuration
- [ ] Email templates
- [ ] Notification settings
- [ ] API rate limits
- [ ] Feature flags
- [ ] Maintenance mode

### **Analytics & Reports:**
- [ ] User growth metrics
- [ ] Booking trends
- [ ] Revenue analytics
- [ ] Property performance
- [ ] Search analytics
- [ ] Geographic distribution

### **External Integrations:**
- [ ] API key management
- [ ] Webhook subscriptions
- [ ] Third-party service status
- [ ] Integration logs

---

## 🔄 **Data Flow Summary**

### **Key Data Entities:**
```
Users (50+)
    ↓ owns
Properties (174)
    ↓ has
Availability Calendar
    ↓ generates
Bookings
    ↓ triggers
Payments
    ↓ creates
Transactions
    ↓ results in
Host Payouts
```

### **Inter-Platform Data Sharing (Future):**

**This Platform Provides:**
- Property availability data
- Host contact information
- Booking status
- Pricing information

**This Platform Receives:**
- Customer preferences (from AI Agent)
- Long-term property inquiries (from Real Estate Platform)
- Booking requests (from AI Agent)

---

## 📦 **Data Export Capabilities**

For Super Admin dashboard integration, this platform can export:

1. **User Data:**
   - User list (CSV/JSON)
   - User activity logs
   - Login history

2. **Property Data:**
   - Property listings (CSV/JSON)
   - Property performance metrics
   - Availability calendars

3. **Booking Data:**
   - Booking history (CSV/JSON)
   - Revenue reports
   - Occupancy rates

4. **Financial Data:**
   - Transaction logs
   - Platform earnings
   - Host payouts

**API Endpoints for Super Admin:**
```
GET /api/v1/admin/export/users
GET /api/v1/admin/export/properties
GET /api/v1/admin/export/bookings
GET /api/v1/admin/export/transactions
GET /api/v1/admin/export/analytics
```

---

## 🚀 **Future Enhancements**

### **Planned Features:**
1. ✅ Stripe Connect integration (in progress)
2. ⏳ Multi-language support (Arabic + English)
3. ⏳ Mobile app (React Native)
4. ⏳ Smart pricing algorithm
5. ⏳ Calendar sync (Airbnb, Booking.com)
6. ⏳ Instant booking option
7. ⏳ Guest messaging system
8. ⏳ Host verification badges

---

## 📞 **Technical Contacts & Resources**

### **Repositories:**
- **GitHub:** `mahmoudomarus/Krib_host_dahsboard`
- **Branch:** `main`

### **Key URLs:**
- **Frontend:** https://krib-host-dashboard.vercel.app
- **Backend:** https://krib-host-dahsboard-backend.onrender.com
- **API Docs:** /api/docs (Swagger)
- **Health Check:** /api/health

### **Database:**
- **Supabase Project:** host-dashoard-02
- **Dashboard:** https://supabase.com/dashboard/project/bpomacnqaqzgeuahhlka

---

## 🎯 **Key Metrics for Super Admin Dashboard**

### **Platform Health:**
- Total users (50+)
- Active properties (171)
- Monthly bookings
- Revenue (AED)
- Average booking value
- Platform uptime (99.9%)

### **Growth Metrics:**
- User registration rate
- Property listing rate
- Booking conversion rate
- Revenue growth (MoM)

### **Operational Metrics:**
- Response time (avg < 500ms)
- Error rate (< 0.1%)
- API usage
- External API calls

---

**Summary:** This platform is a fully functional short-term rental management system with 174 properties, robust API, external AI agent integration, and planned Stripe payment processing. The Super Admin will need comprehensive access to manage users, properties, bookings, finances, and platform settings across this and two other platforms in the ecosystem.

**Next Step:** Use this document as a blueprint for what the Super Admin needs to control from this platform.

