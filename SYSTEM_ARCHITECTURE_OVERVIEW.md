# 🏗️ Krib AI Platform - System Architecture Overview

## 📋 Complete System Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          KRIB AI PLATFORM ARCHITECTURE                      │
└─────────────────────────────────────────────────────────────────────────────┘

                                [SUPERADMIN DASHBOARD]
                                         │
                           ┌─────────────┴──────────────┐
                           │      Oversight & Control    │
                           │  - User Management          │
                           │  - Dispute Resolution       │
                           │  - Payment Oversight        │
                           │  - Analytics & Reports      │
                           │  - System Configuration     │
                           └─────────────┬──────────────┘
                                         │
                                         ▼
        ┌────────────────────────────────────────────────────────────┐
        │                    BACKEND API (Render)                    │
        │                                                            │
        │  ┌──────────────────────────────────────────────────────┐ │
        │  │         PROPERTY SERVICES                            │ │
        │  │  - Search (Short-term + Long-term)                  │ │
        │  │  - Booking Management                                │ │
        │  │  - Payment Processing (Stripe)                       │ │
        │  │  - Pricing & Availability                            │ │
        │  └──────────────────────────────────────────────────────┘ │
        │                                                            │
        │  ┌──────────────────────────────────────────────────────┐ │
        │  │         AI AGENT SERVICES                            │ │
        │  │  - Natural Language Processing                       │ │
        │  │  - Intent Detection (Short/Long-term)                │ │
        │  │  - Tool Execution                                    │ │
        │  │  - Multi-tier LLM Routing                            │ │
        │  └──────────────────────────────────────────────────────┘ │
        │                                                            │
        │  ┌──────────────────────────────────────────────────────┐ │
        │  │         MESSAGING & DISPUTES                         │ │
        │  │  - Guest-Host Messaging                              │ │
        │  │  - AI-Facilitated Communication                      │ │
        │  │  - Dispute Creation & Tracking                       │ │
        │  │  - Complaint Management                              │ │
        │  └──────────────────────────────────────────────────────┘ │
        │                                                            │
        │  ┌──────────────────────────────────────────────────────┐ │
        │  │         AUTHENTICATION & AUTHORIZATION               │ │
        │  │  - Supabase Auth (Email, Google, GitHub)             │ │
        │  │  - UAE PASS Integration (Optional)                   │ │
        │  │  - API Key Management                                │ │
        │  │  - Role-Based Access Control                         │ │
        │  └──────────────────────────────────────────────────────┘ │
        └─────────────────────────┬──────────────────────────────────┘
                                  │
                     ┌────────────┴────────────┐
                     ▼                         ▼
        ┌──────────────────────┐  ┌──────────────────────┐
        │  EXTERNAL PROPERTY   │  │    STRIPE PAYMENTS   │
        │      APIS            │  │                      │
        │                      │  │  - PaymentIntents    │
        │  • Host Dashboard    │  │  - SetupIntents      │
        │    (Short-term)      │  │  - Customers         │
        │    174 Properties    │  │  - Refunds           │
        │                      │  │  - Security Deposits │
        │  • Real Estate API   │  │  - Stripe Connect    │
        │    (Long-term)       │  │    (Host Payouts)    │
        │                      │  │                      │
        └──────────────────────┘  └──────────────────────┘
                                  
                     │
                     ▼
        ┌─────────────────────────────────┐
        │      DATABASE (Supabase)        │
        │                                 │
        │  Tables:                        │
        │  • auth.users                   │
        │  • property_bookings            │
        │  • property_messages            │
        │  • booking_disputes             │
        │  • stripe_customers             │
        │  • user_verification            │
        │  • audit_logs                   │
        │                                 │
        │  Features:                      │
        │  • Row Level Security (RLS)     │
        │  • Real-time Subscriptions      │
        │  • Storage (Images, Documents)  │
        └─────────────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────┐
        │   FRONTEND (Vercel/Next.js)     │
        │                                 │
        │  Pages:                         │
        │  • Property Search              │
        │  • Chat with AI Agent           │
        │  • Booking Management           │
        │  • Messaging Interface          │
        │  • Payment Methods              │
        │  • User Profile                 │
        │                                 │
        │  Components:                    │
        │  • PropertySearchTool           │
        │  • BookingToolView              │
        │  • MessageThread                │
        │  • AddPaymentMethodModal        │
        │  • DisputeForm                  │
        └─────────────────────────────────┘
                     │
                     ▼
           ┌─────────────────────┐
           │   END USERS          │
           │                      │
           │  • Guests            │
           │  • Hosts             │
           │  • Property Owners   │
           └─────────────────────┘
```

---

## 🔄 Data Flow Examples

### 1. Property Search Flow

```
User Query: "Find a 2-bedroom apartment in Dubai Marina under 500 AED/night"
    │
    ├──► Frontend (Chat Interface)
    │
    ├──► Backend AI Agent
    │     ├─► Intent Detection → "short_term_rental"
    │     ├─► Extract Parameters → {bedrooms: 2, area: "Dubai Marina", max_price: 500}
    │     └─► Execute Tool → PropertySearchTool
    │
    ├──► UnifiedPropertyService
    │     └─► Route to HostDashboardClient (short-term)
    │
    ├──► Host Dashboard API
    │     └─► GET /api/v1/properties/search?city=Dubai%20Marina&bedrooms=2&max_price=500
    │
    ├──► Response: 15 properties found
    │
    ├──► AI Agent formats results
    │
    └──► Frontend displays property cards with booking options
```

### 2. Booking with Payment Flow

```
User: "Book property #5 for Nov 1-5"
    │
    ├──► AI Agent: PropertyBookingTool.create_booking()
    │     ├─► Check user has payment method saved
    │     ├─► If no payment method → Request user to add card
    │     └─► If payment method exists → Proceed
    │
    ├──► PropertyPaymentService.complete_booking_with_payment()
    │     ├─► Create Stripe PaymentIntent
    │     ├─► Charge card
    │     ├─► Create booking in Host Dashboard
    │     ├─► Process payment in Host Dashboard
    │     ├─► Calculate host payout (85%, 15% platform fee)
    │     └─► Save booking in local Supabase DB
    │
    ├──► Response: Booking confirmed + Payment successful
    │
    ├──► Notifications sent:
    │     ├─► Email to guest (confirmation)
    │     ├─► Email to host (new booking)
    │     └─► SMS to guest (optional)
    │
    └──► Frontend: Show booking confirmation
```

### 3. Guest Complaint Flow

```
Guest: "The apartment is dirty and WiFi doesn't work"
    │
    ├──► AI Agent assesses severity
    │     ├─► Severity: MEDIUM (property_condition)
    │     └─► Decision: File complaint + Message host
    │
    ├──► ai_file_complaint()
    │     ├─► Create dispute in booking_disputes table
    │     ├─► Priority: MEDIUM
    │     ├─► Status: OPEN
    │     └─► Notify superadmin
    │
    ├──► ai_send_message_to_host()
    │     ├─► Send message: "Guest reporting cleanliness issue and WiFi problem"
    │     └─► Mark as urgent
    │
    ├──► Superadmin Dashboard receives alert
    │     └─► Dispute #12345 - Property Condition - Medium Priority
    │
    ├──► Superadmin reviews:
    │     ├─► View guest messages
    │     ├─► View host response (if any)
    │     ├─► Check property history
    │     └─► Make decision
    │
    ├──► Resolution: Partial refund + Warning to host
    │     ├─► Refund 20% to guest
    │     ├─► Send warning to host
    │     └─► Update dispute status to RESOLVED
    │
    └──► Both parties notified of resolution
```

### 4. Host-Guest Messaging Flow

```
Guest: "Can I check in early at 12pm instead of 3pm?"
    │
    ├──► AI Agent: ai_send_message_to_host()
    │     ├─► Create message in property_messages table
    │     ├─► sender_role: 'ai_agent' (on behalf of guest)
    │     ├─► recipient_role: 'host'
    │     └─► message_type: 'text'
    │
    ├──► Host receives notification:
    │     ├─► Real-time push notification
    │     ├─► Email notification
    │     └─► SMS notification (if enabled)
    │
    ├──► Host replies: "Yes, early check-in is fine!"
    │     ├─► Create message in property_messages table
    │     ├─► sender_role: 'host'
    │     └─► recipient_role: 'guest'
    │
    ├──► Guest receives notification
    │
    └──► AI Agent sees response and informs guest:
          "Great news! The host confirmed early check-in at 12pm is available."
```

---

## 🔐 Security Architecture

### Authentication Layers

```
┌─────────────────────────────────────────────────────────┐
│                   AUTHENTICATION FLOW                    │
└─────────────────────────────────────────────────────────┘

1. User Authentication (Supabase Auth)
   ├─► Email/Password
   ├─► Google OAuth
   ├─► GitHub OAuth
   └─► UAE PASS (Optional, for verification)

2. API Key Authentication (for external/superadmin)
   ├─► HOST_DASHBOARD_API_KEY → Short-term properties
   ├─► REAL_ESTATE_API_KEY → Long-term properties
   └─► SUPERADMIN_API_KEY → Full system access

3. Row Level Security (Supabase RLS)
   ├─► Users can only see their own data
   ├─► Hosts can see their property bookings
   ├─► Admins bypass RLS with service_role key
   └─► AI Agent uses service_role for cross-user operations

4. Payment Security (Stripe PCI Compliance)
   ├─► No card data stored in our DB
   ├─► Stripe Elements for secure card input
   ├─► 3D Secure (SCA) for EU/UK cards
   └─► Webhook signature verification
```

### Authorization Matrix

| Role       | Search Properties | Book Properties | View Own Bookings | Message Host | File Dispute | Resolve Dispute | Manage Users | System Config |
|------------|-------------------|-----------------|-------------------|--------------|--------------|-----------------|--------------|---------------|
| Guest      | ✅                | ✅              | ✅                | ✅           | ✅           | ❌              | ❌           | ❌            |
| Host       | ✅                | ❌              | ✅ (as host)      | ✅           | ✅           | ❌              | ❌           | ❌            |
| AI Agent   | ✅                | ✅ (on behalf)  | ✅                | ✅           | ✅           | ❌              | ❌           | ❌            |
| Superadmin | ✅                | ✅              | ✅ (all)          | ✅           | ✅           | ✅              | ✅           | ✅            |

---

## 📊 Database Schema Summary

### Core Tables

**1. `auth.users` (Supabase managed)**
- User authentication and profile
- Email, auth provider, metadata

**2. `property_bookings`**
- All booking records
- Links: user, property, payment, host
- Tracks: check-in/out, guests, amount, status

**3. `property_messages`**
- Guest-Host-AI communications
- Links: booking, sender, recipient
- Tracks: delivery, read status, flagging

**4. `booking_disputes`**
- Complaints and disputes
- Links: booking, complainant, defendant, admin
- Tracks: type, priority, status, resolution

**5. `stripe_customers`**
- Maps Supabase users to Stripe customers
- Enables saved payment methods

**6. `message_attachments`**
- Image/document evidence for disputes
- Links to messages

**7. `user_verification`**
- UAE PASS verification status
- Identity verification records

**8. `audit_logs`**
- All superadmin actions
- System-wide activity tracking

---

## 🚀 Deployment Architecture

```
┌───────────────────────────────────────────────────────┐
│                 PRODUCTION ENVIRONMENT                │
└───────────────────────────────────────────────────────┘

Frontend (Vercel)
├─► Domain: https://krib.ai
├─► Framework: Next.js 15
├─► Deploy: git push → auto-deploy
└─► Environment Variables:
    ├─► NEXT_PUBLIC_SUPABASE_URL
    ├─► NEXT_PUBLIC_SUPABASE_ANON_KEY
    ├─► NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
    └─► NEXT_PUBLIC_API_URL

Backend (Render)
├─► Domain: https://krib-backend.onrender.com
├─► Framework: FastAPI (Python)
├─► Deploy: git push → auto-deploy
└─► Environment Variables:
    ├─► SUPABASE_URL
    ├─► SUPABASE_SERVICE_ROLE_KEY
    ├─► HOST_DASHBOARD_API_KEY (or KRIB_AI_AGENT_API_KEY)
    ├─► REAL_ESTATE_API_KEY
    ├─► STRIPE_SECRET_KEY
    ├─► STRIPE_WEBHOOK_SECRET
    ├─► SUPERADMIN_API_KEY
    ├─► OPENAI_API_KEY
    └─► ANTHROPIC_API_KEY

Database (Supabase)
├─► Postgres Database
├─► Real-time Engine
├─► Storage (for attachments)
└─► Auth Service

Payments (Stripe)
├─► Payment Processing
├─► Stripe Connect (Host Payouts)
└─► Webhooks to Render

External APIs
├─► Host Dashboard (Short-term properties)
├─► Real Estate API (Long-term properties)
└─► UAE PASS (Optional verification)
```

---

## 📈 Monitoring & Observability

### Key Metrics to Track

**1. User Metrics**
- Active users (daily/monthly)
- New signups
- User retention rate
- Verification completion rate

**2. Booking Metrics**
- Bookings created
- Booking value (total revenue)
- Conversion rate (searches → bookings)
- Cancellation rate

**3. Payment Metrics**
- Successful payments
- Failed payments
- Refunds issued
- Platform revenue (15% fees)

**4. Support Metrics**
- Messages sent
- Disputes created
- Dispute resolution time
- Customer satisfaction

**5. System Metrics**
- API response times
- Error rates
- AI agent tool success rates
- Database query performance

### Logging Strategy

```python
# All critical actions logged:
logger.info(f"Booking created: {booking_id}, User: {user_id}, Amount: {amount}")
logger.warning(f"Payment failed: {payment_intent_id}, Reason: {error}")
logger.error(f"Dispute escalated: {dispute_id}, Priority: URGENT")
```

---

## 🔄 Future Enhancements

### Phase 2: Advanced Features
- [ ] Multi-language support (Arabic, French, Spanish)
- [ ] Smart pricing recommendations for hosts
- [ ] Predictive booking analytics
- [ ] Host reputation scoring
- [ ] Guest trust scoring
- [ ] Automated property quality checks
- [ ] Dynamic pricing based on demand
- [ ] Calendar sync with Airbnb/Booking.com

### Phase 3: Mobile Apps
- [ ] iOS app (React Native)
- [ ] Android app (React Native)
- [ ] Host mobile dashboard
- [ ] Real-time push notifications

### Phase 4: AI Enhancements
- [ ] Voice AI agent (phone bookings)
- [ ] Image recognition for property verification
- [ ] Sentiment analysis on guest reviews
- [ ] Fraud detection ML models
- [ ] Chatbot for hosts (property management tips)

---

## 📞 System Health Checks

### Quick Health Check Commands

```bash
# Backend health
curl https://krib-backend.onrender.com/health

# Database connection
curl https://krib-backend.onrender.com/api/health/db

# Stripe connection
curl https://krib-backend.onrender.com/api/health/stripe

# External APIs
curl https://krib-backend.onrender.com/api/health/external-apis

# Superadmin auth test
curl -H "Authorization: Bearer SUPERADMIN_KEY" \
  https://krib-backend.onrender.com/api/admin/health
```

### Expected Response

```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "stripe": "connected",
    "host_dashboard_api": "connected",
    "real_estate_api": "connected",
    "ai_services": "operational"
  },
  "timestamp": "2025-10-31T12:00:00Z"
}
```

---

## 🎯 Quick Reference: Who Does What

| Component                  | Responsibility                          | Primary Users          |
|---------------------------|-----------------------------------------|------------------------|
| Frontend (Next.js)        | User interface, chat, booking UI        | Guests, Hosts          |
| Backend API               | Business logic, AI agent, orchestration | All (via API)          |
| Host Dashboard API        | Short-term property management          | Backend (via API key)  |
| Real Estate API           | Long-term property listings             | Backend (via API key)  |
| Supabase                  | Database, auth, real-time, storage      | Backend, Frontend      |
| Stripe                    | Payment processing, payouts             | Backend (via SDK)      |
| Superadmin Dashboard      | System oversight, dispute resolution    | Superadmins only       |
| AI Agent                  | Natural language → Actions              | Guests (via chat)      |

---

## 📚 Documentation Index

- **Setup Guides:**
  - `SUPERADMIN_SETUP_GUIDE.md` - Superadmin API setup and usage
  - `UAEPASS_INTEGRATION_GUIDE.md` - UAE PASS verification setup
  
- **System Architecture:**
  - `SYSTEM_ARCHITECTURE_OVERVIEW.md` - This document
  - `HOST_GUEST_MESSAGING_SYSTEM.md` - Messaging and disputes
  
- **Implementation:**
  - `backend/README.md` - Backend setup
  - `frontend/README.md` - Frontend setup
  
- **API References:**
  - Host Dashboard API docs (external)
  - Stripe API docs (external)
  - Supabase docs (external)

