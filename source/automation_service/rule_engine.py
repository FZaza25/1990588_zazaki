import json, redis, time, sys
from kafka import KafkaConsumer
from persistence_layer import get_db_connection
import requests

TOPIC = "mars.telemetry.normalized"
BROKER = "kafka:9092"
SIMULATOR_URL = "http://simulator:8080"

# Redis Connection for State Store and Pub/Sub
cache = redis.Redis(host="mars_redis", port=6379, decode_responses=True)

def trigger_actuator(name, state):
    """Sends a REST POST command to the simulator actuators"""
    try:
        url = f"{SIMULATOR_URL}/api/actuators/{name}"
        payload = {"state": state}
        response = requests.post(url, json=payload, timeout=2)
        
        if response.status_code == 200:
            print(f"[INFO] Actuator {name} successfully set to {state}", flush=True)
        else:
            print(f"[ERROR] Failed to set actuator {name}: Status {response.status_code}", flush=True)
    except Exception as e:
        print(f"[ERROR] Actuator connection failure: {e}", flush=True)

print("[SYSTEM] Initializing Rule Engine service...", flush=True)

try:
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=[BROKER],
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='latest',
        api_version=(3, 7, 0),
        group_id=f'rule-engine-giulio-{time.time()}'
    )
    print("[SYSTEM] Kafka consumer connected. Routing protocol: ACTIVE", flush=True)

    for message in consumer:
        data = message.value
        
        # 1. DATA EXTRACTION
        source_id = data.get('source_id', '')
        series_id = data.get('series_id', '')
        val = data.get('value')
        metric = data.get('metric', 'default')

        if source_id and val is not None:
            
            # --- 2. ROUTING LOGIC & PREFIX REMOVAL ---
            # Telemetry is identified by the "mars/telemetry/" prefix in source_id
            is_telemetry = source_id.startswith("mars/telemetry/")
            
            # Remove prefix for clean output (e.g., mars/telemetry/solar_array -> solar_array)
            clean_id = source_id.replace("mars/telemetry/", "")
            
            # Normalize JSON payload for Gateway/Frontend requirements
            data['sensor_id'] = clean_id
            data['source_id'] = clean_id
            data['metric'] = metric

            # --- 3. CHANNEL DISTRIBUTION ---
            if is_telemetry:
                # STREAM CHANNEL: Published to WebSocket subscribers
                # Includes metric and cleaned ID
                cache.publish("mars_telemetry_stream", json.dumps(data))
                print(f"[DEBUG] Telemetry Stream: {clean_id} | {metric}: {val}", flush=True)
            else:
                # REST CHANNEL: Stored in Redis for state polling
                # Key format: sensor:{id}:{metric}
                cache.set(f"sensor:{clean_id}:{metric}", json.dumps(data))
                print(f"[DEBUG] Sensor State Updated: {clean_id} | {metric}", flush=True)

            # --- 4. AUTOMATION RULES ENGINE ---
            if isinstance(val, (int, float)):
                try:
                    conn = get_db_connection()
                    with conn.cursor() as cur:
                        # Match rules using the cleaned sensor name
                        cur.execute("SELECT * FROM automation_rules WHERE sensor_name = %s", (clean_id,))
                        rules = cur.fetchall()
                        
                        for rule in rules:
                            op = rule['operator']
                            threshold = float(rule['threshold_value'])
                            
                            triggered = False
                            if op == ">" and val > threshold: triggered = True
                            elif op == "<" and val < threshold: triggered = True
                            elif op == "==" and val == threshold: triggered = True
                            elif op == ">=" and val >= threshold: triggered = True
                            elif op == "<=" and val <= threshold: triggered = True
                            
                            if triggered:
                                print(f"[ALERT] Automation triggered: {clean_id} ({metric}) {val} {op} {threshold}", flush=True)
                                trigger_actuator(rule['actuator_name'], rule['target_state'])
                    conn.close()
                except Exception as e:
                    print(f"[ERROR] Database query failed: {e}", flush=True)

except Exception as e:
    print(f"[CRITICAL] Rule Engine failure: {e}", flush=True)