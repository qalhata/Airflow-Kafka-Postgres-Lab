CREATE TABLE IF NOT EXISTS sensor_readings (
    id SERIAL PRIMARY KEY,
    device_id INTEGER,
    temperature NUMERIC(5,2),
    timestamp BIGINT
);

--CREATE TABLE IF NOT EXISTS tweets (
--    id SERIAL PRIMARY KEY,
--    text TEXT,
--    sentiment TEXT,
--    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

CREATE TABLE IF NOT EXISTS tweet_entities (
    id SERIAL PRIMARY KEY,
    original_text TEXT,
    entities JSONB,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);