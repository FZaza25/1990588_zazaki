# Mars IoT Automation Platform

**Laboratory of Advanced Programming 2025/2026**  
**Team:** Zazaki  
**Leader Matricola:** 1990588  
**Members:** Federico Zaza, Giulio Schintu, Andrea Pulsoni

---

## 1. System Description:

This project implements a distributed automation platform for managing a compromised Martian habitat. The system ingests heterogeneous IoT sensor data from REST polling and telemetry streams (SSE/WebSocket), normalizes it into a unified event format, evaluates automation rules dynamically, and provides a real-time dashboard for habitat monitoring.

### Architecture

The platform follows an **Event-Driven Microservices Architecture** with the following components:

- **IoT Simulator** (`mars-iot-simulator:multiarch_v1`): Simulates Mars habitat sensors and actuators on port 8080
- **Ingestion & Normalization Service**: Polls REST sensors and consumes telemetry streams, normalizes data, publishes to message broker
- **Message Broker** (Kafka/RabbitMQ): Decouples services via pub/sub pattern
- **Automation Rule Engine**: Consumes events, evaluates rules, triggers actuators, maintains in-memory state cache
- **Database** (SQLite/PostgreSQL): Persists automation rules
- **API Gateway**: Exposes REST APIs for frontend, manages WebSocket connections
- **Frontend Dashboard** (React): Real-time monitoring, manual actuator control, rule management

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
  "sensor_id": "string",
  "timestamp": "string (ISO 8601)",
  "metric": "string",
  "value": "number or string",
  "unit": "string",
  "status": "string (ok/warning)",
  "subsystem": "string (optional)",
  "loop": "string (optional)",
  "airlock_id": "string (optional)"
}
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
- System polls all REST sensors listed in `/api/sensors` endpoint
- Polling interval configurable (default: 5 seconds)
- Failed polls are logged and retried
- Data successfully published to message broker

---

#### US-02: Telemetry Stream Consumption
**As a** system operator  
**I want** the platform to consume real-time telemetry streams via SSE or WebSocket  
**So that** I can receive asynchronous updates from critical systems (solar array, radiation, life support)

**Acceptance Criteria:**
- System subscribes to all topics from `/api/telemetry/topics`
- Connection reconnects automatically on failure
- Telemetry data parsed and forwarded to message broker
- Stream latency < 1 second

**Non-Functional Requirements:**
- Stream latency: < 1 second
- Reconnection delay: 2 seconds with exponential backoff

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

**Non-Functional Requirements:**
- Normalization overhead: < 10ms per event

---

#### US-04: Message Broker Integration
**As a** system architect  
**I want** all sensor events published to a message broker 
**So that** the system follows event-driven architecture and services are decoupled

**Acceptance Criteria:**
- Broker configured in `docker-compose.yml`
- Ingestion service publishes to `sensor.events` topic
- Rule engine consumes from `sensor.events` topic
- Frontend subscribes to `state.updates` topic
- Messages persist during service restarts

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

**Non-Functional Requirements:**
- API response time: < 50ms
- Cache memory footprint: < 100MB

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
- UI form accepts: sensor name (dropdown), operator (`>`, `<`, `>=`, `<=`, `==`, `!=`), value (number), unit (text), actuator name (dropdown), state (ON/OFF radio buttons)
- Rule validated before saving
- Rule persisted to database 

**Examples:**
- `IF greenhouse_temperature > 28 C THEN set cooling_fan to ON`
- `IF entrance_humidity < 30 % THEN set entrance_humidifier to ON`
- `IF corridor_pressure < 95 kPa THEN set hall_ventilation to OFF`

**Non-Functional Requirements:**
- Form validation: instant client-side feedback
- Database insert latency: < 200ms

---

#### US-07: List Active Rules
**As a** habitat manager  
**I want** to view all active automation rules in a table  
**So that** I can audit the system's autonomous behavior

**Acceptance Criteria:**
- Table displays: Rule ID, Condition (full IF-THEN statement), Created Date
- Rules fetched from persistent database
- Table updates in real-time when rules added/deleted
- Empty state message if no rules exist

**Non-Functional Requirements:**
- Table load time: < 500ms
- Real-time update latency: < 1 second

---

#### US-08: Delete Automation Rule
**As a** habitat manager  
**I want** to delete an automation rule  
**So that** I can remove outdated or conflicting logic

**Acceptance Criteria:**
- Delete button next to each rule in table
- Confirmation dialog before deletion
- Rule removed from database
- Rule engine stops evaluating deleted rule immediately

**Non-Functional Requirements:**
- Deletion latency: < 300ms
- No downtime for remaining rules during deletion

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

**Non-Functional Requirements:**
- Evaluation latency: < 100ms per rule
- Support for concurrent rule evaluations (thread-safe)

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
- Dashboard displays cards for each sensor: name, value, unit, timestamp
- Values update in real-time via WebSocket/SSE
- Color-coded status: green (normal), yellow (warning), red (critical)
- Sensors grouped by category: Temperature, Pressure, Humidity, Air Quality, Power, Life Support

**Non-Functional Requirements:**
- Update frequency: real-time (< 1 second latency)
- UI responsiveness: 60 FPS rendering

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

**Non-Functional Requirements:**
- Chart rendering: < 100ms
- Data retention in browser: last 5 minutes (300 data points max)

---

#### US-12: Manual Actuator Control
**As a** habitat operator  
**I want** to manually override actuator states via toggle switches  
**So that** I can respond to emergencies independently of automation rules

**Acceptance Criteria:**
- Toggle switch for each actuator: `cooling_fan`, `entrance_humidifier`, `hall_ventilation`, `habitat_heater`
- Switch sends POST to `/api/actuators/{actuator_name}` with `{"state": "ON"}` or `{"state": "OFF"}`
- Current state fetched on dashboard load from `/api/actuators`
- Switch disabled during API call (loading state)

**Non-Functional Requirements:**
- Toggle response time: < 500ms
- Visual feedback: switch animates to new position

---

#### US-13: Actuator Status Monitor
**As a** maintenance technician  
**I want** to see the current state of all actuators  
**So that** I can verify physical hardware matches software commands

**Acceptance Criteria:**
- Dashboard section lists all actuators with ON/OFF badges
- Status polled from `/api/actuators` every 10 seconds
- Badge colors: green (ON), gray (OFF)
- Last updated timestamp displayed

**Non-Functional Requirements:**
- Polling interval: 10 seconds
- UI update latency: < 100ms

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

**Non-Functional Requirements:**
- Database startup time: < 5 seconds
- Rule loading latency: < 1 second

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

**Non-Functional Requirements:**
- Total startup time: < 60 seconds
- Zero manual intervention required

---

