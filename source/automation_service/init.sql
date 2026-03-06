CREATE TABLE IF NOT EXISTS automation_rules (
    id SERIAL PRIMARY KEY,
    sensor_name VARCHAR(50) NOT NULL,
    operator VARCHAR(2) NOT NULL,
    threshold_value DECIMAL NOT NULL,
    threshold_unit VARCHAR(10),
    actuator_name VARCHAR(50) NOT NULL,
    target_state VARCHAR(3) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
