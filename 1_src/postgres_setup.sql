-- scripts/postgres_setup.sql
-- Create user_events table with indexed columns and created_at
CREATE TABLE IF NOT EXISTS user_events (
    event_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    event_type VARCHAR(10) NOT NULL,
    product_id VARCHAR(36),
    product_name VARCHAR(100),
    price FLOAT,
    timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_user_id ON user_events (user_id);
CREATE INDEX IF NOT EXISTS idx_event_type ON user_events (event_type);