# Real Estate Agent Dashboard - Project Architecture for Super Admin Integration

## 📋 Project Overview

**Project Name**: KRIB Real Estate Agent Dashboard  
**Purpose**: Platform for real estate agents to list and manage properties  
**Current Role**: Agent-facing application with agent registration, verification, and property management  
**Target Users**: Real estate agents in UAE (Dubai, Abu Dhabi, etc.)

---

## 🏗️ System Architecture

### Technology Stack

#### Frontend
- **Framework**: React 18 + TypeScript + Vite
- **Deployment**: Vercel
- **URL**: `https://krib-real-estate-agent-dahaboard-ba.vercel.app`
- **Styling**: TailwindCSS
- **UI Components**: Custom components + shadcn/ui
- **State Management**: React Context + Hooks
- **Routing**: React Router v6

#### Backend
- **Framework**: FastAPI (Python)
- **Deployment**: Render
- **URL**: `https://krib-real-estate-agent-dahaboard-backend.onrender.com`
- **API Documentation**: `/docs` (Swagger UI)

#### Database & Services
- **Database**: Supabase PostgreSQL
- **Project ID**: `lnhhdaiyhphkmhikcagj`
- **URL**: `https://lnhhdaiyhphkmhikcagj.supabase.co`
- **Authentication**: Supabase Auth (Email + OTP)
- **Storage**: Supabase S3-Compatible Storage
  - **Bucket 1**: `krib_host` (property images)
  - **Bucket 2**: `docs` (verification documents)
- **Region**: `us-east-2`

---

## 🔐 Authentication & User Management

### Current Authentication Flow

1. **Agent Registration** (Multi-Step Process):
   - **Step 1**: Basic Information
     - First Name, Last Name
     - Email (verified via OTP)
     - Password
     - Phone Number (with country code)
   
   - **Step 2**: Company Information
     - Company Name
     - Trade License Number
     - RERA Certificate Number (optional)
     - Company Address, City, Phone
     - Business Type (agency, brokerage, developer, etc.)
     - Number of Agents
   
   - **Step 3**: Document Upload
     - **Company Documents**:
       - Trade License
       - RERA Certificate
       - Memorandum of Association or Power of Attorney
     - **Personal Documents**:
       - Emirates ID (EID)
       - Passport + Visa

2. **Email Verification**:
   - Uses Supabase OTP (6-digit code)
   - Email template configured to send token instead of magic link
   - 2-minute expiry

3. **User States**:
   - `pending`: Just registered, documents not submitted
   - `under_review`: Documents submitted, awaiting admin approval
   - `approved`: Verified by admin, can list properties
   - `rejected`: Rejected by admin with reason
   - `resubmission_required`: Admin requested document resubmission

### User Roles & Account Types

```typescript
enum AccountType {
  agent = "agent"           // Real estate agent (default)
  admin = "admin"           // Platform admin (not implemented yet)
  super_admin = "super_admin" // Super admin (for your multi-platform dashboard)
}
```

**Important**: Currently, ALL users are agents. There's no "regular user" or "customer" in this system.

---

## 🗄️ Database Schema

### Core Tables

#### 1. `public.users`
Primary user table with authentication and verification data.

```sql
CREATE TABLE public.users (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  email TEXT UNIQUE NOT NULL,
  first_name TEXT,
  last_name TEXT,
  phone TEXT,
  avatar_url TEXT,
  
  -- Verification fields
  verification_status TEXT DEFAULT 'pending',
  account_type TEXT DEFAULT 'agent',
  can_list_properties BOOLEAN DEFAULT false,
  rejection_reason TEXT,
  verified_at TIMESTAMPTZ,
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
)
```

**Key Fields for Super Admin**:
- `verification_status`: Track agent verification state
- `account_type`: Distinguish between agent/admin/super_admin
- `can_list_properties`: Permission flag for property listing
- `rejection_reason`: Admin notes if rejected

#### 2. `public.agent_companies`
Company information for each agent.

```sql
CREATE TABLE public.agent_companies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  
  -- Company details
  company_name TEXT NOT NULL,
  company_name_arabic TEXT,
  trade_license_number TEXT NOT NULL,
  rera_certificate_number TEXT,
  
  -- Contact info
  company_email TEXT,
  company_phone TEXT,
  company_website TEXT,
  company_address TEXT NOT NULL,
  company_city TEXT NOT NULL,
  company_country TEXT DEFAULT 'UAE',
  po_box TEXT,
  
  -- Business info
  business_type TEXT NOT NULL,
  year_established INTEGER,
  number_of_agents INTEGER NOT NULL,
  description TEXT,
  specializations TEXT[],
  service_areas TEXT[],
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
)
```

**Key Fields for Super Admin**:
- `trade_license_number`: Verify legitimacy
- `rera_certificate_number`: UAE real estate authority certification
- `business_type`: Agency, brokerage, developer, etc.
- `number_of_agents`: Company size

#### 3. `public.verification_documents`
Uploaded documents for agent verification.

```sql
CREATE TABLE public.verification_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  
  -- Document info
  document_type TEXT NOT NULL, -- 'trade_license', 'rera_certificate', etc.
  document_category TEXT NOT NULL, -- 'company' or 'personal'
  file_url TEXT NOT NULL,
  s3_key TEXT NOT NULL,
  file_name TEXT NOT NULL,
  file_size INTEGER,
  mime_type TEXT,
  
  -- Document details
  document_number TEXT,
  issue_date DATE,
  expiry_date DATE,
  issuing_authority TEXT,
  
  -- Verification
  verification_status TEXT DEFAULT 'pending',
  verified_by UUID REFERENCES public.users(id),
  verified_at TIMESTAMPTZ,
  rejection_reason TEXT,
  notes TEXT,
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
)
```

**Document Types**:
- Company: `trade_license`, `rera_certificate`, `moa_poa`
- Personal: `emirates_id`, `passport`, `visa`

**Key Fields for Super Admin**:
- `verification_status`: Document approval state
- `expiry_date`: Track document validity
- `rejection_reason`: Admin feedback

#### 4. `public.verification_audit_log`
Audit trail for all verification actions.

```sql
CREATE TABLE public.verification_audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  admin_id UUID REFERENCES public.users(id),
  
  -- Action details
  action TEXT NOT NULL, -- 'approve', 'reject', 'request_resubmission'
  previous_status TEXT,
  new_status TEXT,
  notes TEXT,
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW()
)
```

**Key Fields for Super Admin**:
- Full audit trail of who did what and when
- Track admin actions for accountability

#### 5. `public.properties`
Property listings created by agents.

```sql
CREATE TABLE public.properties (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  
  -- Property details
  title TEXT NOT NULL,
  description TEXT,
  property_type TEXT NOT NULL, -- 'apartment', 'villa', 'townhouse', etc.
  listing_type TEXT NOT NULL, -- 'sale', 'rent'
  
  -- Location
  city TEXT NOT NULL,
  community TEXT,
  sub_community TEXT,
  street_address TEXT,
  building_name TEXT,
  unit_number TEXT,
  
  -- Specifications
  bedrooms INTEGER,
  bathrooms INTEGER,
  size_sqft NUMERIC,
  furnished BOOLEAN,
  
  -- Pricing
  price NUMERIC NOT NULL,
  price_currency TEXT DEFAULT 'AED',
  
  -- Features
  amenities TEXT[],
  images TEXT[], -- Array of S3 URLs
  
  -- Status
  status TEXT DEFAULT 'active', -- 'active', 'inactive', 'sold', 'rented'
  is_featured BOOLEAN DEFAULT false,
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
)
```

**Key Fields for Super Admin**:
- Track all property listings across agents
- Monitor property status and pricing
- `is_featured`: Premium listing flag

#### 6. `public.agencies`
Agency profiles (auto-created from company info).

```sql
CREATE TABLE public.agencies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  
  -- Agency details (mirrors agent_companies)
  name TEXT NOT NULL,
  description TEXT,
  logo_url TEXT,
  
  -- Contact
  email TEXT,
  phone TEXT,
  website TEXT,
  address TEXT,
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
)
```

---

## 🔒 Row Level Security (RLS) Policies

### Current RLS Implementation

#### Properties Table
```sql
-- Agents can only insert properties if verified
CREATE POLICY "Agents can insert properties if verified"
ON public.properties FOR INSERT
WITH CHECK (
  auth.uid() = user_id 
  AND (
    can_list_properties = true 
    OR account_type IN ('super_admin', 'admin')
  )
);

-- Agents can only update their own properties
CREATE POLICY "Agents can update own properties"
ON public.properties FOR UPDATE
USING (auth.uid() = user_id);

-- Everyone can view active properties
CREATE POLICY "Anyone can view active properties"
ON public.properties FOR SELECT
USING (status = 'active' OR auth.uid() = user_id);
```

#### Agent Companies Table
```sql
-- Agents can view their own company
CREATE POLICY "Agents can view own company"
ON public.agent_companies FOR SELECT
USING (auth.uid() = user_id);

-- Agents can insert their own company
CREATE POLICY "Agents can insert own company"
ON public.agent_companies FOR INSERT
WITH CHECK (auth.uid() = user_id);
```

#### Verification Documents Table
```sql
-- Agents can view their own documents
CREATE POLICY "Agents can view own documents"
ON public.verification_documents FOR SELECT
USING (auth.uid() = user_id);

-- Agents can upload their own documents
CREATE POLICY "Agents can upload own documents"
ON public.verification_documents FOR INSERT
WITH CHECK (auth.uid() = user_id);
```

**For Super Admin**: You'll need to add policies that allow `super_admin` account type to bypass these restrictions.

---

## 🔌 API Endpoints

### Base URL
`https://krib-real-estate-agent-dahaboard-backend.onrender.com/api`

### Authentication Endpoints

#### `POST /auth/signup`
Register new agent (handled by Supabase Auth + custom backend logic)

#### `POST /auth/signin`
Sign in with email + password

#### `POST /auth/verify-otp`
Verify email with OTP code

### Registration Endpoints

#### `POST /registration/register/step1`
```json
{
  "user_id": "uuid",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "phone": "string"
}
```
Creates user profile in database.

#### `POST /registration/register/step2`
```json
{
  "company_name": "string",
  "trade_license_number": "string",
  "rera_certificate_number": "string",
  "company_address": "string",
  "company_city": "string",
  "company_phone": "string",
  "business_type": "string",
  "number_of_agents": 5
}
```
Creates agent company profile.

#### `POST /registration/documents/upload`
```json
{
  "document_type": "trade_license",
  "document_category": "company",
  "file": "base64_or_multipart",
  "document_number": "string",
  "issue_date": "2024-01-01",
  "expiry_date": "2025-01-01"
}
```
Uploads verification document to `docs` bucket.

#### `GET /registration/documents`
Get all uploaded documents for current user.

#### `DELETE /registration/documents/{id}`
Delete a specific document.

#### `GET /registration/verification/status`
Get current verification status and all related data.

#### `POST /registration/verification/submit-for-review`
Change status from `pending` to `under_review`.

### Admin Verification Endpoints (For Your Super Admin)

#### `GET /admin/verification/pending`
List all users with `pending` or `under_review` status.

#### `GET /admin/verification/user/{id}`
Get detailed verification info for a specific user (profile + company + documents).

#### `POST /admin/verification/user/{id}/action`
```json
{
  "action": "approve", // or "reject", "request_resubmission"
  "notes": "string",
  "rejection_reason": "string" // if rejecting
}
```
Approve, reject, or request resubmission.

**Actions**:
- `approve`: Sets `verification_status = 'approved'`, `can_list_properties = true`
- `reject`: Sets `verification_status = 'rejected'`, adds `rejection_reason`
- `request_resubmission`: Sets `verification_status = 'resubmission_required'`

#### `GET /admin/verification/audit-log/{id}`
Get audit log for a user's verification process.

#### `GET /admin/verification/statistics`
```json
{
  "total_users": 150,
  "pending": 20,
  "under_review": 15,
  "approved": 100,
  "rejected": 10,
  "resubmission_required": 5
}
```

### Property Endpoints

#### `GET /properties`
List all properties (with filters).

#### `GET /properties/{id}`
Get single property details.

#### `POST /properties`
Create new property (requires `can_list_properties = true`).

#### `PUT /properties/{id}`
Update property (own properties only).

#### `DELETE /properties/{id}`
Delete property (own properties only).

### Agency Endpoints

#### `GET /agencies/current`
Get current user's agency (auto-onboarding).

#### `GET /agencies`
List all agencies.

#### `GET /agencies/{id}`
Get agency details.

---

## 📁 File Storage Structure

### S3 Buckets

#### Bucket 1: `krib_host` (Property Images)
```
krib_host/
├── properties/
│   ├── {property_id}/
│   │   ├── image_1.jpg
│   │   ├── image_2.jpg
│   │   └── ...
```

**Public URLs**:
`https://lnhhdaiyhphkmhikcagj.supabase.co/storage/v1/object/public/krib_host/properties/{property_id}/{image_name}`

#### Bucket 2: `docs` (Verification Documents)
```
docs/
├── users/
│   ├── {user_id}/
│   │   ├── company/
│   │   │   ├── trade_license_{timestamp}.pdf
│   │   │   ├── rera_certificate_{timestamp}.pdf
│   │   │   └── moa_poa_{timestamp}.pdf
│   │   └── personal/
│   │       ├── emirates_id_{timestamp}.pdf
│   │       ├── passport_{timestamp}.pdf
│   │       └── visa_{timestamp}.pdf
```

**Private URLs** (require authentication):
`https://lnhhdaiyhphkmhikcagj.supabase.co/storage/v1/object/authenticated/docs/users/{user_id}/{category}/{file_name}`

---

## 🎯 Super Admin Integration Points

### What Your Super Admin Dashboard Needs to Access

#### 1. **User Management**
- **Endpoint**: `GET /admin/verification/pending`
- **Purpose**: View all agents awaiting verification
- **Data**: User profile, company info, uploaded documents
- **Actions**: Approve, reject, request resubmission

#### 2. **Verification Workflow**
- **Endpoint**: `POST /admin/verification/user/{id}/action`
- **Purpose**: Approve/reject agents
- **Required**: Admin notes, rejection reasons
- **Result**: Updates `verification_status` and `can_list_properties`

#### 3. **Document Review**
- **Endpoint**: `GET /admin/verification/user/{id}`
- **Purpose**: View all documents for a user
- **Access**: Direct S3 URLs to view PDFs/images
- **Validation**: Check expiry dates, document numbers

#### 4. **Audit Trail**
- **Endpoint**: `GET /admin/verification/audit-log/{id}`
- **Purpose**: Track all verification actions
- **Data**: Who approved/rejected, when, why

#### 5. **Statistics & Analytics**
- **Endpoint**: `GET /admin/verification/statistics`
- **Purpose**: Dashboard metrics
- **Metrics**: Total agents, pending, approved, rejected

#### 6. **Property Oversight**
- **Endpoint**: `GET /properties` (with admin override)
- **Purpose**: View all properties across all agents
- **Actions**: Feature properties, moderate listings, remove violations

#### 7. **Agency Management**
- **Endpoint**: `GET /agencies`
- **Purpose**: View all agencies
- **Actions**: Activate/deactivate agencies

### Authentication for Super Admin

#### Option 1: Separate Super Admin Auth (Recommended)
- Create super admin users directly in Supabase
- Set `account_type = 'super_admin'`
- Use same Supabase Auth but different login portal
- Super admin dashboard is a separate application

#### Option 2: Service Role Key (For Backend-to-Backend)
- Use Supabase Service Role Key
- Bypass RLS policies
- Direct database access
- **Security**: Only use server-side, never expose to frontend

**Service Role Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxuaGhkYWl5aHBoa21oaWtjYWdqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjE2NTE5NCwiZXhwIjoyMDcxNzQxMTk0fQ.TWsm8cCtg83L_1v9SEewx2Q0as6egDpOusLQoKXhqrM`

---

## 🔐 Security Considerations

### Current Security Measures

1. **Row Level Security (RLS)**: Enabled on all tables
2. **JWT Authentication**: Supabase Auth tokens
3. **Email Verification**: OTP-based email verification
4. **Document Storage**: Private bucket with authenticated access
5. **API Authorization**: Bearer token required for protected endpoints

### What Super Admin Needs

1. **Elevated Permissions**:
   - Bypass RLS policies for read access
   - View all users, properties, documents
   - Modify user verification status

2. **Audit Logging**:
   - Log all super admin actions
   - Track who approved/rejected agents
   - Monitor property moderation

3. **Secure Document Access**:
   - Generate signed URLs for document viewing
   - Time-limited access to sensitive documents
   - No direct S3 key exposure

---

## 🚀 Deployment & Environment

### Frontend (Vercel)
```bash
# Environment Variables
VITE_SUPABASE_URL=https://lnhhdaiyhphkmhikcagj.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
VITE_API_URL=https://krib-real-estate-agent-dahaboard-backend.onrender.com/api
```

### Backend (Render)
```bash
# Environment Variables
SUPABASE_URL=https://lnhhdaiyhphkmhikcagj.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# S3 Storage
AWS_ACCESS_KEY_ID=67cb63fc697a5c13a7f8c98dd539853d
AWS_SECRET_ACCESS_KEY=<your_secret_key>
AWS_REGION=us-east-2
S3_BUCKET_NAME=krib_host
S3_ENDPOINT_URL=https://lnhhdaiyhphkmhikcagj.storage.supabase.co/storage/v1/s3
```

### Database (Supabase)
- **Project**: `lnhhdaiyhphkmhikcagj`
- **Region**: `us-east-2`
- **Connection String**: Available in Supabase dashboard
- **Migrations**: Located in `supabase/migrations/`

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT REGISTRATION FLOW                   │
└─────────────────────────────────────────────────────────────┘

1. Agent Signs Up
   ├─> Frontend: AuthForm.tsx
   ├─> Supabase Auth: Create auth.users record
   ├─> Backend: POST /registration/register/step1
   └─> Database: Insert into public.users (status: pending)

2. Email Verification
   ├─> Supabase: Send OTP email
   ├─> Frontend: OTP input form
   ├─> Supabase Auth: Verify OTP
   └─> Redirect: /register?step=2

3. Company Information
   ├─> Frontend: AgentRegistrationWizard (Step 2)
   ├─> Backend: POST /registration/register/step2
   └─> Database: Insert into public.agent_companies

4. Document Upload
   ├─> Frontend: AgentRegistrationWizard (Step 3)
   ├─> Backend: POST /registration/documents/upload
   ├─> S3: Upload to docs bucket
   └─> Database: Insert into public.verification_documents

5. Submit for Review
   ├─> Backend: POST /registration/verification/submit-for-review
   └─> Database: Update users.verification_status = 'under_review'

┌─────────────────────────────────────────────────────────────┐
│                 SUPER ADMIN VERIFICATION FLOW                │
└─────────────────────────────────────────────────────────────┘

1. View Pending Agents
   ├─> Super Admin Dashboard
   ├─> Backend: GET /admin/verification/pending
   └─> Display: List of agents with status 'under_review'

2. Review Agent Details
   ├─> Super Admin Dashboard
   ├─> Backend: GET /admin/verification/user/{id}
   └─> Display: Profile, company, documents

3. View Documents
   ├─> S3: Generate signed URL
   └─> Display: PDF/Image viewer

4. Take Action
   ├─> Super Admin Dashboard: Approve/Reject/Request Resubmission
   ├─> Backend: POST /admin/verification/user/{id}/action
   ├─> Database: Update users.verification_status
   ├─> Database: Update users.can_list_properties (if approved)
   └─> Database: Insert into verification_audit_log

5. Agent Notification
   ├─> Email: Notify agent of decision
   └─> Dashboard: Agent sees updated status

┌─────────────────────────────────────────────────────────────┐
│                    PROPERTY LISTING FLOW                     │
└─────────────────────────────────────────────────────────────┘

1. Agent Creates Property
   ├─> Frontend: Property form
   ├─> Check: can_list_properties = true?
   ├─> S3: Upload property images to krib_host bucket
   ├─> Backend: POST /properties
   └─> Database: Insert into public.properties

2. Super Admin Oversight
   ├─> Super Admin Dashboard
   ├─> Backend: GET /properties (all properties)
   ├─> Actions: Feature, moderate, remove
   └─> Database: Update properties.is_featured or status
```

---

## 🎨 Frontend Structure

### Key Components

#### `AuthForm.tsx`
- Multi-step registration form
- Email + OTP verification
- Step 1: Basic info + phone with country code
- Redirects to `/register?step=2` after OTP

#### `AgentRegistrationWizard.tsx`
- Step 2: Company information form
- Step 3: Document upload interface
- Step 4: Review and submit
- Reads `?step=` from URL params

#### `VerificationStatusPage.tsx`
- Shows agent's current verification status
- Displays uploaded documents
- Shows rejection reason if rejected
- Allows resubmission if required

### Routing Structure
```
/auth                    → AuthForm (Sign In / Sign Up)
/register?step=2         → AgentRegistrationWizard (Company Info)
/register?step=3         → AgentRegistrationWizard (Documents)
/dashboard               → Main dashboard (requires auth)
/properties              → Property listings
/properties/new          → Create property (requires can_list_properties)
/verification-status     → Verification status page
```

---

## 🔧 Backend Structure

### API Routes
```
backend/app/api/routes/
├── auth.py                    # Authentication endpoints
├── registration.py            # Agent registration & documents
├── admin_verification.py      # Admin verification actions
├── properties.py              # Property CRUD
├── agencies.py                # Agency management
└── storage.py                 # File upload utilities
```

### Services
```
backend/app/services/
├── storage_service.py         # S3 file upload/download
└── supabase_client.py         # Supabase client initialization
```

### Models
```
backend/app/models/
└── schemas.py                 # Pydantic models for API validation
```

---

## 📝 Key Business Logic

### Agent Verification Rules

1. **Registration**:
   - All users must verify email via OTP
   - Must complete company information
   - Must upload required documents

2. **Document Requirements**:
   - **Company**: Trade License (required), RERA Certificate (optional), MOA/POA (required)
   - **Personal**: Emirates ID (required) OR Passport + Visa (required)

3. **Verification States**:
   - `pending`: Just registered, not submitted for review
   - `under_review`: Submitted, awaiting admin review
   - `approved`: Verified, can list properties
   - `rejected`: Not approved, cannot list properties
   - `resubmission_required`: Admin requested changes

4. **Property Listing Permission**:
   - `can_list_properties = true` only if `verification_status = 'approved'`
   - OR `account_type IN ('admin', 'super_admin')`

### Auto-Onboarding

When a user signs in:
1. Frontend calls `GET /agencies/current`
2. Backend checks if agency exists
3. If not, creates agency from `agent_companies` data
4. Returns agency profile

---

## 🌐 Multi-Platform Super Admin Strategy

### Your Super Admin Dashboard Should:

1. **Centralize User Management**:
   - Real Estate Agent Platform (this project)
   - Customer AI Agent Platform (future)
   - Any other platforms

2. **Unified Authentication**:
   - Single super admin login
   - Access all platforms via API
   - Service role keys for backend access

3. **Cross-Platform Analytics**:
   - Total users across all platforms
   - Revenue metrics
   - Usage statistics

4. **Centralized Verification**:
   - Approve agents for real estate platform
   - Verify customers for AI platform
   - Unified document storage

### Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              SUPER ADMIN DASHBOARD (Separate App)            │
│  - Next.js / React                                           │
│  - Deployed separately (Vercel/Netlify)                      │
│  - Uses service role keys for backend access                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ API Calls
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ Real Estate   │  │ Customer AI   │  │ Future        │
│ Agent API     │  │ Agent API     │  │ Platform API  │
│ (This Project)│  │ (Future)      │  │               │
└───────────────┘  └───────────────┘  └───────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │  Supabase (Shared)    │
                │  - Auth               │
                │  - Database           │
                │  - Storage            │
                └───────────────────────┘
```

### API Integration for Super Admin

#### Authentication
```typescript
// Super Admin uses service role key
const supabaseAdmin = createClient(
  'https://lnhhdaiyhphkmhikcagj.supabase.co',
  'SERVICE_ROLE_KEY' // Full access, bypasses RLS
)
```

#### Fetching Data
```typescript
// Get all agents awaiting verification
const response = await fetch(
  'https://krib-real-estate-agent-dahaboard-backend.onrender.com/api/admin/verification/pending',
  {
    headers: {
      'Authorization': `Bearer ${serviceRoleToken}`
    }
  }
)
```

#### Taking Actions
```typescript
// Approve an agent
await fetch(
  `https://krib-real-estate-agent-dahaboard-backend.onrender.com/api/admin/verification/user/${userId}/action`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${serviceRoleToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      action: 'approve',
      notes: 'All documents verified'
    })
  }
)
```

---

## 📞 Support & Maintenance

### Logs & Monitoring

#### Backend Logs (Render)
- Access via Render dashboard
- Real-time logs for API requests
- Error tracking

#### Frontend Logs (Vercel)
- Access via Vercel dashboard
- Build logs and runtime logs
- Analytics

#### Database Logs (Supabase)
- Query performance
- Connection pooling
- RLS policy violations

### Common Issues & Solutions

1. **Agent can't list properties**:
   - Check `users.can_list_properties = true`
   - Check `users.verification_status = 'approved'`

2. **Document upload fails**:
   - Check S3 bucket permissions
   - Verify AWS credentials
   - Check file size limits

3. **OTP not received**:
   - Check Supabase email template
   - Verify email provider settings
   - Check spam folder

---

## 🎯 Summary for Super Admin Development

### What This Project Does:
- **Agent Registration**: Multi-step registration with company info and document upload
- **Email Verification**: OTP-based email verification
- **Document Management**: Secure storage of verification documents
- **Property Listings**: Agents can list properties after verification
- **Verification Workflow**: Admin endpoints for approving/rejecting agents

### What Your Super Admin Needs:
1. **Read Access**: View all agents, properties, documents
2. **Write Access**: Approve/reject agents, moderate properties
3. **Analytics**: Statistics on registrations, verifications, listings
4. **Audit Trail**: Track all admin actions
5. **Document Viewer**: View uploaded PDFs and images

### Key Endpoints for Super Admin:
- `GET /admin/verification/pending` - List pending agents
- `GET /admin/verification/user/{id}` - Get agent details
- `POST /admin/verification/user/{id}/action` - Approve/reject
- `GET /admin/verification/statistics` - Dashboard metrics
- `GET /properties` - View all properties (with admin override)

### Database Tables to Monitor:
- `public.users` - All agents
- `public.agent_companies` - Company information
- `public.verification_documents` - Uploaded documents
- `public.verification_audit_log` - Admin actions
- `public.properties` - Property listings

### Security:
- Use Supabase Service Role Key for backend access
- Implement proper authentication for super admin users
- Log all admin actions for accountability
- Use signed URLs for document access

---

## 📚 Additional Resources

### Documentation Files in Project:
- `API_INTEGRATION_GUIDE.md` - API integration details
- `AGENT_VERIFICATION_SYSTEM.md` - Verification system details
- `SUPABASE_OTP_SETUP.md` - OTP configuration guide
- `README.md` - Project setup and deployment

### Supabase Dashboard:
- **URL**: https://supabase.com/dashboard/project/lnhhdaiyhphkmhikcagj
- **Database**: SQL Editor, Table Editor
- **Storage**: Bucket management
- **Auth**: User management, email templates

### API Documentation:
- **Swagger UI**: https://krib-real-estate-agent-dahaboard-backend.onrender.com/docs
- **ReDoc**: https://krib-real-estate-agent-dahaboard-backend.onrender.com/redoc

---

## 🚀 Next Steps for Super Admin Development

1. **Set Up Super Admin Project**:
   - Create new Next.js/React app
   - Install Supabase client
   - Configure service role key

2. **Implement Authentication**:
   - Create super admin login
   - Use separate auth or same Supabase with `account_type = 'super_admin'`

3. **Build Verification Dashboard**:
   - List pending agents
   - View agent details and documents
   - Approve/reject interface
   - Audit log viewer

4. **Add Analytics**:
   - Total agents, properties
   - Verification statistics
   - Revenue tracking (if applicable)

5. **Implement Property Moderation**:
   - View all properties
   - Feature/unfeature properties
   - Remove policy violations

6. **Set Up Notifications**:
   - Email agents when approved/rejected
   - Slack/Discord notifications for new registrations
   - Admin alerts for suspicious activity

---

**Document Version**: 1.0  
**Last Updated**: October 29, 2025  
**Project**: KRIB Real Estate Agent Dashboard  
**For**: Super Admin Integration Planning

