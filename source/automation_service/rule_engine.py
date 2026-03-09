import json, redis, time, sys
from kafka import KafkaConsumer
from persistence_layer import get_db_connection
import requests

KAFKA_TOPIC = "mars.telemetry.normalized"
BROKER = "kafka:9092"
SIMULATOR_URL = "http://simulator:8080"

def trigger_actuator(name, state):
    """Sends a REST POST command to the simulator actuators"""
    try:
        url = f"{SIMULATOR_URL}/api/actuators/{name}"
        payload = {"state": state}
        response = requests.post(url, json=payload, timeout=2)
        
        if response.status_code == 200:
            print(f"[ACTUATOR] {name} successfully set to {state}", flush=True)
        else:
            print(f"⚠[ACTUATOR] Failed to set {name}: Status {response.status_code}", flush=True)
    except Exception as e:
        print(f"[ACTUATOR] Connection error to simulator: {e}", flush=True)

print("[SYSTEM]: INITIATING RULE ENGINE (FULL LOGS)...", flush=True)

try:
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=[BROKER],
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='latest',
        api_version=(3, 7, 0),
        group_id=f'rule-engine-giulio-{time.time()}'
    )
    print(f"[SYSTEM] CONNECTED.", flush=True)
except Exception as e:
    print(f"[ERROR] FAILURE: {e}", flush=True)
    sys.exit(1)

cache = redis.Redis(host="mars_redis", port=6379, decode_responses=True)

while True:
    messages = consumer.poll(timeout_ms=1000)
    if not messages:
        continue

    for tp, msgs in messages.items():
        for message in msgs:
            data = message.value

            series_id = data.get("series_id")
            source_id = data.get("source_id")
            metric = data.get("metric")
            val = data.get("value")
            unit = data.get("unit")
            timestamp = data.get("timestamp")
            event_type = data.get("type")

            if not series_id or source_id is None:
                print(f"[WARN] Evento scartato: manca series_id/source_id -> {data}", flush=True)
                continue

            print(f"[RECEIVED] {series_id} = {val} {unit}", flush=True)

            # Cache latest-state per serie, non per sola sorgente
            cache.set(f"sensor:{series_id}", json.dumps(data))

            # Pubblica verso frontend
            cache.publish("mars_telemetry_stream", json.dumps(data))

            # Se non numerico, niente confronto regole
            if not isinstance(val, (int, float)):
                continue

            try:
                conn = get_db_connection()
                with conn.cursor() as cur:
                    # Compatibilità semplice:
                    # prima prova match su series_id, poi su source_id
                    cur.execute("""
                        SELECT * FROM automation_rules
                        WHERE sensor_name = %s OR sensor_name = %s
                    """, (series_id, source_id))
                    rules = cur.fetchall()

                    for rule in rules:
                        op = rule["operator"]
                        threshold = float(rule["threshold_value"])
                        rule_unit = rule["threshold_unit"]

                        # opzionale ma consigliato: se unità diversa, skippa
                        if rule_unit and unit and rule_unit != unit:
                            print(
                                f"[RULE SKIP] {series_id}: unit mismatch event={unit} rule={rule_unit}",
                                flush=True
                            )
                            continue

                        triggered = False
                        if op == ">" and val > threshold:
                            triggered = True
                        elif op == "<" and val < threshold:
                            triggered = True
                        elif op == ">=" and val >= threshold:
                            triggered = True
                        elif op == "<=" and val <= threshold:
                            triggered = True
                        elif op == "==" and val == threshold:
                            triggered = True
                        elif op == "!=" and val != threshold:
                            triggered = True

                        if triggered:
                            print(
                                f"[RULE TRUE] {timestamp} | {series_id}: {val} {op} {threshold} -> {rule['actuator_name']}={rule['target_state']}",
                                flush=True
                            )
                            trigger_actuator(rule["actuator_name"], rule["target_state"])
                        else:
                            print(
                                f"[RULE FALSE] {timestamp} | {series_id}: {val} {op} {threshold}",
                                flush=True
                            )

                conn.close()
            except Exception as e:
                print(f"[ERROR DB] {e}", flush=True)

