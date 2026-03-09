-- 1. Tabella Anagrafica Attuatori
CREATE TABLE IF NOT EXISTS actuators (
    name VARCHAR(50) PRIMARY KEY,
    status VARCHAR(10) DEFAULT 'OFF',
    mode VARCHAR(10) DEFAULT 'AUTO', -- 'AUTO' o 'MANUAL'
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabella Regole con Chiave Esterna (FK)
CREATE TABLE IF NOT EXISTS automation_rules (
    id SERIAL PRIMARY KEY,
    sensor_name VARCHAR(50) NOT NULL,
    operator VARCHAR(2) NOT NULL,
    threshold_value DECIMAL NOT NULL,
    threshold_unit VARCHAR(10),
    actuator_name VARCHAR(50) REFERENCES actuators(name) ON DELETE CASCADE,
    target_state VARCHAR(10) NOT NULL, -- Aumentato a 10 per supportare 'OPEN', 'HIGH', ecc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Popolamento iniziale dei 4 attuatori reali del simulatore
INSERT INTO actuators (name, mode) VALUES 
('cooling_fan', 'AUTO'),
('habitat_heater', 'AUTO'),
('hall_ventilation', 'AUTO'),
('entrance_humidifier', 'AUTO')
ON CONFLICT (name) DO NOTHING;


-- Regole di default per la demo
INSERT INTO automation_rules (sensor_name, operator, threshold_value, actuator_name, target_state) VALUES 
('greenhouse_temperature', '>', 25.0, 'cooling_fan', 'ON'),
('greenhouse_temperature', '<', 18.0, 'habitat_heater', 'ON'),
('co2_hall', '>', 1000.0, 'hall_ventilation', 'ON'),
('entrance_humidity', '<', 30.0, 'entrance_humidifier', 'ON')
ON CONFLICT DO NOTHING;