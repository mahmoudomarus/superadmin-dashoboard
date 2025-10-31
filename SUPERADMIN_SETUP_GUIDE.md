# 🔐 Superadmin Platform - Setup & API Guide

## 📋 Overview

The Superadmin platform provides complete oversight of the Krib AI property rental system, including:
- User management (guests, hosts, agents)
- Booking oversight and dispute resolution
- Payment monitoring and refunds
- Host-Guest communication management
- System analytics and reporting

---

## 🔑 API Keys & Database Access

### Supabase Configuration

**Service Role Key (Full Access):**
```bash
# Get this from: Supabase Dashboard → Settings → API → service_role key
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Project URL:**
```bash
SUPABASE_URL=https://your-project.supabase.co
```

**Anon Key (Public API):**
```bash
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Backend API Keys

**Superadmin API Key (Create New):**
```bash
# Add to Render environment variables
SUPERADMIN_API_KEY=krib_superadmin_$(openssl rand -hex 32)
```

**Example:**
```bash
SUPERADMIN_API_KEY=krib_superadmin_7f3a8b9c2d1e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b
```

---

## 🚀 Quick Start - Connecting to Superadmin APIs

### 1. Authentication

All superadmin requests require the special API key:

```bash
# Example Request
curl -X GET https://krib-backend.onrender.com/api/admin/users \
  -H "Authorization: Bearer krib_superadmin_YOUR_KEY_HERE" \
  -H "Content-Type: application/json"
```

### 2. Python Example

```python
import requests
import os

SUPERADMIN_API_KEY = os.getenv("SUPERADMIN_API_KEY")
BASE_URL = "https://krib-backend.onrender.com/api/admin"

headers = {
    "Authorization": f"Bearer {SUPERADMIN_API_KEY}",
    "Content-Type": "application/json"
}

# Get all users
response = requests.get(f"{BASE_URL}/users", headers=headers)
users = response.json()
```

### 3. JavaScript/TypeScript Example

```typescript
const SUPERADMIN_API_KEY = process.env.SUPERADMIN_API_KEY;
const BASE_URL = "https://krib-backend.onrender.com/api/admin";

const headers = {
  "Authorization": `Bearer ${SUPERADMIN_API_KEY}`,
  "Content-Type": "application/json"
};

// Get all users
const response = await fetch(`${BASE_URL}/users`, { headers });
const users = await response.json();
```

---

## 👥 User Management

### List All Users

```bash
GET /api/admin/users
```

**Query Parameters:**
- `role` - Filter by role: `guest`, `host`, `agent`, `admin`
- `status` - Filter by status: `active`, `suspended`, `banned`
- `page` - Page number (default: 1)
- `limit` - Results per page (default: 50)

**Response:**
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": "uuid",
        "email": "user@example.com",
        "role": "guest",
        "status": "active",
        "created_at": "2025-10-31T00:00:00Z",
        "last_login": "2025-10-31T12:00:00Z",
        "metadata": {
          "total_bookings": 5,
          "total_spent": 5000.00,
          "verification_status": "verified"
        }
      }
    ],
    "total": 1250,
    "page": 1,
    "pages": 25
  }
}
```

### Get User Details

```bash
GET /api/admin/users/{user_id}
```

**Response includes:**
- User profile
- Booking history
- Payment history
- Messages/complaints
- Verification status

### Update User Status

```bash
PATCH /api/admin/users/{user_id}/status
```

**Request Body:**
```json
{
  "status": "suspended",
  "reason": "Multiple complaints",
  "duration_days": 30,
  "notify_user": true
}
```

### Verify User

```bash
POST /api/admin/users/{user_id}/verify
```

**Request Body:**
```json
{
  "verification_type": "identity",
  "verified": true,
  "notes": "UAE PASS verification completed"
}
```

---

## 📊 Booking Management

### List All Bookings

```bash
GET /api/admin/bookings
```

**Query Parameters:**
- `status` - Filter: `pending`, `confirmed`, `completed`, `cancelled`, `disputed`
- `property_id` - Filter by property
- `guest_id` - Filter by guest
- `host_id` - Filter by host
- `from_date` - Start date
- `to_date` - End date

### Get Booking Details

```bash
GET /api/admin/bookings/{booking_id}
```

**Response includes:**
- Full booking details
- Payment information
- Guest and host info
- Communication history
- Dispute details (if any)

### Override/Modify Booking

```bash
PATCH /api/admin/bookings/{booking_id}
```

**Request Body:**
```json
{
  "action": "force_cancel",
  "reason": "Host property unavailable",
  "refund_amount": "full",
  "notify_parties": true,
  "admin_notes": "Emergency cancellation - property maintenance issue"
}
```

---

## 💰 Payment Management

### View All Transactions

```bash
GET /api/admin/payments
```

**Query Parameters:**
- `type` - Filter: `booking`, `refund`, `security_deposit`
- `status` - Filter: `succeeded`, `pending`, `failed`, `refunded`
- `min_amount` - Minimum amount
- `max_amount` - Maximum amount

### Issue Refund

```bash
POST /api/admin/payments/refund
```

**Request Body:**
```json
{
  "booking_id": "uuid",
  "amount": 500.00,
  "reason": "Service issue",
  "refund_type": "full",
  "notify_guest": true,
  "admin_notes": "Refund approved after review"
}
```

### Release Security Deposit

```bash
POST /api/admin/payments/security-deposit/{booking_id}/release
```

**Request Body:**
```json
{
  "amount_to_release": 1000.00,
  "amount_to_retain": 0.00,
  "reason": "Clean checkout, no damages",
  "notify_parties": true
}
```

---

## 💬 Dispute Resolution

### List Active Disputes

```bash
GET /api/admin/disputes
```

**Query Parameters:**
- `status` - Filter: `open`, `under_review`, `resolved`
- `priority` - Filter: `low`, `medium`, `high`, `urgent`

**Response:**
```json
{
  "success": true,
  "data": {
    "disputes": [
      {
        "id": "uuid",
        "booking_id": "uuid",
        "complainant_id": "uuid",
        "complainant_role": "guest",
        "defendant_id": "uuid",
        "defendant_role": "host",
        "type": "property_condition",
        "status": "open",
        "priority": "high",
        "created_at": "2025-10-31T10:00:00Z",
        "description": "Property did not match listing photos",
        "evidence": [
          {"type": "image", "url": "..."},
          {"type": "message", "content": "..."}
        ]
      }
    ]
  }
}
```

### View Dispute Details

```bash
GET /api/admin/disputes/{dispute_id}
```

**Includes:**
- Full complaint details
- All messages between parties
- Evidence (photos, documents)
- Payment information
- Booking details
- User history

### Resolve Dispute

```bash
POST /api/admin/disputes/{dispute_id}/resolve
```

**Request Body:**
```json
{
  "resolution": "partial_refund",
  "refund_amount": 250.00,
  "ruling": "Guest claim partially validated. Property condition issues confirmed.",
  "actions": [
    {
      "type": "refund_guest",
      "amount": 250.00
    },
    {
      "type": "warning_host",
      "severity": "moderate",
      "message": "Ensure property listing photos are accurate"
    },
    {
      "type": "require_property_inspection",
      "property_id": "uuid"
    }
  ],
  "notify_parties": true,
  "close_dispute": true
}
```

---

## 📧 Message Management

### View All Messages

```bash
GET /api/admin/messages
```

**Query Parameters:**
- `booking_id` - Filter by booking
- `user_id` - Filter by user
- `flagged_only` - Show only flagged messages (default: false)

### View Conversation

```bash
GET /api/admin/messages/conversation/{booking_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "booking_id": "uuid",
    "guest": {"id": "uuid", "name": "John Doe"},
    "host": {"id": "uuid", "name": "Jane Smith"},
    "messages": [
      {
        "id": "uuid",
        "sender_id": "uuid",
        "sender_role": "guest",
        "message": "Hi, I have a question about check-in",
        "timestamp": "2025-10-31T10:00:00Z",
        "flagged": false,
        "delivered": true,
        "read": true
      }
    ]
  }
}
```

### Send Admin Message

```bash
POST /api/admin/messages/send
```

**Request Body:**
```json
{
  "booking_id": "uuid",
  "recipient_id": "uuid",
  "message": "This is an official message from Krib Support regarding your booking...",
  "message_type": "admin_notification",
  "priority": "high"
}
```

---

## 📈 Analytics & Reports

### System Overview

```bash
GET /api/admin/analytics/overview
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_users": 5000,
    "active_bookings": 150,
    "total_revenue_30d": 250000.00,
    "open_disputes": 5,
    "avg_booking_value": 1500.00,
    "occupancy_rate": 0.78,
    "top_properties": [...],
    "recent_issues": [...]
  }
}
```

### Generate Report

```bash
POST /api/admin/reports/generate
```

**Request Body:**
```json
{
  "report_type": "monthly_revenue",
  "start_date": "2025-10-01",
  "end_date": "2025-10-31",
  "filters": {
    "property_type": ["apartment", "villa"],
    "city": ["Dubai"]
  },
  "format": "pdf",
  "email_to": "admin@krib.ai"
}
```

---

## 🏠 Property Management

### List All Properties

```bash
GET /api/admin/properties
```

### Approve/Reject Property Listing

```bash
POST /api/admin/properties/{property_id}/review
```

**Request Body:**
```json
{
  "status": "approved",
  "notes": "Property meets all listing requirements",
  "visibility": "public"
}
```

### Suspend Property

```bash
POST /api/admin/properties/{property_id}/suspend
```

**Request Body:**
```json
{
  "reason": "Multiple guest complaints",
  "duration_days": 30,
  "notify_host": true,
  "block_new_bookings": true,
  "allow_existing_bookings": true
}
```

---

## 🔧 System Configuration

### Update Platform Settings

```bash
PATCH /api/admin/settings
```

**Request Body:**
```json
{
  "platform_fee_percentage": 15,
  "security_deposit_default": 1000.00,
  "cancellation_policy": "flexible",
  "auto_refund_threshold_hours": 48,
  "require_host_verification": true,
  "require_guest_verification": false
}
```

---

## 🔐 Security & Audit

### View Audit Logs

```bash
GET /api/admin/audit-logs
```

**Query Parameters:**
- `action_type` - Filter by action
- `user_id` - Filter by user
- `from_date` - Start date
- `to_date` - End date

**Response:**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "id": "uuid",
        "timestamp": "2025-10-31T10:00:00Z",
        "admin_id": "uuid",
        "admin_email": "admin@krib.ai",
        "action": "user_suspended",
        "target_type": "user",
        "target_id": "uuid",
        "details": {
          "reason": "Multiple complaints",
          "duration_days": 30
        },
        "ip_address": "192.168.1.1"
      }
    ]
  }
}
```

---

## 🚨 Emergency Actions

### System Maintenance Mode

```bash
POST /api/admin/system/maintenance
```

**Request Body:**
```json
{
  "enabled": true,
  "message": "System maintenance in progress. Expected completion: 2 hours",
  "allow_admin_access": true,
  "estimated_completion": "2025-10-31T14:00:00Z"
}
```

### Bulk User Action

```bash
POST /api/admin/users/bulk-action
```

**Request Body:**
```json
{
  "user_ids": ["uuid1", "uuid2", "uuid3"],
  "action": "suspend",
  "reason": "Security incident",
  "notify_users": true
}
```

---

## 📱 Webhooks (for Superadmin Dashboard)

### Subscribe to Events

```bash
POST /api/admin/webhooks/subscribe
```

**Request Body:**
```json
{
  "url": "https://superadmin-dashboard.com/webhooks/krib",
  "events": [
    "dispute.created",
    "dispute.escalated",
    "payment.refund_issued",
    "user.flagged",
    "booking.disputed"
  ],
  "secret": "your_webhook_secret"
}
```

**Webhook Event Example:**
```json
{
  "event": "dispute.created",
  "timestamp": "2025-10-31T10:00:00Z",
  "data": {
    "dispute_id": "uuid",
    "booking_id": "uuid",
    "priority": "high",
    "type": "property_condition"
  }
}
```

---

## 🧪 Testing the API

### Test Authentication

```bash
curl -X GET https://krib-backend.onrender.com/api/admin/health \
  -H "Authorization: Bearer krib_superadmin_YOUR_KEY" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Superadmin API authenticated",
  "permissions": ["full_access"]
}
```

---

## 📚 Additional Resources

- **Database Schema:** See `docs/SUPERADMIN_DATABASE_SCHEMA.md`
- **Messaging System:** See `docs/HOST_GUEST_MESSAGING_SYSTEM.md`
- **Dispute Resolution Workflow:** See `docs/DISPUTE_RESOLUTION_FLOW.md`

---

## 🆘 Support

For technical support or API issues:
- Email: tech@krib.ai
- Documentation: https://docs.krib.ai
- Status Page: https://status.krib.ai

