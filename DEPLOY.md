# Deployment Instructions

## 1. Supabase Database
- Run `backend/database/migrations.sql` in SQL Editor
- Get your service role key from Supabase dashboard

## 2. Get Redis URL
1. Go to https://upstash.com/
2. Create Redis database (free tier)
3. Copy Redis URL

## 3. Deploy to Render
1. Go to https://dashboard.render.com/
2. Click "New" → "Blueprint"
3. Connect GitHub: https://github.com/mahmoudomarus/superadmin-dashoboard
4. Select `render.yaml` (in backend folder)
5. Add environment variables (check backend/.env for reference - values are in your local env file, DO NOT commit that file)

## 4. After Deployment
- Backend will be at: https://krib-superadmin-backend.onrender.com
- Frontend will be at: https://krib-superadmin-frontend.onrender.com
- Login: admin@krib.ai / admin123 (change immediately)

