-- Phase 2: Authentication Schema Migration
-- Profiles table for user tier and segment tracking

CREATE TABLE IF NOT EXISTS profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT UNIQUE,
  tier TEXT DEFAULT 'free' CHECK (tier IN ('free', 'contractor_pro', 'ic_consultant', 'sponsor_admin', 'partner_admin')),
  customer_segment TEXT DEFAULT 'contractor' CHECK (customer_segment IN ('contractor', 'ic_consultant', 'sponsor', 'partner', 'admin')),
  company_name TEXT,
  trial_active BOOLEAN DEFAULT false,
  trial_expires_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_tier ON profiles(tier);
CREATE INDEX IF NOT EXISTS idx_profiles_segment ON profiles(customer_segment);
