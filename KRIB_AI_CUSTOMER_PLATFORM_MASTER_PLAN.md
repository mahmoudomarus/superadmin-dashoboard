# 🏠 Krib AI Customer Platform - Master Plan & Architecture

**Last Updated**: October 29, 2025  
**Status**: 🟢 LIVE (Render + Vercel)  
**Version**: 2.0

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Current Architecture](#current-architecture)
3. [Payment Integration Plan (Stripe Connect)](#payment-integration-plan)
4. [Integration with Host Dashboard](#integration-with-host-dashboard)
5. [API Endpoints Summary](#api-endpoints-summary)
6. [Deployment Architecture](#deployment-architecture)
7. [Future: Super Admin Integration](#future-super-admin-integration)

---

## 1. 📖 Project Overview

### **What is Krib AI Customer Platform?**

**Krib AI Customer Platform** is the **customer-facing AI agent** that helps users find, book, and manage properties in Dubai. It's the "front door" to the entire Krib ecosystem.

### **Role in the Ecosystem:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    KRIB ECOSYSTEM                                │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐         ┌──────────────────────┐
│  Krib AI Customer    │         │  Host Dashboard      │
│  Platform            │◄───────►│  (Property Mgmt)     │
│  (This Project)      │  API    │                      │
└──────────────────────┘         └──────────────────────┘
         │                                   │
         │                                   │
         ├─ AI Agent (Claude)                ├─ Property listings
         ├─ Property search                  ├─ Availability mgmt
         ├─ Booking management               ├─ Host tools
         ├─ Payment processing (NEW)         ├─ Analytics
         ├─ User authentication              └─ Booking confirmations
         └─ Chat interface
                  │
                  ▼
         ┌──────────────────────┐
         │  External Services   │
         ├──────────────────────┤
         │ - Stripe (payments)  │
         │ - Supabase (auth/db) │
         │ - UAE PASS (optional)│
         └──────────────────────┘
```

### **Key Responsibilities:**

| Responsibility | Description |
|----------------|-------------|
| **AI Concierge** | Natural language property search & recommendations |
| **Property Discovery** | Search 171+ short-term & long-term rentals in Dubai |
| **Market Research** | Price analysis, comparisons, statistics |
| **Booking Engine** | Handle reservations, viewings, payments |
| **User Management** | Authentication, profiles, preferences |
| **Payment Gateway** | Process payments, splits, refunds (via Stripe) |
| **Communication** | Chat interface, notifications, confirmations |

### **Technology Stack:**

- **Backend**: Python FastAPI (Render)
- **Frontend**: Next.js 14 + TypeScript (Vercel)
- **AI**: Claude Sonnet 4.5 (Anthropic)
- **Database**: Supabase (PostgreSQL)
- **Payments**: Stripe Connect (to be implemented)
- **Auth**: Supabase Auth + optional UAE PASS

---

## 2. 🏗️ Current Architecture

### **Live Deployment:**

```
Frontend (Vercel)                Backend (Render)
https://krib.ai              https://krib-backend.onrender.com
     │                                  │
     │                                  │
     ├─ Next.js 14                      ├─ FastAPI
     ├─ React Components                ├─ AI Agent (Claude)
     ├─ Tailwind CSS                    ├─ Property API Clients
     ├─ Property Cards UI               ├─ Unified Property Service
     └─ Chat Interface                  └─ Tool System
                  │                            │
                  └────────────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    │                    │
              Supabase DB          Host Dashboard API
         (Users, Bookings)      (Properties, Availability)
```

### **Property System (Recently Fixed):**

✅ **PropertySearchTool** - Search properties (amenities, filters, loading states)  
✅ **MarketResearchTool** - Market analytics (average prices, comparisons)  
✅ **PropertyBookingTool** - Handle bookings & viewings (payment integration needed)  
✅ **UnifiedPropertyService** - Route between short-term & long-term platforms

### **Current Integrations:**

| Service | Purpose | Status |
|---------|---------|--------|
| Host Dashboard API | Short-term rentals (174 properties) | ✅ LIVE |
| Real Estate API | Long-term leases | ✅ LIVE |
| Supabase Auth | User authentication | ✅ LIVE |
| Claude AI | Natural language interface | ✅ LIVE |
| UAE PASS | Identity verification | 📝 PLANNED |
| Stripe | Payment processing | 📝 NEXT |

---

## 3. 💳 Payment Integration Plan (Stripe Connect)

### **Overview:**

We'll use **Stripe Connect** to enable:
- ✅ Split payments between Krib (platform fee) and hosts
- ✅ AI agent auto-booking (off-session payments)
- ✅ Security deposits (manual capture)
- ✅ Refunds & cancellations

### **Architecture:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    STRIPE CONNECT ARCHITECTURE                   │
└─────────────────────────────────────────────────────────────────┘

        Krib Platform Account (Connected Account Manager)
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    Host A              Host B              Host C
  (Connect Acct)      (Connect Acct)      (Connect Acct)
        │                   │                   │
        └───────────────────┴───────────────────┘
                            │
                    Guest Payment (Customer)
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
   Host Receives 90%                  Krib Keeps 10%
   (transfer_data.destination)        (application_fee_amount)
```

### **Two Payment Flows:**

#### **Flow A: Interactive One-Shot Checkout**

**Use Case**: User manually books a property through the AI

```python
# 1. Create PaymentIntent
payment_intent = stripe.PaymentIntent.create(
    amount=5000,  # AED 50.00 (example)
    currency="aed",
    automatic_payment_methods={"enabled": True},
    transfer_data={
        "destination": host_stripe_account_id,  # Host gets this
    },
    application_fee_amount=500,  # Krib fee (10% = AED 5.00)
    metadata={
        "booking_id": "booking_123",
        "property_id": "prop_456",
        "user_id": "user_789"
    }
)

# 2. Frontend: Confirm with Stripe Payment Element
# 3. Webhook: Handle payment_intent.succeeded
# 4. Create booking in database
# 5. Notify host via Host Dashboard API
```

**Flow:**
```
User → AI Agent → "Book this property"
    ↓
Create PaymentIntent (Krib backend)
    ↓
Show Payment Element (frontend)
    ↓
User enters card details
    ↓
Stripe processes payment
    ↓
Webhook → Create booking → Notify host
```

---

#### **Flow B: AI Auto-Booking (Off-Session)**

**Use Case**: AI agent books automatically for user (recurring, scheduled)

**Step 1: Save card on file (first time only)**

```python
# Create Customer + SetupIntent
customer = stripe.Customer.create(
    email=user_email,
    metadata={"user_id": user_id}
)

setup_intent = stripe.SetupIntent.create(
    customer=customer.id,
    payment_method_types=["card"],
    usage="off_session"
)

# Frontend: Confirm SetupIntent with card details
# Store payment_method_id in database
```

**Step 2: AI auto-books later**

```python
# AI decides to book property
payment_intent = stripe.PaymentIntent.create(
    amount=5000,
    currency="aed",
    customer=customer_id,
    payment_method=saved_payment_method_id,
    off_session=True,  # No user interaction
    confirm=True,  # Immediately charge
    transfer_data={"destination": host_account_id},
    application_fee_amount=500,
    metadata={
        "booking_id": "booking_123",
        "booked_by": "ai_agent"
    }
)

# If 3DS/SCA required:
# → Catch CardError
# → Send notification to user: "Please confirm payment"
# → Show approval screen in app
```

**Flow:**
```
AI Agent analyzes user preferences
    ↓
Finds perfect property
    ↓
Checks saved payment method
    ↓
Creates PaymentIntent (off_session=True)
    ↓
If successful → Booking confirmed
If SCA required → Notify user for approval
```

---

### **Security Deposits (Optional)**

**Use Case**: Hold deposit for property damage, cancellations

```python
# Create hold (don't capture yet)
deposit_intent = stripe.PaymentIntent.create(
    amount=2000,  # AED 200 deposit
    currency="aed",
    capture_method="manual",  # Hold funds, don't capture
    customer=customer_id,
    payment_method=saved_payment_method_id,
    off_session=True,
    confirm=True,
    metadata={
        "type": "security_deposit",
        "booking_id": "booking_123"
    }
)

# Later (after checkout):
# Option 1: Capture (charge the deposit)
stripe.PaymentIntent.capture(deposit_intent.id)

# Option 2: Cancel (release the hold)
stripe.PaymentIntent.cancel(deposit_intent.id)
```

---

### **Refunds & Cancellations**

```python
# Cancel booking = refund payment
refund = stripe.Refund.create(
    payment_intent=payment_intent_id,
    amount=5000,  # Full refund
    refund_application_fee=True,  # Also refund Krib's fee
    reason="requested_by_customer"
)

# Partial refund (e.g., cancellation fee)
refund = stripe.Refund.create(
    payment_intent=payment_intent_id,
    amount=2500,  # 50% refund
    refund_application_fee=False  # Keep Krib's fee
)
```

---

### **Fee Structure:**

| Scenario | Host Receives | Krib Fee | Total |
|----------|---------------|----------|-------|
| Booking (AED 500/night × 3 nights) | AED 1,350 | AED 150 (10%) | AED 1,500 |
| Security Deposit (AED 200) | AED 200 | AED 0 | AED 200 |
| Cancellation Fee (50% refund) | AED 675 | AED 75 | AED 750 |

---

## 4. 🔗 Integration with Host Dashboard

### **What We Need from Host Dashboard:**

| Requirement | Endpoint | Why We Need It |
|-------------|----------|----------------|
| **Host's Stripe Account ID** | `GET /api/v1/hosts/{host_id}/stripe-account` | To send payments via `transfer_data.destination` |
| **Booking Confirmation** | `POST /api/v1/external/bookings` | Create booking on host side |
| **Pricing Validation** | `GET /api/v1/properties/{id}/pricing` | Verify price before charging |
| **Availability Check** | `GET /api/v1/properties/{id}/availability` | Prevent double-booking |
| **Booking Status Update** | `PATCH /api/v1/external/bookings/{id}/status` | Update status (confirmed, cancelled) |

### **New Endpoint Needed on Host Dashboard:**

```http
GET /api/v1/hosts/{host_id}/stripe-account
Authorization: Bearer krib_prod_xxx

Response:
{
  "success": true,
  "data": {
    "host_id": "host_123",
    "stripe_account_id": "acct_xxxxxxxxxxxxxx",
    "charges_enabled": true,
    "payouts_enabled": true
  }
}
```

### **Payment Flow Between Systems:**

```
Krib AI Customer Platform          Host Dashboard
        │                                 │
        │  1. Check property availability │
        ├────────────────────────────────>│
        │                                 │
        │  2. Get host Stripe account ID  │
        ├────────────────────────────────>│
        │                                 │
        │  3. Create Stripe PaymentIntent │
        │     with transfer_data          │
        │                                 │
        │  4. Process payment (Stripe)    │
        │                                 │
        │  5. Send booking confirmation   │
        ├────────────────────────────────>│
        │                                 │
        │  6. Host receives notification  │
        │                                 │
        ▼                                 ▼
```

---

## 5. 🛠️ API Endpoints Summary

### **New Stripe Endpoints (Krib Backend):**

```
POST   /api/stripe/guest/create-setup-intent
       → Save card on file for off-session payments

POST   /api/stripe/booking/authorize
       → Create PaymentIntent (manual capture for deposits)

POST   /api/stripe/booking/confirm
       → Confirm payment (interactive checkout)

POST   /api/stripe/booking/capture
       → Capture held payment (after stay)

POST   /api/stripe/booking/cancel
       → Cancel PaymentIntent or void hold

POST   /api/stripe/refund
       → Process refund (full or partial)

POST   /api/stripe/webhook
       → Handle Stripe events (payment_intent.succeeded, etc.)

GET    /api/stripe/payment-methods
       → List user's saved payment methods

DELETE /api/stripe/payment-methods/{pm_id}
       → Remove saved payment method
```

### **Database Schema Updates:**

```sql
-- payments table
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    booking_id UUID REFERENCES bookings(id),
    stripe_payment_intent_id TEXT UNIQUE NOT NULL,
    amount INTEGER NOT NULL, -- in fils (AED cents)
    currency TEXT DEFAULT 'aed',
    status TEXT NOT NULL, -- 'pending', 'succeeded', 'failed', 'refunded'
    payment_type TEXT NOT NULL, -- 'booking', 'deposit', 'refund'
    host_stripe_account_id TEXT,
    application_fee_amount INTEGER,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- saved_payment_methods table
CREATE TABLE saved_payment_methods (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    stripe_customer_id TEXT NOT NULL,
    stripe_payment_method_id TEXT NOT NULL,
    card_brand TEXT, -- 'visa', 'mastercard', etc.
    card_last4 TEXT,
    card_exp_month INTEGER,
    card_exp_year INTEGER,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add to bookings table
ALTER TABLE bookings ADD COLUMN payment_id UUID REFERENCES payments(id);
ALTER TABLE bookings ADD COLUMN payment_status TEXT DEFAULT 'pending';
ALTER TABLE bookings ADD COLUMN deposit_payment_id UUID REFERENCES payments(id);
```

---

## 6. 🚀 Deployment Architecture

### **Current Live Setup:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRODUCTION ENVIRONMENT                        │
└─────────────────────────────────────────────────────────────────┘

Frontend (Vercel)
├─ Domain: https://krib.ai
├─ Build: Next.js (automatic deployments on git push)
├─ Environment Variables:
│  ├─ NEXT_PUBLIC_API_URL
│  ├─ NEXT_PUBLIC_SUPABASE_URL
│  └─ NEXT_PUBLIC_SUPABASE_ANON_KEY

Backend (Render)
├─ Domain: https://krib-backend.onrender.com
├─ Service: Python (FastAPI)
├─ Auto-deploy: main branch
├─ Environment Variables:
│  ├─ HOST_DASHBOARD_API_KEY (krib_prod_xxx)
│  ├─ REAL_ESTATE_API_KEY
│  ├─ SUPABASE_URL
│  ├─ SUPABASE_SERVICE_KEY
│  ├─ ANTHROPIC_API_KEY (Claude)
│  ├─ STRIPE_SECRET_KEY (NEW)
│  └─ STRIPE_WEBHOOK_SECRET (NEW)

Database (Supabase)
├─ PostgreSQL (hosted)
├─ Auth enabled
└─ Row Level Security (RLS)
```

### **New Environment Variables for Stripe:**

```bash
# Add to Render environment variables
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
STRIPE_PLATFORM_ACCOUNT_ID=acct_xxxxxxxxxxxxx
STRIPE_APPLICATION_FEE_PERCENT=10  # 10% fee
```

### **Deployment Process:**

```bash
# 1. Push code to GitHub
git push origin main

# 2. Automatic deployments:
# ✅ Vercel: Rebuilds frontend (2-3 mins)
# ✅ Render: Rebuilds backend (5-7 mins)

# 3. Verify deployment:
curl https://krib-backend.onrender.com/api/health
curl https://krib.ai/api/health
```

---

## 7. 🔮 Future: Super Admin Integration

### **What Super Admin Will Do:**

The **Super Admin Dashboard** will be a separate project that orchestrates the entire Krib ecosystem.

**Super Admin's Role:**
- 🔧 Manage all platforms (Customer, Host, Real Estate, etc.)
- 📊 View cross-platform analytics
- 💰 Monitor payment splits & fees
- 🏢 Onboard new hosts to Stripe Connect
- 🛠️ Configure platform settings
- 📈 Generate financial reports
- 👥 Manage users across all platforms

### **How Super Admin Connects to This Project:**

```
Super Admin Dashboard
        │
        ├─ READ: User analytics, bookings, revenue
        ├─ WRITE: Feature flags, configuration
        ├─ CONTROL: Enable/disable integrations
        └─ MONITOR: Health checks, error logs

        ↓

Krib AI Customer Platform (This Project)
        │
        ├─ Exposes admin API endpoints
        ├─ Reports metrics to Super Admin
        ├─ Receives configuration updates
        └─ Shares authentication (Supabase)
```

**Admin API Endpoints (Future):**

```
GET    /admin/api/analytics/bookings
GET    /admin/api/analytics/revenue
GET    /admin/api/users
PATCH  /admin/api/users/{id}/status
GET    /admin/api/payments/transactions
POST   /admin/api/config/feature-flags
GET    /admin/api/health/detailed
```

---

## 📊 Implementation Timeline

### **Phase 1: Stripe Setup (Week 1)**
- [ ] Create Stripe Connect platform account
- [ ] Add environment variables to Render
- [ ] Implement basic PaymentIntent flow
- [ ] Test with Stripe test mode

### **Phase 2: Backend Implementation (Week 1-2)**
- [ ] Create Stripe service (`backend/services/stripe_service.py`)
- [ ] Add payment endpoints (`backend/api_endpoints/stripe_endpoints.py`)
- [ ] Database migrations (payments, saved_payment_methods)
- [ ] Webhook handler
- [ ] Integration with PropertyBookingTool

### **Phase 3: Frontend Implementation (Week 2)**
- [ ] Stripe Elements integration
- [ ] Payment form component
- [ ] Saved cards UI
- [ ] Booking confirmation flow
- [ ] Error handling & loading states

### **Phase 4: Host Dashboard Coordination (Week 2-3)**
- [ ] Request Stripe account ID endpoint
- [ ] Test payment splitting
- [ ] Verify booking creation on host side
- [ ] Test refund flow

### **Phase 5: Testing & Launch (Week 3-4)**
- [ ] Test in Stripe test mode
- [ ] Test all payment scenarios
- [ ] Security audit
- [ ] Go live with production keys

---

## 🔒 Security Considerations

### **PCI Compliance:**
✅ **Never store card details** - Stripe handles all sensitive data  
✅ **Use Stripe Elements** - Pre-built secure forms  
✅ **HTTPS only** - All API calls over TLS  
✅ **Webhook signature verification** - Validate Stripe webhooks

### **Payment Security:**
- ✅ Validate amounts server-side (never trust frontend)
- ✅ Check property availability before charging
- ✅ Implement rate limiting on payment endpoints
- ✅ Log all payment attempts for audit trail
- ✅ Use idempotency keys to prevent duplicate charges

### **User Data:**
- ✅ Hash Emirates ID (if using UAE PASS)
- ✅ Store minimal payment metadata
- ✅ Comply with UAE data protection laws

---

## 📞 Key Contacts & Resources

| Service | URL | Purpose |
|---------|-----|---------|
| **Stripe Dashboard** | https://dashboard.stripe.com | Payment management |
| **Stripe Connect Docs** | https://stripe.com/docs/connect | Integration guide |
| **Host Dashboard API** | https://krib-host-dahsboard-backend.onrender.com | Property & booking API |
| **Supabase Dashboard** | https://supabase.com/dashboard | Database management |
| **Render Dashboard** | https://dashboard.render.com | Backend deployment |
| **Vercel Dashboard** | https://vercel.com/dashboard | Frontend deployment |

---

## ✅ Success Metrics

Track these KPIs after payment integration:

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| **Payment Success Rate** | > 95% | Minimize failed transactions |
| **Average Transaction Time** | < 3 seconds | Fast checkout experience |
| **Refund Rate** | < 5% | Quality bookings |
| **AI Auto-Booking Success** | > 90% | Off-session payments work |
| **Saved Card Usage** | > 60% | Repeat bookings easier |

---

## 🎯 Summary

**Krib AI Customer Platform** is the customer-facing AI agent for property search and booking in Dubai. It integrates with:
- **Host Dashboard** (property data, bookings)
- **Stripe Connect** (payments, splits, refunds)
- **Supabase** (auth, database)
- **Claude AI** (natural language interface)

**Next Steps:**
1. ✅ Setup Stripe Connect account
2. ✅ Coordinate with Host Dashboard team for Stripe account ID endpoint
3. ✅ Implement payment flows (interactive + off-session)
4. ✅ Test thoroughly in staging
5. ✅ Deploy to production

**Timeline**: 3-4 weeks for full payment integration

**Status**: Ready to implement. All architecture documented, code patterns ready.

---

**Questions?** This is the single source of truth for Krib AI Customer Platform. Update this document as architecture evolves.

