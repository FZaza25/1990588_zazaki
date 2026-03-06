import os
import time
import json
import threading
import requests
import sseclient
from kafka import KafkaProducer

SIMULATOR_URL = os.environ.get("SIMULATOR_URL", "http://localhost:8080")
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = "mars.telemetry.normalized"

# Attendi che Kafka sia pronto
time.sleep(10) 
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def publish_event(sensor_id, timestamp, metric, value, unit):
    """Formatta l'evento nello Schema Unificato e lo pubblica su Kafka"""
    normalized_event = {
        "sensor_id": sensor_id,
        "timestamp": timestamp,
        "metric": metric,
        "value": value,
        "unit": unit
    }
    producer.send(KAFKA_TOPIC, normalized_event)
    print(f"[KAFKA] Pubblicato: {sensor_id} | {metric} = {value} {unit}")

def normalize_payload(schema_type, data):
    """Il Motore di Normalizzazione: mappa i contratti in eventi unificati"""
    try:
        timestamp = data.get("captured_at") or data.get("event_time") or time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        sensor_id = data.get("sensor_id") or data.get("topic") or "unknown"

        # --- REST SENSORS ---
        if schema_type == "rest.scalar.v1":
            publish_event(sensor_id, timestamp, data["metric"], data["value"], data["unit"])
            
        elif schema_type == "rest.chemistry.v1":
            for meas in data.get("measurements", []):
                publish_event(sensor_id, timestamp, meas["metric"], meas["value"], meas["unit"])
                
        elif schema_type == "rest.particulate.v1":
            publish_event(sensor_id, timestamp, "pm1", data["pm1_ug_m3"], "ug/m3")
            publish_event(sensor_id, timestamp, "pm2.5", data["pm25_ug_m3"], "ug/m3")
            publish_event(sensor_id, timestamp, "pm10", data["pm10_ug_m3"], "ug/m3")
            
        elif schema_type == "rest.level.v1":
            publish_event(sensor_id, timestamp, "level_pct", data["level_pct"], "%")
            publish_event(sensor_id, timestamp, "level_liters", data["level_liters"], "L")

        # --- TELEMETRY TOPICS ---
        elif schema_type == "topic.power.v1":
            publish_event(sensor_id, timestamp, "power", data["power_kw"], "kW")
            publish_event(sensor_id, timestamp, "voltage", data["voltage_v"], "V")
            publish_event(sensor_id, timestamp, "current", data["current_a"], "A")
            
        elif schema_type == "topic.environment.v1":
            for meas in data.get("measurements", []):
                publish_event(sensor_id, timestamp, meas["metric"], meas["value"], meas["unit"])
                
        elif schema_type == "topic.thermal_loop.v1":
            publish_event(sensor_id, timestamp, "temperature", data["temperature_c"], "C")
            publish_event(sensor_id, timestamp, "flow", data["flow_l_min"], "L/min")
            
        elif schema_type == "topic.airlock.v1":
            publish_event(sensor_id, timestamp, "cycles", data["cycles_per_hour"], "cycles/h")

    except Exception as e:
        print(f"[ERROR] Normalizzazione fallita per {schema_type}: {e}")

def poll_sensor(sensor_name, schema_type):
    """Effettua il polling REST ogni 5 secondi"""
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
    """Consuma i Server-Sent Events (SSE) della telemetria"""
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
    
    # Lista dei sensori REST da interrogare (Polling)
    rest_sensors = [
        ("greenhouse_temperature", "rest.scalar.v1"),
        ("entrance_humidity", "rest.scalar.v1"),
        ("hydroponic_ph", "rest.chemistry.v1"),
        ("air_quality_pm25", "rest.particulate.v1"),
        ("water_tank_level", "rest.level.v1")
    ]
    
    # Lista dei topic di Telemetria da ascoltare (SSE)
    telemetry_topics = [
        ("mars/telemetry/solar_array", "topic.power.v1"),
        ("mars/telemetry/radiation", "topic.environment.v1"),
        ("mars/telemetry/thermal_loop", "topic.thermal_loop.v1"),
        ("mars/telemetry/airlock", "topic.airlock.v1")
    ]

    # Avvio di un thread per ogni sensore/flusso
    for name, schema in rest_sensors:
        threading.Thread(target=poll_sensor, args=(name, schema), daemon=True).start()
        
    for topic, schema in telemetry_topics:
        threading.Thread(target=consume_stream, args=(topic, schema), daemon=True).start()

    # Mantiene il processo attivo
    while True:
        time.sleep(1)
