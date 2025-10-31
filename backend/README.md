# Krib Super Admin Backend

FastAPI backend for the Krib Super Admin platform that manages all three Krib platforms.

## Setup

### 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual values
```

### 3. Set Up Database

1. Create a new Supabase project
2. Run the migrations: `backend/database/migrations.sql` in Supabase SQL Editor
3. Copy the Supabase URL and Service Role Key to `.env`

### 4. Set Up Redis

Use Upstash Redis (free tier):
1. Go to https://upstash.com/
2. Create a Redis database
3. Copy the Redis URL to `.env`

### 5. Generate Encryption Key

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the output to `ENCRYPTION_KEY` in `.env`

### 6. Run the Server

```bash
uvicorn app.main:app --reload
```

API will be available at http://localhost:8000

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deployment

Deploy to Render:
```bash
git push origin main
```

Render will automatically deploy using `render.yaml` configuration.

## Key Endpoints

- `POST /api/v1/auth/login` - Super admin login
- `GET /api/v1/users` - List all users
- `GET /api/v1/verification/queue` - Get verification queue
- `POST /api/v1/verification/{id}/approve` - Approve verification

## Architecture

- **Platform Clients**: Abstract HTTP clients for each platform
- **Sync Service**: Synchronizes data from all platforms
- **Redis Cache**: Caches API responses to reduce load
- **Supabase**: Unified database for super admin data

