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

#Funzione ausiliara per semplificare l'utilizzo dei vari dati nel front end
def short_source_id(source_id: str) -> str:
    if source_id.startswith("mars/telemetry/"):
        return source_id.replace("mars/telemetry/", "")
    return source_id


# Spara il json pulito dentro Kafka 
def publish_event(source_id, timestamp, metric, value, unit, event_type, status="ok", **tags):
    if isinstance(value, (int, float)):
        value = round(value, 2)

    short_id = short_source_id(source_id)

    normalized_event = {
        "source_id": source_id,                    # id originale completo
        "series_id": f"{short_id}:{metric}",       
        "metric": metric,
        "timestamp": timestamp,
        "value": value,
        "unit": unit,
        "type": event_type,
        "status": status
    }

    if tags:
        normalized_event["tags"] = tags

    producer.send(KAFKA_TOPIC, normalized_event)
    producer.flush()

    print(
        f"[KAFKA] source={source_id} | series={normalized_event['series_id']} | "
        f"{value} {unit} | type={event_type} | status={status}",
        flush=True
    )
    

def normalize_payload(schema_type, data):
    try:
        timestamp = (
            data.get("captured_at")
            or data.get("event_time")
            or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        )

        source_id = data.get("sensor_id") or data.get("topic") or "unknown"
        status = data.get("status", "ok")

        # REST scalar
        if schema_type == "rest.scalar.v1":
            publish_event(
                source_id=source_id,
                timestamp=timestamp,
                metric=data["metric"],
                value=data["value"],
                unit=data["unit"],
                event_type=schema_type,
                status=status
            )

        # REST chemistry
        elif schema_type == "rest.chemistry.v1":
            for meas in data.get("measurements", []):
                publish_event(
                    source_id=source_id,
                    timestamp=timestamp,
                    metric=meas["metric"],
                    value=meas["value"],
                    unit=meas["unit"],
                    event_type=schema_type,
                    status=status
                )

        # REST particulate
        elif schema_type == "rest.particulate.v1":
            publish_event(source_id, timestamp, "pm1", data["pm1_ug_m3"], "ug/m3", schema_type, status)
            publish_event(source_id, timestamp, "pm2.5", data["pm25_ug_m3"], "ug/m3", schema_type, status)
            publish_event(source_id, timestamp, "pm10", data["pm10_ug_m3"], "ug/m3", schema_type, status)

        # REST level
        elif schema_type == "rest.level.v1":
            publish_event(source_id, timestamp, "level_pct", data["level_pct"], "%", schema_type, status)
            publish_event(source_id, timestamp, "level_liters", data["level_liters"], "L", schema_type, status)

        # TOPIC power
        elif schema_type == "topic.power.v1":
            sub = data.get("subsystem", "unknown")
            publish_event(source_id, timestamp, "power", data["power_kw"], "kW", schema_type, status, subsystem=sub)
            publish_event(source_id, timestamp, "voltage", data["voltage_v"], "V", schema_type, status, subsystem=sub)
            publish_event(source_id, timestamp, "current", data["current_a"], "A", schema_type, status, subsystem=sub)
            publish_event(source_id, timestamp, "cumulative_energy", data["cumulative_kwh"], "kWh", schema_type, status, subsystem=sub)

        # TOPIC environment
        elif schema_type == "topic.environment.v1":
            source_info = data.get("source", {})
            for meas in data.get("measurements", []):
                publish_event(
                    source_id=source_id,
                    timestamp=timestamp,
                    metric=meas["metric"],
                    value=meas["value"],
                    unit=meas["unit"],
                    event_type=schema_type,
                    status=status,
                    system=source_info.get("system"),
                    segment=source_info.get("segment")
                )

        # TOPIC thermal loop
        elif schema_type == "topic.thermal_loop.v1":
            loop_id = data.get("loop", "unknown")
            publish_event(source_id, timestamp, "temperature", data["temperature_c"], "C", schema_type, status, loop=loop_id)
            publish_event(source_id, timestamp, "flow", data["flow_l_min"], "L/min", schema_type, status, loop=loop_id)

        # TOPIC airlock
        elif schema_type == "topic.airlock.v1":
            airlock_id = data.get("airlock_id", "unknown")
            publish_event(source_id, timestamp, "cycles", data["cycles_per_hour"], "cycles/h", schema_type, status, airlock_id=airlock_id)
            publish_event(source_id, timestamp, "state", data["last_state"], "enum", schema_type, status, airlock_id=airlock_id)

        else:
            print(f"[WARN] Unsupported schema_type={schema_type} data={data}", flush=True)

    except Exception as e:
        print(f"[ERROR] Normalizzazione fallita per {schema_type}: {e} | Dati: {data}", flush=True)

def poll_sensor(sensor_name, schema_type):
    """Effettua il polling REST ogni 5 secondi invia richiesta get al simulatore per lo stato del sensore"""
    url = f"{SIMULATOR_URL}/api/sensors/{sensor_name}"
    while True:
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                normalize_payload(schema_type, res.json())
            else:
                print(f"[REST ERROR] {sensor_name}: status={res.status_code}", flush=True)
        except Exception as e:
            print(f"[REST ERROR] {sensor_name}: {e}", flush=True)
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
            print(f"[STREAM ERROR] {topic_name}: disconnesso. Riconnessione... ({e})", flush=True)
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
        ("water_tank_level", "rest.level.v1"),
    ]
    
    # Lista dei topic di Telemetria da ascoltare (SSE) - AGGIORNATA CON TUTTI I TOPIC
    telemetry_topics = [
        ("mars/telemetry/solar_array", "topic.power.v1"),
        ("mars/telemetry/power_bus", "topic.power.v1"),
        ("mars/telemetry/power_consumption", "topic.power.v1"),
        ("mars/telemetry/radiation", "topic.environment.v1"),
        ("mars/telemetry/life_support", "topic.environment.v1"),
        ("mars/telemetry/thermal_loop", "topic.thermal_loop.v1"),
        ("mars/telemetry/airlock", "topic.airlock.v1"),
    ]

    # (il demone) Avvio di un thread per ogni sensore/flusso
    for name, schema in rest_sensors:
        threading.Thread(target=poll_sensor, args=(name, schema), daemon=True).start()

    for topic, schema in telemetry_topics:
        threading.Thread(target=consume_stream, args=(topic, schema), daemon=True).start()

    # Mantiene il processo attivo
    while True:
        time.sleep(1)
