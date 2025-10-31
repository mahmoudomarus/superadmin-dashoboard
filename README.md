# Krib Super Admin Platform

Centralized super admin dashboard to manage all three Krib platforms:
- Host Dashboard (short-term rentals)
- Real Estate Agent Dashboard (long-term rentals)
- Customer AI Platform (booking agent)

## Architecture

```
Super Admin Dashboard
        │
        ├─ Host Dashboard API
        ├─ Agent Dashboard API
        └─ Customer Platform API
```

## Project Structure

```
krib-superadmin/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/v1/      # API endpoints
│   │   ├── services/    # Platform clients & sync
│   │   ├── models/      # Pydantic schemas
│   │   ├── core/        # Supabase, Redis, security
│   │   └── utils/       # Helpers
│   ├── database/        # SQL migrations
│   └── requirements.txt
│
└── frontend/            # Next.js 14 frontend
    ├── app/             # Pages (App Router)
    ├── components/      # React components
    ├── lib/             # API clients, utilities
    └── package.json
```

## Quick Start

### 1. Set Up Database

1. Create Supabase project
2. Run `backend/database/migrations.sql`
3. Update platform API keys in `platforms` table

### 2. Set Up Redis

- Use Upstash Redis (free tier)
- Get Redis URL

### 3. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env (see backend/ENV_SETUP.md)
# Generate encryption key:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

uvicorn app.main:app --reload
```

### 4. Frontend Setup

```bash
cd frontend
npm install
# Create .env.local with NEXT_PUBLIC_API_URL
npm run dev
```

### 5. Login

- URL: http://localhost:3000/login
- Email: admin@krib.ai
- Password: admin123 (change immediately!)

## Key Features

### ✅ Implemented

- **Platform Integration**: HTTP clients for all 3 platforms
- **Data Synchronization**: Sync users, properties, bookings
- **User Management**: View/manage users across platforms
- **Verification System**: Approve/reject agent verifications
- **Caching**: Redis caching for API responses
- **Authentication**: JWT-based auth
- **Audit Logging**: Track all admin actions
- **Dashboard**: Overview metrics
- **RLS Policies**: Secure database access

### 🚧 To Implement

- Analytics dashboard
- Financial reports
- Booking management
- Property moderation
- Real-time notifications
- Advanced search/filters
- Bulk operations
- Export functionality

## Environment Variables

### Backend

```bash
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
REDIS_URL=
SECRET_KEY=
ENCRYPTION_KEY=
HOST_DASHBOARD_API_KEY=
AGENT_DASHBOARD_API_KEY=
CUSTOMER_PLATFORM_API_KEY=
```

### Frontend

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Deployment

### Backend (Render)

```bash
# Push to GitHub, Render auto-deploys via render.yaml
git push origin main
```

### Frontend (Vercel)

```bash
vercel --prod
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Key Endpoints

- `POST /api/v1/auth/login` - Login
- `GET /api/v1/users` - List users
- `GET /api/v1/verification/queue` - Verification queue
- `POST /api/v1/verification/{id}/approve` - Approve
- `POST /api/v1/verification/{id}/reject` - Reject

## Security

- JWT authentication
- Row-level security (RLS)
- API key encryption
- Audit logging
- HTTPS only (production)

## Monitoring

- Health checks: `/api/health`
- Platform connectivity checks every 30s
- Redis connection monitoring
- Audit trail for all actions

## Cost Estimate

- Supabase Pro: $25/month
- Render Pro: $25/month
- Vercel Pro: $20/month
- Upstash Redis: $10/month
- **Total**: ~$80/month

## Support

See individual READMEs:
- `backend/README.md`
- `frontend/README.md`
- `TECHNICAL_PLAN.md` (detailed architecture)

