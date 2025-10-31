# Real Estate Agent Dashboard - Info Needed for Super Admin Integration

**Platform URL:** https://krib-real-estate-agent-dahaboard-backend.onrender.com

## Required Information

### 1. Supabase Credentials
```
SUPABASE_URL=https://lnhhdaiyhphkmhikcagj.supabase.co
SUPABASE_SERVICE_ROLE_KEY= (NEED THIS)
```

### 2. API Authentication
```
API_KEY= (the krib_ext_... key)
# External API: /api/external/v1
# Auth: Bearer krib_ext_[API_KEY]
```

### 3. Database Schema
List all table names:
- `users`
- `agent_companies`
- `verification_documents`
- `verification_audit_log`
- `properties`
- Other tables...

### 4. Available API Endpoints
Confirm these exist and list any others:
```
GET /api/admin/verification/pending
GET /api/admin/verification/user/{id}
POST /api/admin/verification/user/{id}/action
GET /api/admin/verification/statistics
GET /api/admin/agents
GET /api/properties
# etc.
```

### 5. User Roles
What user types? (agent, admin, super_admin)

### 6. Verification Workflow
- What statuses exist? (pending, under_review, approved, rejected)
- What actions can super admin take?
- Document access method (signed URLs?)

### 7. Key Operations Super Admin Needs
- View pending agent verifications
- Approve/reject agents
- View all agent properties
- Access verification documents
- View audit logs
- Suspend agents

## Output Format
Provide as environment variables + confirmed endpoint list + table schema + verification workflow details.

