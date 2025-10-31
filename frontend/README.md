# Krib Super Admin Frontend

Next.js 14 frontend for the Krib Super Admin platform.

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Create `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### 3. Run Development Server

```bash
npm run dev
```

Open http://localhost:3000

## Features

- **Dashboard**: Overview of all platforms
- **User Management**: View and manage users across platforms
- **Verification Queue**: Approve/reject agent verifications
- **Properties**: View all properties
- **Bookings**: Manage bookings
- **Analytics**: Platform metrics

## Deployment

Deploy to Vercel:
```bash
vercel --prod
```

## Tech Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- React Query (TanStack Query)
- Axios
- Lucide Icons

