import json, redis, time, sys
from kafka import KafkaConsumer
from persistence_layer import get_db_connection
import requests

TOPIC = "mars.telemetry.normalized"
BROKER = "kafka:9092"
SIMULATOR_URL = "http://simulator:8080"

# Connessione a Redis (Nome host allineato al docker-compose)
cache = redis.Redis(host="state_store", port=6379, decode_responses=True)

def trigger_actuator(name, state):
    """Invia il comando al simulatore e sincronizza Database e Cache"""
    try:
        # 1. Controllo Anti-Spam (Redis)
        last_state_key = f"last_cmd:{name}"
        last_sent_state = cache.get(last_state_key)
        
        if last_sent_state == state:
            return 

        # 2. Invio al simulatore
        url = f"{SIMULATOR_URL}/api/actuators/{name}"
        payload = {"state": state}
        
        print(f"[DEBUG] Cambio stato rilevato! Invio a simulatore: {payload}", flush=True)
        response = requests.post(url, json=payload, timeout=2)
        
        if response.status_code == 200:
            print(f"[INFO] Attuatore {name} impostato a {state}", flush=True)
            
            # 3. Aggiorna Cache
            cache.set(last_state_key, state)
            
            # 4. Aggiorna Database (Sincronizzazione Dashboard)
            try:
                conn = get_db_connection()
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE actuators SET status = %s, last_update = CURRENT_TIMESTAMP WHERE name = %s",
                        (state, name)
                    )
                    conn.commit()
                conn.close()
            except Exception as e:
                print(f"[ERROR] Database update failed: {e}", flush=True)
        else:
            print(f"[ERROR] Il simulatore ha rifiutato il comando: {response.status_code}", flush=True)
            
    except Exception as e:
        print(f"[ERROR] Errore connessione simulatore: {e}", flush=True)

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
        source_id = data.get('source_id', '')
        val = data.get('value')
        metric = data.get('metric', 'default')

        if source_id and val is not None:
            clean_id = source_id.replace("mars/telemetry/", "")
            is_telemetry = source_id.startswith("mars/telemetry/")
            
            data['sensor_id'] = clean_id
            
            # Distribuzione canali
            if is_telemetry:
                cache.publish("mars_telemetry_stream", json.dumps(data))
            else:
                cache.set(f"sensor:{clean_id}:{metric}", json.dumps(data))

            # --- LOGICA AUTOMAZIONE ---
            if isinstance(val, (int, float)):
                try:
                    conn = get_db_connection()
                    with conn.cursor() as cur:
                        # JOIN per controllare la modalità (AUTO/MANUAL)
                        query = """
                            SELECT r.*, a.mode 
                            FROM automation_rules r
                            JOIN actuators a ON r.actuator_name = a.name
                            WHERE r.sensor_name = %s
                        """
                        cur.execute(query, (clean_id,))
                        rules = cur.fetchall()
                        
                        for rule in rules:
                            if rule['mode'] != 'AUTO':
                                continue

                            op = rule['operator']
                            threshold = float(rule['threshold_value'])
                            triggered = False

                            if op == ">" and val > threshold: triggered = True
                            elif op == "<" and val < threshold: triggered = True
                            elif op == "==" and val == threshold: triggered = True
                            elif op == ">=" and val >= threshold: triggered = True
                            elif op == "<=" and val <= threshold: triggered = True
                            
                            if triggered:
                                print(f"[ALERT] Automation triggered: {clean_id} {val} {op} {threshold}", flush=True)
                                trigger_actuator(rule['actuator_name'], rule['target_state'])
                    conn.close()
                except Exception as e:
                    print(f"[ERROR] Database query failed: {e}", flush=True)

except Exception as e:
    print(f"[CRITICAL] Rule Engine failure: {e}", flush=True)