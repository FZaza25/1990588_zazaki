# Mars IoT Automation Platform

**Laboratory of Advanced Programming 2025/2026**  
**Team:** Zazaki  
**Leader Matricola:** 1990588  
**Members:** Federico Zaza, Giulio Maria Schintu, Andrea Pulsoni

---

## 1. System Description:

This project implements a distributed automation platform for managing a compromised Martian habitat. The system ingests heterogeneous IoT sensor data from REST polling and telemetry streams (SSE/WebSocket), normalizes it into a unified event format, evaluates automation rules dynamically, and provides a real-time dashboard for habitat monitoring.

### Architecture

The platform follows an **Event-Driven Microservices Architecture** with the following components:

- **IoT Simulator** (`mars-iot-simulator:multiarch_v1`): Simulates Mars habitat sensors and actuators on port 8080
- **Ingestion & Normalization Service**: Polls REST sensors and consumes telemetry streams, normalizes data, publishes to message broker
- **Message Broker** (Kafka): Decouples services via pub/sub pattern
- **Automation Rule Engine**: Consumes events, evaluates rules, triggers actuators, maintains in-memory state cache
- **Database** (SQLite/PostgreSQL): Persists automation rules
- **API Gateway**: Exposes REST APIs for frontend, manages WebSocket connections
- **Frontend Dashboard** (Vue.js): Real-time monitoring, manual actuator control, rule management

**Data Flow:**
```
Simulator → Ingestion Service → Broker → Rule Engine → Actuators
                                   ↓
                              State Cache
                                   ↓
                           API Gateway → Frontend
```

All services are containerized with Docker and orchestrated via `docker-compose`.

### Standard Event Schema
To decouple the business logic from the specific hardware dialects provided by the simulator's OpenAPI, the Ingestion Service flattens all incoming data (from both REST and Telemetry streams) into a single, predictable JSON Standard Event Schema before publishing to the message broker:
{
  "sensor_id": "string",          // id 'pulito', es: 'greenhouse_temperature', 'solar_array'
  "source_id": "string",          // id sorgente completo, es: 'mars/telemetry/solar_array'
  "series_id": "string",          // combinazione sensor_id + metric, es: 'solar_array:power'
  "metric": "string",             // tipo di misura, es: 'power', 'temperature', 'co2ppm'
  "timestamp": "string (ISO 8601)",
  "value": "number or string",
  "unit": "string",
  "type": "string (schema type, es: rest.scalar.v1, topic.power.v1)",
  "status": "string (ok / warning / error)",
  "tags": {
    "subsystem": "string (optional)",
    "system": "string (optional)",
    "segment": "string (optional)",
    "loop": "string (optional)",
    "airlock_id": "string (optional)"
  }
}
Nota: Nel Rule Engine, sensor_name usato dalle regole corrisponde a sensor_id normalizzato (es. "greenhouse_temperature", "co2_hall", "solar_array").
This guarantees that downstream services (Rule Engine and Dashboard) can process any event uniformly, regardless of its origin.

### Rule Model
The automation logic is defined through a straightforward relational model, evaluated dynamically by the Rule Engine upon receiving a new event from the broker.

**Logical Syntax:** `IF <sensor_name> <operator> <value> THEN set <actuator_name> to <ON|OFF>`

Rules are persisted in a relational database using the following schema mapping to ensure fault tolerance across service restarts:

* **`id`** (Primary Key)
* **`sensor_name`** (Target telemetry)
* **`operator`** (Evaluation logic: `>`, `<`, `==`, `!=`, `>=`, `<=`)
* **`threshold_value`** (Numeric trigger point)
* **`actuator_name`** (Target hardware)
* **`target_state`** (`ON` or `OFF`)

---

## 2. User Stories

### Core Infrastructure & Data Ingestion (5 stories)

#### US-01: REST Sensor Polling
**As a** system operator  
**I want** the platform to automatically poll REST-based sensors at regular intervals  
**So that** I can monitor critical environmental parameters without manual intervention

**Acceptance Criteria:**
- System polls all required REST sensors exposed by the simulator via /api/sensors/{sensor_name}, as configured in the ingestion service (rest_sensors list).
- Polling interval configurable (default: 5 seconds)
- Data successfully published to message broker

---

#### US-02: Telemetry Stream Consumption
**As a** system operator  
**I want** the platform to consume real-time telemetry streams via SSE or WebSocket  
**So that** I can receive asynchronous updates from critical systems (solar array, radiation, life support)

**Acceptance Criteria:**



- Ingestion service subscribes via SSE to all simulator telemetry topics at /api/telemetry/stream/{topic_name} (list defined in telemetry_topics).
- Normalized telemetry events are published to Kafka topic "mars.telemetry.normalized".
- API Gateway subscribes to Redis channel "mars_telemetry_stream" and forwards telemetry to the frontend WebSocket at ws://localhost:8000/ws/telemetry.
- Connection is re-established automatically on failure.


---

#### US-03: Unified Event Schema Normalization
**As a** backend developer  
**I want** all heterogeneous sensor data normalized into a unified JSON schema  
**So that** downstream services can process events uniformly

**Acceptance Criteria:**
- REST sensors (scalar.v1, chemistry.v1, level.v1, particulate.v1) mapped to unified schema
- Telemetry topics (power.v1, environment.v1, thermalloop.v1, airlock.v1) mapped to unified schema
- Schema includes: `event_id`, `sensor_name`, `timestamp`, `value`, `unit`, `source_type`
- Normalization documented in Section 3

---

#### US-04: Message Broker Integration
**As a** system architect  
**I want** all sensor events published to a message broker 
**So that** the system follows event-driven architecture and services are decoupled

**Acceptance Criteria:**
- Broker (Kafka) configured in docker-compose.yml.
- Ingestion service publishes all normalized events to Kafka topic "mars.telemetry.normalized".
- Rule engine consumes from "mars.telemetry.normalized".
- API Gateway publishes real-time updates to Redis channels: "mars_telemetry_stream" (telemetry), "rules_update" (rule changes), "actuator_updates" (actuator state).
- Frontend consumes current state via REST /api/state and real-time telemetry via WebSocket /ws/telemetry.



---

#### US-05: In-Memory State Caching
**As a** system operator  
**I want** the latest value of each sensor cached in memory  
**So that** the dashboard loads instantly without querying historical data

**Acceptance Criteria:**
- Rule engine maintains map: `{sensor_name: {value, unit, timestamp}}`
- State updated on every incoming event
- REST API `/api/state` exposes current state
- Cache survives rule engine restarts (rehydrated from last events)

---

### Automation Rule Engine (4 stories)

#### US-06: Create Automation Rule
**As a** habitat manager  
**I want** to define automation rules using IF-THEN logic  
**So that** actuators respond automatically to sensor thresholds

**Syntax (EXACT as per exam specification):**
```
IF <sensor_name> <operator> <value> [unit] THEN set <actuator_name> to ON|OFF
```

**Acceptance Criteria:**
- UI table for each Actuator contains its own rules.
- Rule validated before saving
- Rule persisted to database 

**Examples:**
- `IF greenhouse_temperature > 28 C THEN set cooling_fan to ON`
- `IF entrance_humidity < 30 % THEN set entrance_humidifier to ON`
- `IF corridor_pressure < 95 kPa THEN set hall_ventilation to OFF`

---

#### US-07: List Active Rules
**As a** habitat manager  
**I want** to view all active automation rules in a table  
**So that** I can audit the system's autonomous behavior

**Acceptance Criteria:**
- Table displays: Sensor, Sensor value, Operator, Threshold, Target state and action
- Rules fetched from persistent database
- Table updates in real-time when rules added/deleted

---

#### US-08: Delete Automation Rule
**As a** habitat manager  
**I want** to delete an automation rule  
**So that** I can remove outdated or conflicting logic

**Acceptance Criteria:**
- Delete button next to each rule in table
- Rule removed from database
- Rule engine stops evaluating deleted rule immediately

---

#### US-09: Rule Evaluation Engine
**As a** system  
**I want** to evaluate incoming sensor events against all active rules  
**So that** actuators are triggered automatically when conditions are met

**Acceptance Criteria:**
- On event arrival, fetch rules matching `sensor_name`
- Parse rule statement: extract operator, threshold value, unit, actuator name, target state
- Evaluate condition: compare `event.value` with rule threshold using specified operator
- If condition TRUE: send POST to `/api/actuators/{actuator_name}` with body `{"state": "ON"}` or `{"state": "OFF"}`
- Log all rule evaluations with timestamp and result (for debugging)

**Example Flow:**
```
Event received: {sensor_name: "greenhouse_temperature", value: 29.5, unit: "C"}
Rule in DB: "IF greenhouse_temperature > 28 C THEN set cooling_fan to ON"
Evaluation: 29.5 > 28 → TRUE
Action: POST http://localhost:8080/api/actuators/cooling_fan {"state": "ON"}
```

---

### Real-Time Dashboard (4 stories)

#### US-10: Live Sensor Value Display
**As a** habitat operator  
**I want** to see the latest value of all sensors on a dashboard  
**So that** I can monitor habitat conditions at a glance

**Acceptance Criteria:**
- Dashboard displays cards for each sensor: name, value, unit, charts
- Values update via polling every 5 seconds

---

#### US-11: Historical Telemetry Chart
**As an** engineer  
**I want** to visualize telemetry streams as line charts  
**So that** I can identify trends and anomalies over time

**Acceptance Criteria:**
- Line chart for selected sensor (e.g., `solar_array`, `radiation`, `power_consumption`)
- X-axis: time (last 5 minutes)
- Y-axis: sensor value
- Chart updates every 5 seconds
- Tooltip shows exact value on hover
---

#### US-12: Manual Actuator Control
**As a** habitat operator  
**I want** to manually override actuator states via toggle switches  
**So that** I can respond to emergencies independently of automation rules

**Acceptance Criteria:**
- Toggle switch for each actuator: `cooling_fan`, `entrance_humidifier`, `hall_ventilation`, `habitat_heater`
- Mode toggle sends PATCH to /api/actuators/{actuatorName}/mode with body {"mode": "AUTO"} or {"mode": "MANUAL"}.
- ON/OFF toggle sends PATCH to /api/actuators/{actuatorName}/status with body {"status": "ON"} or {"status": "OFF"}; the API Gateway forwards {"state": "ON"/"OFF"} to the simulator.
- Current state fetched on dashboard load from `/api/actuators`
- Switch disabled during API call (loading state)

---

#### US-13: Actuator Status Monitor
**As a** maintenance technician  
**I want** to see the current state of all actuators  
**So that** I can verify physical hardware matches software commands

**Acceptance Criteria:**
- Dashboard section lists all actuators with ON/OFF switches
- Status polled from `/api/actuators` every 5 if auto is selected seconds
- Switch colors: orange (ON), gray (OFF)

---

### System Reliability & DevOps (2 stories)

#### US-14: Rule Persistence Across Restarts
**As a** system administrator  
**I want** automation rules to persist in a database  
**So that** life-support automations resume immediately after system crashes

**Acceptance Criteria:**
- Rules stored in PostgreSQL/MongoDB/SQLite
- Database initialized via Docker volume
- Rule engine loads rules from DB on startup
- **Test:** Create rule → `docker-compose restart` → rule still exists and evaluates correctly

---

#### US-15: One-Command Deployment
**As an** instructor  
**I want** to start the entire system with `docker-compose up`  
**So that** I can reproduce the project environment without manual setup

**Acceptance Criteria:**
- `docker-compose.yml` includes: simulator, broker, database, backend services, frontend
- All services start automatically with correct dependencies (`depends_on`)
- Health checks ensure services ready before dependent services start
- Simulator accessible at `http://localhost:8080`
- Dashboard accessible at `http://localhost:3000`
- No manual configuration steps required

---

