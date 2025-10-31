# AI Agent/Customer Platform - Info Needed for Super Admin Integration

**Platform URL:** https://kribz-i7jx.onrender.com

## Required Information

### 1. Supabase Credentials
```
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
```

### 2. API Authentication
```
API_KEY= (if exists)
# Or describe how external systems authenticate
```

### 3. Database Schema
List all table names:
- `users` (or equivalent)
- `bookings` (or equivalent)
- `conversations` (or equivalent)
- Other tables...

### 4. Available API Endpoints
List admin/external endpoints:
```
GET /api/users
GET /api/bookings
PATCH /api/users/{id}
DELETE /api/bookings/{id}
# etc.
```

### 5. User Roles/Types
What user types exist? (guest, admin, etc.)

### 6. Key Operations Super Admin Needs
- View all users
- View all bookings
- Cancel bookings
- Ban/suspend users
- View AI conversations
- Access payment data

## Output Format
Provide as environment variables + list of endpoints + table schema.

