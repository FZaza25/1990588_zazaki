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
            s_id = data.get("sensor_id")
            val = data.get("value")
            
            # --- 1. LOG GENERALE ---
            print(f"RECEIVED: {s_id} = {val}", flush=True)
            
            # --- 2. GESTIONE STATO (API REST) E WEBSOCKET ---
            # Per le REST API salviamo lo stato intero con il nome originale
            cache.set(f"sensor:{s_id}", json.dumps(data))
            
            # FILTRO WEBSOCKET: Trasmette solo i dati 'mars/telemetry/...' troncandone l'id
            if s_id and s_id.startswith("mars/telemetry/"):
                # Facciamo una copia per non rovinare i dati che vanno al DB
                stream_data = data.copy()
                # Tronchiamo la stringa sostituendo il prefisso
                stream_data['sensor_id'] = s_id.replace("mars/telemetry/", "")
                
                # Invia ad Andrea i dati con il nome pulito
                cache.publish("mars_telemetry_stream", json.dumps(stream_data))
                
            # Se il valore non è un numero, non possiamo fare confronti matematici
            if not isinstance(val, (int, float)):
                continue
            
            # --- 3. Controllo REGOLE ---
            try:
                conn = get_db_connection()
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM automation_rules WHERE sensor_name = %s", (s_id,))
                    rules = cur.fetchall()
                    
                    for rule in rules:
                        op = rule['operator']
                        threshold = float(rule['threshold_value'])
                        
                        # Verifica condizione: val > threshold o val < threshold, ecc.
                        triggered = False
                        if op == ">" and val > threshold: triggered = True
                        elif op == "<" and val < threshold: triggered = True
                        elif op == ">=" and val >= threshold: triggered = True
                        elif op == "<=" and val <= threshold: triggered = True
                        elif op == "==" and val == threshold: triggered = True
                        elif op == "!=" and val != threshold: triggered = True

                        if triggered:
                            print(f"\033[91m  [ALARM] \033[0m {s_id} ACTIVATE {rule['actuator_name']}! ({val} {op} {threshold}) ", flush=True)
                            trigger_actuator(rule['actuator_name'], rule['target_state'])
                        else:
                            print(f"  [EVAL] {s_id}: {val} {op} {threshold} → FALSE (no action)", flush=True)
                conn.close()
            except Exception as e:
                print(f"ERROR DB: {e}", flush=True)
