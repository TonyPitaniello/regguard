-- Result Deliveries Tracking
-- Tracks SMS and email deliveries of research results

CREATE TABLE IF NOT EXISTS result_deliveries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  research_id UUID NOT NULL,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  delivery_method TEXT NOT NULL CHECK (delivery_method IN ('sms', 'email')),
  destination TEXT NOT NULL,  -- phone number or email address
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed')),
  service_message_id TEXT,  -- Twilio SID or SendGrid message ID
  error_message TEXT,  -- Error details if failed
  sent_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT now(),
  updated_at TIMESTAMP NOT NULL DEFAULT now()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_result_deliveries_user_id ON result_deliveries(user_id);
CREATE INDEX IF NOT EXISTS idx_result_deliveries_research_id ON result_deliveries(research_id);
CREATE INDEX IF NOT EXISTS idx_result_deliveries_created_at ON result_deliveries(created_at);
CREATE INDEX IF NOT EXISTS idx_result_deliveries_status ON result_deliveries(status);

-- Add rate limiting tracking table
CREATE TABLE IF NOT EXISTS delivery_rate_limits (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  delivery_method TEXT NOT NULL CHECK (delivery_method IN ('sms', 'email')),
  hour_slot TIMESTAMP NOT NULL,  -- Truncated to hour boundary
  count INT NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT now(),
  updated_at TIMESTAMP NOT NULL DEFAULT now(),
  UNIQUE(user_id, delivery_method, hour_slot)
);

CREATE INDEX IF NOT EXISTS idx_delivery_rate_limits_user_method ON delivery_rate_limits(user_id, delivery_method, hour_slot);
