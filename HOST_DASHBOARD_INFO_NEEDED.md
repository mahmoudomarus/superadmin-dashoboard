# Host Dashboard - Info Needed for Super Admin Integration

**Platform URL:** https://krib-host-dahsboard-backend.onrender.com

## Required Information

### 1. Supabase Credentials
```
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
```

### 2. API Authentication
```
API_KEY= (current external API key)
# Used in: Authorization: Bearer {API_KEY}
```

### 3. Database Schema
List all table names:
- `users`
- `properties`
- `bookings`
- `reviews`
- Other tables...

### 4. Available API Endpoints
Confirm these exist and list any others:
```
GET /api/v1/properties
GET /api/v1/properties/{id}
GET /api/v1/bookings
GET /api/v1/users
PATCH /api/v1/properties/{id}/status
DELETE /api/v1/bookings/{id}
# etc.
```

### 5. User Roles
What user types? (host, guest, admin)

### 6. Key Operations Super Admin Needs
- View all properties (174 properties)
- View all bookings
- View all hosts
- Suspend properties
- Cancel bookings
- Refund payments
- View host earnings

## Output Format
Provide as environment variables + confirmed endpoint list + table schema.

