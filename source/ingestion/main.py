import os
import time
import json
import threading
import requests
import sseclient
from kafka import KafkaProducer

# Leggo le variabili d'ambiente passate dal docker-compose.yml
SIMULATOR_URL = os.environ.get("SIMULATOR_URL", "http://localhost:8080")    
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = "mars.telemetry.normalized"

# Attendi che Kafka sia pronto
time.sleep(10) 

# Il producer è l'entità che ha il permesso di "scrivere" messaggi sul broker.
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8') # lambda serve a convertire automaticamente i dizionari Python in stringhe JSON prima di inviarli
)

# Spara il json pulito dentro Kafka 
def publish_event(sensor_id, timestamp, metric, value, unit, status="ok", **extra_data):
    """Formatta l'evento nello Schema Unificato e lo pubblica su Kafka"""
    
    # Arrotonda solo i valori numerici
    if isinstance(value, (int, float)):
        value = round(value, 2)
    
    normalized_event = {
        "sensor_id": sensor_id,
        "timestamp": timestamp,
        "metric": metric,
        "value": value,
        "unit": unit,
        "status": status 
    }
    
    # Se ci sono dati extra (come subsystem o airlock_id), li uniamo al JSON
    if extra_data:
        normalized_event.update(extra_data)

    producer.send(KAFKA_TOPIC, normalized_event)
    print(f"[KAFKA] {sensor_id} | {metric} = {value} {unit} | Stato: {status}")
    

def normalize_payload(schema_type, data):
    """Il Motore di Normalizzazione: mappa i contratti in eventi unificati"""
    try:
        timestamp = data.get("captured_at") or data.get("event_time") or time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        sensor_id = data.get("sensor_id") or data.get("topic") or "unknown"
        status = data.get("status", "ok") # Peschiamo lo status, default "ok"

        # --- REST SENSORS ---
        if schema_type == "rest.scalar.v1":
            publish_event(sensor_id, timestamp, data["metric"], data["value"], data["unit"], status)
            
        elif schema_type == "rest.chemistry.v1":
            for meas in data.get("measurements", []):
                publish_event(sensor_id, timestamp, meas["metric"], meas["value"], meas["unit"], status)
                
        elif schema_type == "rest.particulate.v1":
            publish_event(sensor_id, timestamp, "pm1", data["pm1_ug_m3"], "ug/m3", status)
            publish_event(sensor_id, timestamp, "pm2.5", data["pm25_ug_m3"], "ug/m3", status)
            publish_event(sensor_id, timestamp, "pm10", data["pm10_ug_m3"], "ug/m3", status)
            
        elif schema_type == "rest.level.v1":
            publish_event(sensor_id, timestamp, "level_pct", data["level_pct"], "%", status)
            publish_event(sensor_id, timestamp, "level_liters", data["level_liters"], "L", status)

        # --- TELEMETRY TOPICS ---
        elif schema_type == "topic.power.v1":
            sub = data.get("subsystem", "unknown")
            publish_event(sensor_id, timestamp, "power", data["power_kw"], "kW", status, subsystem=sub)
            publish_event(sensor_id, timestamp, "voltage", data["voltage_v"], "V", status, subsystem=sub)
            publish_event(sensor_id, timestamp, "current", data["current_a"], "A", status, subsystem=sub)
            # Aggiunto cumulative_kwh mancante!
            if "cumulative_kwh" in data:
                publish_event(sensor_id, timestamp, "cumulative_energy", data["cumulative_kwh"], "kWh", status, subsystem=sub)
            
        elif schema_type == "topic.environment.v1":
            source_info = data.get("source", {})
            for meas in data.get("measurements", []):
                publish_event(sensor_id, timestamp, meas["metric"], meas["value"], meas["unit"], status, source=source_info)
                
        elif schema_type == "topic.thermal_loop.v1":
            loop_id = data.get("loop", "unknown")
            publish_event(sensor_id, timestamp, "temperature", data["temperature_c"], "C", status, loop=loop_id)
            publish_event(sensor_id, timestamp, "flow", data["flow_l_min"], "L/min", status, loop=loop_id)
            
        elif schema_type == "topic.airlock.v1":
            a_id = data.get("airlock_id", "unknown")
            publish_event(sensor_id, timestamp, "cycles", data["cycles_per_hour"], "cycles/h", status, airlock_id=a_id)
            # Aggiunto last_state mancante! Lo salviamo come valore stringa.
            publish_event(sensor_id, timestamp, "state", data["last_state"], "enum", status, airlock_id=a_id)

    except Exception as e:
        print(f"[ERROR] Normalizzazione fallita per {schema_type}: {e} | Dati: {data}")

def poll_sensor(sensor_name, schema_type):
    """Effettua il polling REST ogni 5 secondi invia richiesta get al simulatore per lo stato del sensore"""
    url = f"{SIMULATOR_URL}/api/sensors/{sensor_name}"
    while True:
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                normalize_payload(schema_type, res.json())
        except Exception as e:
            print(f"[REST ERROR] {sensor_name}: {e}")
        time.sleep(5)

def consume_stream(topic_name, schema_type):
    """Consuma i Server-Sent Events (SSE) della telemetria, mantiene la connessione aperta e resta in ascolto"""
    url = f"{SIMULATOR_URL}/api/telemetry/stream/{topic_name}"
    while True:
        try:
            res = requests.get(url, stream=True, timeout=10)
            client = sseclient.SSEClient(res)
            for event in client.events():
                normalize_payload(schema_type, json.loads(event.data))
        except Exception as e:
            print(f"[STREAM ERROR] {topic_name}: disconnesso. Riconnessione... ({e})")
            time.sleep(5)

if __name__ == "__main__":
    print("Avvio Ingestion Service per Marte...")
    
    # Lista dei sensori REST da interrogare (Polling) - AGGIORNATA CON TUTTI I SENSORI
    rest_sensors = [
        ("greenhouse_temperature", "rest.scalar.v1"),
        ("entrance_humidity", "rest.scalar.v1"),
        ("co2_hall", "rest.scalar.v1"),                
        ("corridor_pressure", "rest.scalar.v1"),      
        ("hydroponic_ph", "rest.chemistry.v1"),
        ("air_quality_voc", "rest.chemistry.v1"),     
        ("air_quality_pm25", "rest.particulate.v1"),
        ("water_tank_level", "rest.level.v1")
    ]
    
    # Lista dei topic di Telemetria da ascoltare (SSE) - AGGIORNATA CON TUTTI I TOPIC
    telemetry_topics = [
        ("mars/telemetry/solar_array", "topic.power.v1"),
        ("mars/telemetry/power_bus", "topic.power.v1"),                 
        ("mars/telemetry/power_consumption", "topic.power.v1"),        
        ("mars/telemetry/radiation", "topic.environment.v1"),
        ("mars/telemetry/life_support", "topic.environment.v1"),       
        ("mars/telemetry/thermal_loop", "topic.thermal_loop.v1"),
        ("mars/telemetry/airlock", "topic.airlock.v1")
    ]

    # (il demone) Avvio di un thread per ogni sensore/flusso
    for name, schema in rest_sensors:
        threading.Thread(target=poll_sensor, args=(name, schema), daemon=True).start()
        
    for topic, schema in telemetry_topics:
        threading.Thread(target=consume_stream, args=(topic, schema), daemon=True).start()

    # Mantiene il processo attivo
    while True:
        time.sleep(1)
