### How to run the system
1. Download .tar file from (provided by exam): https://drive.google.com/drive/folders/1Noa3Mp71Dao1QrZ4dyW2GvEAPnPUABZT

2. After download exec one-time:

   `docker load -i mars-iot-simulator-oci.tar`

   `docker run --rm -p 8080:8080 mars-iot-simulator:multiarch_v1`

3. Start full stack:
   docker compose up --build

Simulator: http://localhost:8080

API Gateway: http://localhost:8000 (REST + WS)

Dashboard: http://localhost:3000



# SYSTEM DESCRIPTION:

Mars Habitat Automation System is an IoT platform for automated control of a simulated Martian habitat.
Sensor data is collected from the simulator, normalized by the ingestion service, delivered through the broker, evaluated by the rule engine, and exposed by the API Gateway to the frontend dashboard.
The frontend supports real-time monitoring, rule CRUD, and manual/automatic actuator control.

# USER STORIES:

- US-01: REST Sensor Polling
- US-02: Telemetry Stream Consumption
- US-03: Unified Event Schema Normalization
- US-04: Message Broker Integration
- US-05: In-Memory State Caching
- US-06: Create Automation Rule
- US-07: List Active Rules
- US-08: Delete Automation Rule
- US-09: Rule Evaluation Engine
- US-10: Live Sensor Value Display
- US-11: Historical Telemetry Chart
- US-12: Manual Actuator Control
- US-13: Actuator Status Monitor
- US-14: Rule Persistence Across Restarts
- US-15: One-Command Deployment

FOR EXTEND VERSION OF US SEE:

[input.md](./input.md)

# CONTAINERS:

## CONTAINER_NAME: simulator

### DESCRIPTION:
Mars IoT simulator container that exposes virtual sensors and actuators.

### USER STORIES:
US-01, US-02, US-09, US-12, US-13

### PORTS:
8080:8080

### DESCRIPTION:
Provides REST sensor endpoints and actuator command endpoints used by ingestion and rule engine.

### PERSISTENCE EVALUATION
No application persistence required in this container.

### EXTERNAL SERVICES CONNECTIONS
No required outgoing dependency for core logic.

### MICROSERVICES:

#### MICROSERVICE: mars-iot-simulator
- TYPE: backend
- DESCRIPTION: External simulator service used as data source and actuator target.
- PORTS: 8080
- TECHNOLOGICAL SPECIFICATION:
Docker image `mars-iot-simulator:multiarch_v1`.
- SERVICE ARCHITECTURE:
Standalone service consumed by other project microservices.


## CONTAINER_NAME: kafka

### DESCRIPTION:
Message broker for decoupling ingestion and rule evaluation.

### USER STORIES:
US-04

### PORTS:
9092:9092, 29092:29092

### DESCRIPTION:
Receives normalized events and delivers them to subscribed consumers.

### PERSISTENCE EVALUATION
Broker persistence depends on Kafka internal log retention; no custom persistence layer configured in the project files.

### EXTERNAL SERVICES CONNECTIONS
Connected by ingestion service (producer) and rule engine (consumer).

### MICROSERVICES:

#### MICROSERVICE: kafka-broker
- TYPE: backend
- DESCRIPTION: Event broker for telemetry normalization pipeline.
- PORTS: 9092, 29092
- TECHNOLOGICAL SPECIFICATION:
Apache Kafka 3.7.0 container.
- SERVICE ARCHITECTURE:
Single-node broker/controller setup for local development.


## CONTAINER_NAME: ingestion_service

### DESCRIPTION:
Collects REST/SSE data from simulator and normalizes payloads into a common event format.

### USER STORIES:
US-01, US-02, US-03, US-04

### PORTS:
No published host ports.

### DESCRIPTION:
Publishes normalized events to Kafka topic `mars.telemetry.normalized`.

### PERSISTENCE EVALUATION
No persistent storage; stateless processing service.

### EXTERNAL SERVICES CONNECTIONS
- Simulator (`http://simulator:8080`)
- Kafka (`kafka:9092`)

### MICROSERVICES:

#### MICROSERVICE: ingestion
- TYPE: backend
- DESCRIPTION: Polls sensor endpoints and consumes telemetry streams, then normalizes and forwards events.
- PORTS: none
- TECHNOLOGICAL SPECIFICATION:
Python service with `requests`, `sseclient`, `kafka-python`.
- SERVICE ARCHITECTURE:
Multi-threaded polling/stream consumers + normalization + Kafka producer.

- ENDPOINTS:
	
	| HTTP METHOD | URL | Description | User Stories |
	| ----------- | --- | ----------- | ------------ |
	| N/A | N/A | Internal worker service, no public HTTP API | US-01, US-02, US-03, US-04 |


## CONTAINER_NAME: mars_db

### DESCRIPTION:
PostgreSQL database for actuator metadata and automation rules.

### USER STORIES:
US-06, US-07, US-08, US-09, US-14

### PORTS:
No published host port in compose.

### DESCRIPTION:
Stores persistent rule definitions and actuator state/mode.

### PERSISTENCE EVALUATION
Persistent via Docker volume `mars_db_data`.

### EXTERNAL SERVICES CONNECTIONS
Used by API Gateway and Rule Engine.

### MICROSERVICES:

#### MICROSERVICE: postgres
- TYPE: backend
- DESCRIPTION: Relational persistence layer.
- PORTS: none (internal Docker network)
- TECHNOLOGICAL SPECIFICATION:
PostgreSQL 15 alpine image, initialized with `init.sql`.
- SERVICE ARCHITECTURE:
Single DB instance, shared by backend services.

- DB STRUCTURE:

	**_actuators_** : | **_name_** | status | mode | last_update

	**_automation_rules_** : | **_id_** | sensor_name | operator | threshold_value | threshold_unit | actuator_name | target_state | created_at


## CONTAINER_NAME: state_store

### DESCRIPTION:
Redis cache/state store used for latest sensor state and pub/sub channels.

### USER STORIES:
US-05, US-10

### PORTS:
6379:6379

### DESCRIPTION:
Stores latest sensor and metric values in Redis keys (`sensor:*`) and broadcasts telemetry events on pub/sub channels. 
The API Gateway reads these keys via `/api/state` to expose the current snapshot to the frontend.

### PERSISTENCE EVALUATION
Primarily in-memory; no explicit durable persistence configured.

### EXTERNAL SERVICES CONNECTIONS
Used by Rule Engine and API Gateway.

### MICROSERVICES:

#### MICROSERVICE: redis-state-store
- TYPE: backend
- DESCRIPTION: Cache and pub/sub bus for state snapshots and updates.
- PORTS: 6379
- TECHNOLOGICAL SPECIFICATION:
Redis 7 alpine image.
- SERVICE ARCHITECTURE:
Single-node cache/pubsub service.


## CONTAINER_NAME: api_gateway

### DESCRIPTION:
Backend API layer exposing REST and WebSocket interfaces used by the frontend.

### USER STORIES:
US-05, US-06, US-07, US-08, US-10, US-12, US-13

### PORTS:
8000:8000

### DESCRIPTION:
Handles rule CRUD, actuator management, and websocket telemetry forwarding.
Manual actuator commands are first persisted in PostgreSQL and then forwarded to the simulator; if the simulator is unreachable, the DB state remains updated and the error is logged.


### PERSISTENCE EVALUATION
No direct persistence; delegates persistence to PostgreSQL and state reads to Redis.

### EXTERNAL SERVICES CONNECTIONS
- PostgreSQL (service: mars_db, container: mars_postgres)
- Redis (service: state_store, container: mars_redis)
- Simulator (service: simulator, base URL: http://simulator:8080)

### MICROSERVICES:

#### MICROSERVICE: api_gateway
- TYPE: backend
- DESCRIPTION: Main HTTP/WebSocket API service.
- PORTS: 8000
- TECHNOLOGICAL SPECIFICATION:
Python FastAPI + psycopg2 + redis client.
- SERVICE ARCHITECTURE:
Gateway pattern with CRUD endpoints and websocket relay.

- ENDPOINTS:
		
	| HTTP METHOD | URL | Description | User Stories |
	| ----------- | --- | ----------- | ------------ |
	| GET | /api/state | Returns current cached sensor state | US-05, US-10 |
	| GET | /api/rules | Returns all automation rules | US-07 |
	| POST | /api/rules | Creates a new automation rule | US-06 |
	| PATCH | /api/rules/{rule_id} | Updates an existing rule | US-06, US-07 |
	| DELETE | /api/rules/{rule_id} | Deletes an existing rule | US-08 |
	| GET | /api/actuators | Returns actuator list with mode/status | US-12, US-13 |
	| PATCH | /api/actuators/{name}/mode | Updates actuator mode (AUTO/MANUAL) | US-12 |
	| PATCH | /api/actuators/{name}/status | Updates actuator status (ON/OFF) | US-12, US-13 |
	| WS | /ws/telemetry | WebSocket stream for telemetry updates | US-10, US-11 |


## CONTAINER_NAME: rule_engine

### DESCRIPTION:
Consumes normalized events, evaluates automation rules, and triggers actuators.

### USER STORIES:
US-05, US-09, US-12

### PORTS:
No published host ports.

### DESCRIPTION:
Implements automatic behavior and respects actuator mode (AUTO vs MANUAL).

### PERSISTENCE EVALUATION
No local persistence; reads rules from PostgreSQL and state interactions through Redis/simulator.

### EXTERNAL SERVICES CONNECTIONS
- Kafka (service: kafka, bootstrap: kafka:9092)
- PostgreSQL (service: mars_db)
- Redis (service: state_store)
- Simulator (service: simulator, base URL: http://simulator:8080)

### MICROSERVICES:

#### MICROSERVICE: rule_engine
- TYPE: backend
- DESCRIPTION: Rule evaluator and actuator trigger executor.
- PORTS: none
- TECHNOLOGICAL SPECIFICATION:
Python service with Kafka consumer and HTTP client.
- SERVICE ARCHITECTURE:
Event-driven consumer loop with DB rule lookup and conditional actuator triggers.

- ENDPOINTS:
		
	| HTTP METHOD | URL | Description | User Stories |
	| ----------- | --- | ----------- | ------------ |
	| N/A | N/A | Internal worker service, no public HTTP API | US-09 |


## CONTAINER_NAME: frontend

### DESCRIPTION:
Vue dashboard for monitoring sensors/streams and managing actuators/rules.

### USER STORIES:
US-06, US-07, US-08, US-10, US-11, US-12, US-13

### PORTS:
3000:80

### DESCRIPTION:
Displays cards/charts/tables, supports rule CRUD from UI, and actuator manual control.

### PERSISTENCE EVALUATION
Frontend local state persistence via Pinia.

### EXTERNAL SERVICES CONNECTIONS
- API Gateway REST (`http://localhost:8000`)
- API Gateway WebSocket (`ws://localhost:8000/ws/telemetry`)

### MICROSERVICES:

#### MICROSERVICE: dashboard_frontend
- TYPE: frontend
- DESCRIPTION: Web user interface for monitoring and control.
- PORTS: 3000
- TECHNOLOGICAL SPECIFICATION:
Vue 3 + Vite + Pinia + Vuetify + Chart.js.
- SERVICE ARCHITECTURE:
SPA with route-based views and shared component/store architecture.

- PAGES:

	| Name | Description | Related Microservice | User Stories |
	| ---- | ----------- | -------------------- | ------------ |
	| Home | Landing / entry screen della dashboard | api_gateway | US-15 |
	| Monitoring / Indoor Environment | Sensor cards and historical charts for indoor sensors | api_gateway | US-10 |
	| Monitoring / Water System | Sensor cards and historical charts for water/hydroponic sensors | api_gateway | US-10 |
	| Monitoring / Energy and Global Systems | Stream cards and telemetry charts | api_gateway | US-11 |
	| Monitoring / Actuators | Rules table, rule CRUD, manual/automatic actuator control | api_gateway | US-06, US-07, US-08, US-12, US-13 |

#### <other microservices>

## <other containers>
