import json
import redis
from kafka import KafkaConsumer
from persistence_layer import get_db_connection

# --- CONFIGURAZIONE ---
KAFKA_BROKER = "localhost:29092"
TOPIC = "mars.telemetry.normalized" # <--- CAMBIATO QUI
REDIS_HOST = "localhost"

# --- CONNESSIONI ---
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=[KAFKA_BROKER],
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='latest' # Legge solo i nuovi messaggi da ora in poi
)
cache = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

print(f"🧠 Rule Engine attivo su {TOPIC}...")

for message in consumer:
    data = message.value
    sensor_name = data.get("sensor_id")
    value = data.get("value")
    
    # 1. Salva su Redis (per Andrea e il frontend)
    # Salviamo tutto il JSON così abbiamo anche timestamp e unità
    cache.set(f"sensor:{sensor_name}", json.dumps(data))
    print(f"📡 Ricevuto: {sensor_name} = {value}")

    # 2. Controllo Regole in Postgres
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM automation_rules WHERE sensor_name = %s", (sensor_name,))
    rules = cur.fetchall()
    
    for rule in rules:
        triggered = False
        # Logica di confronto
        if rule['operator'] == '<' and value < float(rule['threshold_value']):
            triggered = True
        elif rule['operator'] == '>' and value > float(rule['threshold_value']):
            triggered = True
            
        if triggered:
            print(f"⚠️  ALLARME: {sensor_name} è {value}! ATTIVO {rule['actuator_name']} -> {rule['target_state']}")
            
    cur.close()
    conn.close()