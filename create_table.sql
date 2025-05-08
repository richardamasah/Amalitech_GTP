CREATE TABLE heart_rate_data (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    heart_rate INTEGER NOT NULL,
    age INTEGER NOT NULL,
    weight FLOAT NOT NULL,
    CONSTRAINT valid_heart_rate CHECK (heart_rate >= 40 AND heart_rate <= 140),
    CONSTRAINT valid_age CHECK (age >= 18 AND age <= 80),
    CONSTRAINT valid_weight CHECK (weight >= 40 AND weight <= 120)
);

CREATE INDEX idx_timestamp ON heart_rate_data (timestamp);
CREATE INDEX idx_customer_id ON heart_rate_data (customer_id);