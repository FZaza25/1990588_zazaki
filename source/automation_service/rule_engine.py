import json, redis, time, sys
from kafka import KafkaConsumer
from persistence_layer import get_db_connection
import requests

TOPIC = "mars.telemetry.normalized"
BROKER = "kafka:9092"
SIMULATOR_URL = "http://simulator:8080"

# Connessione a Redis (il nostro State Store)
cache = redis.Redis(host="mars_redis", port=6379, decode_responses=True)

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
        TOPIC,
        bootstrap_servers=[BROKER],
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='latest',
        api_version=(3, 7, 0),
        group_id=f'rule-engine-giulio-{time.time()}'
    )
    print("[SYSTEM] CONNECTED TO KAFKA.", flush=True)
    print("[SYSTEM] TELEMETRY ROUTER & PREFIX STRIPPER: ACTIVE", flush=True)

    for message in consumer:
        data = message.value
        s_id = data.get('sensor_id')
        val = data.get('value')
        
        # Filtro: processiamo solo se c'è un ID sensore valido e un valore
        if s_id and 'value' in data:
            
            # --- 1. CAPIAMO LA NATURA DEL DATO (PRIMA DI PULIRLO) ---
            # Se la stringa originale contiene "telemetry", è uno stream in tempo reale
            is_telemetry = "telemetry" in s_id
            
            # --- 2. PULIZIA DEL NOME (STRIP PREFIX) ---
            # Rimuove percorsi come "mars/telemetry/" e tiene solo l'ultimo pezzo
            if "/" in s_id:
                s_id = s_id.split("/")[-1]
                data['sensor_id'] = s_id  # Aggiorniamo il JSON con il nome pulito
            
            # --- 3. SMISTAMENTO (ROUTING COME DA CONSEGNA) ---
            if is_telemetry:
                # Dati Telemetria (es. solar_array) -> SOLO su WebSocket (Stream live)
                cache.publish("mars_telemetry_stream", json.dumps(data))
            else:
                # Dati Sensori REST (es. greenhouse_temperature) -> SOLO su Redis (Stato API)
                metric = data.get('metric', 'default')
                cache.set(f"sensor:{s_id}:{metric}", json.dumps(data))
            
            # Se il valore non è un numero, non possiamo fare confronti matematici
            if not isinstance(val, (int, float)):
                continue
            
            # --- 4. CONTROLLO REGOLE (AUTOMAZIONE) ---
            try:
                conn = get_db_connection()
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM automation_rules WHERE sensor_name = %s", (s_id,))
                    rules = cur.fetchall()
                    
                    for rule in rules:
                        op = rule['operator']
                        threshold = float(rule['threshold_value'])
                        
                        # Verifica condizione
                        triggered = False
                        if op == ">" and val > threshold: triggered = True
                        elif op == "<" and val < threshold: triggered = True
                        elif op == "==" and val == threshold: triggered = True
                        
                        if triggered:
                            print(f"\033[91m  [ALARM] \033[0m {s_id} ACTIVATE {rule['actuator_name']}! ({val} {op} {threshold}) ", flush=True)
                            trigger_actuator(rule['actuator_name'], rule['target_state'])
                conn.close()
            except Exception as e:
                print(f"ERROR DB: {e}", flush=True)

except Exception as e:
    print(f"[CRITICAL] Kafka connection failed: {e}", flush=True)