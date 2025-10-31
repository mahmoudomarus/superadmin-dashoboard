# Environment Variables Setup

Create a `.env` file in the backend directory with these variables:

```
# API Settings
API_V1_PREFIX=/api/v1
PROJECT_NAME=Krib Super Admin
VERSION=1.0.0

# Database (Supabase)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key-here

# Redis (Upstash)
REDIS_URL=redis://default:[password]@redis-12345.upstash.io:12345

# Security (Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here

# Platform APIs
HOST_DASHBOARD_URL=https://krib-host-dahsboard-backend.onrender.com
HOST_DASHBOARD_API_KEY=your-api-key
AGENT_DASHBOARD_URL=https://krib-real-estate-agent-dahaboard-backend.onrender.com
AGENT_DASHBOARD_API_KEY=your-api-key
AGENT_DASHBOARD_SUPABASE_URL=https://lnhhdaiyhphkmhikcagj.supabase.co
AGENT_DASHBOARD_SUPABASE_KEY=your-key
CUSTOMER_PLATFORM_URL=https://krib-backend.onrender.com
CUSTOMER_PLATFORM_API_KEY=your-api-key

# Environment
ENVIRONMENT=development
```
