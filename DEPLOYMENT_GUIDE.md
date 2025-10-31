# Krib Super Admin - Deployment Guide

## Prerequisites

1. Supabase account
2. Upstash Redis account (free tier)
3. Render account (backend hosting)
4. Vercel account (frontend hosting)
5. API keys for all 3 platforms

---

## Step 1: Supabase Setup

### 1.1 Create Project

1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Name: `krib-superadmin`
4. Set database password (save it!)
5. Region: Choose closest to your users

### 1.2 Run Migrations

1. Go to SQL Editor in Supabase dashboard
2. Copy entire content of `backend/database/migrations.sql`
3. Paste and click "Run"
4. Verify all tables created successfully

### 1.3 Update Platform Configurations

```sql
-- Update with actual API keys
UPDATE platforms 
SET api_key = 'YOUR_ACTUAL_KEY' 
WHERE name = 'host_dashboard';

UPDATE platforms 
SET api_key = 'YOUR_ACTUAL_KEY' 
WHERE name = 'agent_dashboard';

UPDATE platforms 
SET api_key = 'YOUR_ACTUAL_KEY' 
WHERE name = 'customer_platform';
```

### 1.4 Get Credentials

Go to Project Settings → API:
- Copy `Project URL` (SUPABASE_URL)
- Copy `service_role` key (SUPABASE_SERVICE_KEY)

---

## Step 2: Redis Setup (Upstash)

### 2.1 Create Database

1. Go to https://upstash.com/
2. Sign up/Login
3. Click "Create Database"
4. Name: `krib-superadmin-cache`
5. Region: Choose same as Supabase
6. Type: Free (250MB)

### 2.2 Get Connection URL

- Click on your database
- Copy "Redis URL" (format: `redis://default:...@...upstash.io:...`)

---

## Step 3: Generate Security Keys

### 3.1 Encryption Key

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy output → `ENCRYPTION_KEY`

### 3.2 Secret Key

```bash
openssl rand -hex 32
```

Copy output → `SECRET_KEY`

---

## Step 4: Backend Deployment (Render)

### 4.1 Push to GitHub

```bash
cd /Users/mahmoudomar/Desktop/krib-superadmin
git init
git add .
git commit -m "Initial commit: Krib Super Admin"
git branch -M main

# Create repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/krib-superadmin.git
git push -u origin main
```

### 4.2 Deploy on Render

1. Go to https://dashboard.render.com/
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Settings:
   - **Name**: `krib-superadmin-backend`
   - **Region**: Same as Supabase
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 4.3 Environment Variables

Click "Environment" and add:

```
API_V1_PREFIX=/api/v1
PROJECT_NAME=Krib Super Admin
VERSION=1.0.0
ENVIRONMENT=production

# From Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key

# From Upstash
REDIS_URL=redis://default:...@...upstash.io:...

# Generated keys
SECRET_KEY=your-generated-secret-key
ENCRYPTION_KEY=your-generated-encryption-key

# Platform APIs - Host Dashboard
HOST_DASHBOARD_URL=https://krib-host-dahsboard-backend.onrender.com
HOST_DASHBOARD_API_KEY=your-actual-api-key

# Platform APIs - Agent Dashboard
AGENT_DASHBOARD_URL=https://krib-real-estate-agent-dahaboard-backend.onrender.com
AGENT_DASHBOARD_API_KEY=your-actual-api-key
AGENT_DASHBOARD_SUPABASE_URL=https://lnhhdaiyhphkmhikcagj.supabase.co
AGENT_DASHBOARD_SUPABASE_KEY=your-agent-service-key

# Platform APIs - Customer Platform
CUSTOMER_PLATFORM_URL=https://krib-backend.onrender.com
CUSTOMER_PLATFORM_API_KEY=your-actual-api-key
```

### 4.4 Deploy

1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Once deployed, note the URL (e.g., `https://krib-superadmin-backend.onrender.com`)

### 4.5 Verify

```bash
curl https://krib-superadmin-backend.onrender.com/api/health
# Should return: {"status":"healthy","version":"1.0.0","environment":"production"}
```

---

## Step 5: Frontend Deployment (Vercel)

### 5.1 Deploy to Vercel

```bash
cd frontend
npm install -g vercel
vercel login
vercel
```

Follow prompts:
- Link to existing project? **No**
- Project name: `krib-superadmin`
- Directory: `./` (current)
- Override settings? **No**

### 5.2 Set Environment Variables

```bash
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://krib-superadmin-backend.onrender.com
```

### 5.3 Deploy to Production

```bash
vercel --prod
```

### 5.4 Note URLs

You'll get a URL like: `https://krib-superadmin.vercel.app`

---

## Step 6: Test the System

### 6.1 Login

1. Go to your Vercel URL: `https://krib-superadmin.vercel.app`
2. Login with:
   - Email: `admin@krib.ai`
   - Password: `admin123`

### 6.2 First-Time Setup

**IMPORTANT: Change default password immediately!**

1. Create a new super admin user in Supabase:

```sql
INSERT INTO super_admin_users (email, full_name, role, permissions)
VALUES (
    'your-email@example.com',
    'Your Name',
    'super_admin',
    '{
        "can_view_users": true,
        "can_edit_users": true,
        "can_view_properties": true,
        "can_edit_properties": true,
        "can_view_bookings": true,
        "can_edit_bookings": true,
        "can_view_verification": true,
        "can_approve_verification": true,
        "can_view_analytics": true,
        "can_view_financial": true,
        "can_manage_platforms": true
    }'::jsonb
);
```

2. Delete or disable default admin:

```sql
UPDATE super_admin_users 
SET is_active = false 
WHERE email = 'admin@krib.ai';
```

### 6.3 Run Initial Sync

Trigger data synchronization manually:

```bash
# SSH into Render or run locally
curl -X POST https://krib-superadmin-backend.onrender.com/api/v1/sync/run \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Or set up a cron job to sync every 5 minutes.

---

## Step 7: Set Up Monitoring

### 7.1 Health Checks

Render automatically monitors `/api/health`

### 7.2 Custom Domain (Optional)

#### Backend (Render)
1. Go to Settings → Custom Domain
2. Add: `api.yourdomain.com`
3. Update DNS with provided CNAME

#### Frontend (Vercel)
1. Go to Settings → Domains
2. Add: `admin.yourdomain.com`
3. Update DNS with provided records

---

## Step 8: Schedule Data Sync

### Option A: GitHub Actions (Recommended)

Create `.github/workflows/sync.yml`:

```yaml
name: Sync Platform Data

on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes
  workflow_dispatch:  # Manual trigger

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Sync
        run: |
          curl -X POST ${{ secrets.API_URL }}/api/v1/sync/run \
            -H "Authorization: Bearer ${{ secrets.ADMIN_TOKEN }}"
```

### Option B: Render Cron Job

1. Create new "Cron Job" service on Render
2. Command: `python sync_job.py`
3. Schedule: `*/5 * * * *`

---

## Step 9: Security Checklist

- [ ] Changed default admin password
- [ ] All API keys encrypted in database
- [ ] HTTPS enabled (automatic with Render/Vercel)
- [ ] Row-level security enabled in Supabase
- [ ] Environment variables set correctly
- [ ] CORS configured for production domain
- [ ] Rate limiting enabled
- [ ] Webhook signatures verified

---

## Step 10: Backup Strategy

### Supabase Backups

1. Go to Settings → Database → Backups
2. Enable automatic daily backups
3. Keep last 7 days

### Code Backups

GitHub is your source of truth - push regularly:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

---

## Troubleshooting

### Backend Won't Start

1. Check Render logs: Dashboard → Logs
2. Verify all environment variables set
3. Test Redis connection:
   ```bash
   redis-cli -u $REDIS_URL ping
   ```

### Frontend Can't Connect

1. Check NEXT_PUBLIC_API_URL is correct
2. Verify CORS settings in backend
3. Check browser console for errors

### Database Connection Issues

1. Verify SUPABASE_URL and SUPABASE_SERVICE_KEY
2. Check Supabase project status
3. Verify RLS policies allow service role access

### API Key Issues

1. Verify platform API keys in `platforms` table
2. Check they're not encrypted with wrong key
3. Test direct API calls to platforms

---

## Monitoring & Maintenance

### Daily Checks

- [ ] Platform health status
- [ ] Pending verifications
- [ ] Error logs (Render dashboard)
- [ ] Database performance (Supabase)

### Weekly Checks

- [ ] Review audit logs
- [ ] Check disk usage
- [ ] Update dependencies
- [ ] Review user activity

### Monthly Checks

- [ ] Security updates
- [ ] Cost analysis
- [ ] Performance optimization
- [ ] Backup verification

---

## Cost Breakdown

| Service | Plan | Cost |
|---------|------|------|
| Supabase | Pro | $25/mo |
| Render | Starter | $7/mo |
| Vercel | Hobby | Free |
| Upstash Redis | Free | $0/mo |
| **Total** | | **$32/mo** |

Upgrade to paid plans as you scale.

---

## Support

- Backend API Docs: `https://your-backend.onrender.com/docs`
- Supabase Support: https://supabase.com/dashboard/support
- Render Support: https://render.com/docs

---

**Deployment Complete! 🎉**

Your Super Admin platform is now live and managing all three Krib platforms.

