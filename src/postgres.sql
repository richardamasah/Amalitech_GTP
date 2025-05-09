-- src/postgres.sql
-- Creates the PostgreSQL database and table for e-commerce events.

-- Create database (manually created via environment variable in Docker)
-- Note: Database 'ecommerce_db' is created by POSTGRES_DB in docker-compose.yml

-- Create table for e-commerce events
CREATE TABLE ecommerce_events (
    event_id VARCHAR(36) PRIMARY KEY,  -- Unique event ID (UUID)
    user_id VARCHAR(36) NOT NULL,     -- User ID (UUID)
    action VARCHAR(20) NOT NULL,      -- Action (view, purchase)
    product_id VARCHAR(10) NOT NULL,  -- Product ID
    product_name VARCHAR(50) NOT NULL,-- Product name
    category VARCHAR(50) NOT NULL,    -- Product category
    price FLOAT NOT NULL,             -- Product price
    timestamp TIMESTAMPTZ NOT NULL,   -- Event timestamp
    CONSTRAINT valid_action CHECK (action IN ('view', 'purchase')),
    CONSTRAINT valid_price CHECK (price >= 0)
);

-- Index for efficient time-based queries
CREATE INDEX idx_timestamp ON ecommerce_events (timestamp);

-- Index for user-based queries
CREATE INDEX idx_user_id ON ecommerce_events (user_id);