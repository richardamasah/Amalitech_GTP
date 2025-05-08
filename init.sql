-- init.sql
-- Creates the heart_rates table in PostgreSQL.

CREATE TABLE heart_rates (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    time TIMESTAMPTZ NOT NULL,
    rate INTEGER NOT NULL,
    CONSTRAINT valid_rate CHECK (rate > 0 AND rate <= 200)
);

-- Index for time-series queries
CREATE INDEX idx_time ON heart_rates (time);