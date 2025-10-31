-- Krib Super Admin Database Schema
-- Run this in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Super admin users table
CREATE TABLE IF NOT EXISTS super_admin_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('super_admin', 'admin', 'analyst')),
    permissions JSONB NOT NULL DEFAULT '{}',
    last_login_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Platform registry
CREATE TABLE IF NOT EXISTS platforms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    api_base_url TEXT NOT NULL,
    api_key TEXT NOT NULL,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'maintenance', 'offline')),
    health_check_endpoint TEXT,
    last_health_check TIMESTAMPTZ,
    supabase_project_id TEXT,
    supabase_url TEXT,
    supabase_service_key TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Unified user registry
CREATE TABLE IF NOT EXISTS unified_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT NOT NULL,
    platform_id UUID REFERENCES platforms(id) ON DELETE CASCADE,
    platform_user_id UUID NOT NULL,
    user_type TEXT NOT NULL CHECK (user_type IN ('host', 'agent', 'customer', 'guest')),
    full_name TEXT,
    phone TEXT,
    verification_status TEXT,
    account_status TEXT DEFAULT 'active' CHECK (account_status IN ('active', 'suspended', 'banned')),
    platform_specific_data JSONB,
    last_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(platform_id, platform_user_id)
);

-- Unified properties
CREATE TABLE IF NOT EXISTS unified_properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_id UUID REFERENCES platforms(id) ON DELETE CASCADE,
    platform_property_id UUID NOT NULL,
    owner_user_id UUID REFERENCES unified_users(id) ON DELETE CASCADE,
    title TEXT,
    property_type TEXT,
    listing_type TEXT CHECK (listing_type IN ('short_term', 'long_term')),
    city TEXT,
    price NUMERIC,
    price_currency TEXT DEFAULT 'AED',
    status TEXT,
    is_featured BOOLEAN DEFAULT false,
    platform_specific_data JSONB,
    last_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(platform_id, platform_property_id)
);

-- Unified bookings
CREATE TABLE IF NOT EXISTS unified_bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_id UUID REFERENCES platforms(id) ON DELETE CASCADE,
    platform_booking_id UUID NOT NULL,
    property_id UUID REFERENCES unified_properties(id) ON DELETE CASCADE,
    guest_user_id UUID REFERENCES unified_users(id) ON DELETE SET NULL,
    host_user_id UUID REFERENCES unified_users(id) ON DELETE SET NULL,
    check_in DATE,
    check_out DATE,
    total_price NUMERIC,
    status TEXT,
    payment_status TEXT,
    platform_specific_data JSONB,
    last_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(platform_id, platform_booking_id)
);

-- Financial transactions
CREATE TABLE IF NOT EXISTS unified_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_id UUID REFERENCES platforms(id) ON DELETE CASCADE,
    booking_id UUID REFERENCES unified_bookings(id) ON DELETE SET NULL,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('booking_payment', 'refund', 'payout')),
    amount_total NUMERIC NOT NULL,
    amount_platform_fee NUMERIC NOT NULL,
    amount_host_payout NUMERIC,
    currency TEXT DEFAULT 'AED',
    payment_provider TEXT,
    payment_provider_id TEXT,
    status TEXT CHECK (status IN ('pending', 'completed', 'failed')),
    platform_specific_data JSONB,
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Admin actions audit log
CREATE TABLE IF NOT EXISTS admin_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    admin_user_id UUID REFERENCES super_admin_users(id) ON DELETE SET NULL,
    action_type TEXT NOT NULL,
    target_platform UUID REFERENCES platforms(id) ON DELETE SET NULL,
    target_entity_type TEXT,
    target_entity_id UUID,
    action_details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Verification queue
CREATE TABLE IF NOT EXISTS verification_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_id UUID REFERENCES platforms(id) ON DELETE CASCADE,
    user_id UUID REFERENCES unified_users(id) ON DELETE CASCADE,
    platform_user_id UUID NOT NULL,
    verification_type TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_review', 'approved', 'rejected')),
    documents JSONB,
    reviewed_by UUID REFERENCES super_admin_users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMPTZ,
    review_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- System notifications
CREATE TABLE IF NOT EXISTS admin_notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    admin_user_id UUID REFERENCES super_admin_users(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT,
    data JSONB,
    is_read BOOLEAN DEFAULT false,
    priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'critical')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Analytics snapshots
CREATE TABLE IF NOT EXISTS analytics_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    snapshot_type TEXT NOT NULL,
    platform_id UUID REFERENCES platforms(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    metrics JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(snapshot_type, platform_id, date)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_unified_users_email ON unified_users(email);
CREATE INDEX IF NOT EXISTS idx_unified_users_platform ON unified_users(platform_id, platform_user_id);
CREATE INDEX IF NOT EXISTS idx_unified_properties_owner ON unified_properties(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_unified_bookings_dates ON unified_bookings(check_in, check_out);
CREATE INDEX IF NOT EXISTS idx_unified_transactions_platform ON unified_transactions(platform_id, created_at);
CREATE INDEX IF NOT EXISTS idx_admin_audit_log_admin ON admin_audit_log(admin_user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_verification_queue_status ON verification_queue(status, created_at);
CREATE INDEX IF NOT EXISTS idx_admin_notifications_user ON admin_notifications(admin_user_id, is_read);

-- Enable RLS on all tables
ALTER TABLE super_admin_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE platforms ENABLE ROW LEVEL SECURITY;
ALTER TABLE unified_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE unified_properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE unified_bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE unified_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE verification_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics_snapshots ENABLE ROW LEVEL SECURITY;

-- RLS Policies for super_admin_users
CREATE POLICY "Admins can view their own profile"
ON super_admin_users FOR SELECT
USING (auth.uid() = id);

CREATE POLICY "Admins can update their own profile"
ON super_admin_users FOR UPDATE
USING (auth.uid() = id);

-- RLS Policies for unified_users (readable by all admins)
CREATE POLICY "Admins can view all users"
ON unified_users FOR SELECT
TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM super_admin_users
        WHERE id = auth.uid() AND is_active = true
    )
);

-- Similar policies for other tables
CREATE POLICY "Admins can view all platforms"
ON platforms FOR SELECT
TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM super_admin_users
        WHERE id = auth.uid() AND is_active = true
    )
);

CREATE POLICY "Admins can view all properties"
ON unified_properties FOR SELECT
TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM super_admin_users
        WHERE id = auth.uid() AND is_active = true
    )
);

CREATE POLICY "Admins can view all bookings"
ON unified_bookings FOR SELECT
TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM super_admin_users
        WHERE id = auth.uid() AND is_active = true
    )
);

CREATE POLICY "Admins can view all transactions"
ON unified_transactions FOR SELECT
TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM super_admin_users
        WHERE id = auth.uid() AND is_active = true
    )
);

CREATE POLICY "Admins can view all audit logs"
ON admin_audit_log FOR SELECT
TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM super_admin_users
        WHERE id = auth.uid() AND is_active = true
    )
);

CREATE POLICY "Admins can insert audit logs"
ON admin_audit_log FOR INSERT
TO authenticated
WITH CHECK (admin_user_id = auth.uid());

CREATE POLICY "Admins can view verification queue"
ON verification_queue FOR SELECT
TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM super_admin_users
        WHERE id = auth.uid() AND is_active = true
    )
);

CREATE POLICY "Admins can view their notifications"
ON admin_notifications FOR SELECT
TO authenticated
USING (admin_user_id = auth.uid());

CREATE POLICY "Admins can update their notifications"
ON admin_notifications FOR UPDATE
TO authenticated
USING (admin_user_id = auth.uid());

-- Insert initial data
-- Create a default super admin (change password immediately!)
INSERT INTO super_admin_users (email, full_name, role, permissions)
VALUES (
    'admin@krib.ai',
    'Super Admin',
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
)
ON CONFLICT (email) DO NOTHING;

-- Insert platform configurations (you'll need to add actual API keys)
INSERT INTO platforms (name, display_name, api_base_url, api_key, status)
VALUES 
(
    'host_dashboard',
    'Host Dashboard',
    'https://krib-host-dahsboard-backend.onrender.com',
    'YOUR_HOST_DASHBOARD_API_KEY',
    'active'
),
(
    'agent_dashboard',
    'Real Estate Agent Dashboard',
    'https://krib-real-estate-agent-dahaboard-backend.onrender.com',
    'YOUR_AGENT_DASHBOARD_API_KEY',
    'active'
),
(
    'customer_platform',
    'Customer AI Platform',
    'https://krib-backend.onrender.com',
    'YOUR_CUSTOMER_PLATFORM_API_KEY',
    'active'
)
ON CONFLICT (name) DO NOTHING;

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
CREATE TRIGGER update_super_admin_users_updated_at BEFORE UPDATE ON super_admin_users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_platforms_updated_at BEFORE UPDATE ON platforms FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_unified_users_updated_at BEFORE UPDATE ON unified_users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_verification_queue_updated_at BEFORE UPDATE ON verification_queue FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

