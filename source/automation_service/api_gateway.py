from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import redis, json, uvicorn, asyncio
from persistence_layer import get_db_connection
import requests
from datetime import datetime  

app = FastAPI()

# Redis connection setup
cache = redis.Redis(host="mars_redis", port=6379, decode_responses=True)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# --- 1. CURRENT STATE (REST) US-05 + US-10 ---
@app.get("/api/state")
def get_current_state():
    keys = cache.keys("sensor:*")
    result = []

    for k in sorted(keys):
        raw = cache.get(k)
        if not raw:
            continue

        try:
            obj = json.loads(raw)
            if "series_id" in obj and "source_id" in obj:
                result.append(obj)
        except Exception:
            continue

    return result


# --- 2. LIVE TELEMETRY (WEBSOCKET) US-10 ---
@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    print("INFO: WebSocket connection established.")
    
    pubsub = cache.pubsub()
    pubsub.subscribe("mars_telemetry_stream")
    
    try:
        for message in pubsub.listen():
            if message['type'] == 'message':
                # Dispatching live data to the connected client
                await websocket.send_text(message['data'])
            await asyncio.sleep(0.01)
    except WebSocketDisconnect:
        print("INFO: WebSocket client disconnected.")
    except Exception as e:
        print(f"ERROR: Unexpected WebSocket error: {e}")
    finally:
        pubsub.unsubscribe("mars_telemetry_stream")
        print("INFO: Unsubscribed from Redis telemetry stream.")

# --- 3. AUTOMATION RULES (POSTGRES) ---
@app.get("/api/rules")
def get_rules():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM automation_rules")
    res = cur.fetchall()
    conn.close()
    return res  # è già una lista di dizionari grazie a RealDictCursor

@app.post("/api/rules")
def create_rule(rule: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO automation_rules (sensor_name, operator, threshold_value, threshold_unit, actuator_name, target_state)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING *;
        """, (rule['sensor_name'], rule['operator'], rule['threshold_value'], rule['threshold_unit'], rule['actuator_name'], rule['target_state']))
        res = cur.fetchone()
        conn.commit()
        
        cache.publish("rules_update", json.dumps({
            "action": "created", 
            "rule": dict(res)
        }))
        
        return dict(res)
    except Exception as e:
        conn.rollback()
        print(f"ERROR: Failed to create rule: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during rule creation.")
    finally:
        conn.close()


# ============================================================
# GET /api/actuators (mancante - US-11, US-13)
# ============================================================
@app.get("/api/actuators")
def get_actuators():
    try:
        # Proviamo a connetterci
        conn = get_db_connection()
        # Usiamo RealDictCursor per avere i nomi delle colonne
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM actuators ORDER BY name ASC")
            res = cur.fetchall()
        conn.close()
        
        # Usiamo il MarsEncoder per evitare crash sui tipi di dati
        return json.loads(json.dumps(res, cls=MarsEncoder))
        
    except Exception as e:
        # Questo log apparirà nel terminale di Docker
        print(f"DEBUG ERROR: {str(e)}", flush=True)
        # Questo lo vedrai nella risposta della curl
        raise HTTPException(status_code=500, detail=f"Errore Reale: {str(e)}")


        

# --- 4. ACTUATOR CONTROL (HTTP DISPATCH) Validazione + Redis publish in manual_control ---
@app.post("/api/actuators/{name}/dispatch")
def manual_control(name: str, command: dict):
    """
    US-12: Manual Actuator Control - con validazione e notifica realtime
    """
    state = command.get("state")
    
    # ← AGGIUNGO validazione input
    if state not in ["ON", "OFF"]:
        raise HTTPException(status_code=400, detail="State must be 'ON' or 'OFF'")
    
    try:
        response = requests.post(
            f"http://simulator:8080/api/actuators/{name}", 
            json={"state": state}, 
            timeout=2
        )
        response.raise_for_status()  # ← AGGIUNGO check HTTP status
        
        print(f"INFO: Command '{state}' dispatched to actuator '{name}'.")
        
        # ← AGGIUNGO notifica realtime su Redis per frontend
        cache.publish("actuator_update", json.dumps({
            "actuator": name,
            "state": state,
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        return {"status": "dispatched", "target": name, "state": state}
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Actuator dispatch failed for '{name}': {e}")
        raise HTTPException(status_code=502, detail="Failed to communicate with simulator.")


@app.delete("/api/rules/{rule_id}")
def delete_rule(rule_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM automation_rules WHERE id = %s RETURNING *;", (rule_id,))
        deleted_rule = cur.fetchone()
        
        if not deleted_rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        conn.commit()
        
        # ← AGGIUNGO notifica realtime
        cache.publish("rules_update", json.dumps({
            "action": "deleted", 
            "rule_id": rule_id
        }))
        
        return {"status": "deleted", "rule": deleted_rule}  # ✓ Non serve dict() con RealDictCursor
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete rule: {e}")
    finally:
        conn.close()

@app.patch("/api/rules/{rule_id}")
def update_rule(rule_id: int, rule: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM automation_rules WHERE id = %s;", (rule_id,))
        existing_rule = cur.fetchone()

        if not existing_rule:
            raise HTTPException(status_code=404, detail="Rule not found")

        updated_rule = {
            "sensor_name": rule.get("sensor_name", existing_rule["sensor_name"]),
            "operator": rule.get("operator", existing_rule["operator"]),
            "threshold_value": rule.get("threshold_value", existing_rule["threshold_value"]),
            "threshold_unit": rule.get("threshold_unit", existing_rule["threshold_unit"]),
            "actuator_name": rule.get("actuator_name", existing_rule["actuator_name"]),
            "target_state": rule.get("target_state", existing_rule["target_state"]),
        }

        cur.execute("""
            UPDATE automation_rules
            SET sensor_name = %s,
                operator = %s,
                threshold_value = %s,
                threshold_unit = %s,
                actuator_name = %s,
                target_state = %s
            WHERE id = %s
            RETURNING *;
        """, (
            updated_rule["sensor_name"],
            updated_rule["operator"],
            updated_rule["threshold_value"],
            updated_rule["threshold_unit"],
            updated_rule["actuator_name"],
            updated_rule["target_state"],
            rule_id
        ))

        res = cur.fetchone()
        conn.commit()
        
        # ← AGGIUNGO notifica realtime
        cache.publish("rules_update", json.dumps({
            "action": "updated", 
            "rule": dict(res)
        }))
        
        return res

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update rule: {e}")
    finally:
        conn.close()


# ============================================================
# WebSocket /ws/rules (US-07 tabella realtime)
# ============================================================
@app.websocket("/ws/rules")
async def websocket_rules(websocket: WebSocket):
    """
    WebSocket per aggiornamenti realtime tabella regole
    Frontend riceve notifiche su create/update/delete senza polling
    """
    await websocket.accept()
    print("INFO: WebSocket rules connection established.")
    
    pubsub = cache.pubsub()
    pubsub.subscribe("rules_update")
    
    try:
        for message in pubsub.listen():
            if message['type'] == 'message':
                await websocket.send_text(message['data'])
            await asyncio.sleep(0.01)
    except WebSocketDisconnect:
        print("INFO: WebSocket rules client disconnected.")
    except Exception as e:
        print(f"ERROR: Unexpected WebSocket error on rules channel: {e}")
    finally:
        pubsub.unsubscribe("rules_update")
        print("INFO: Unsubscribed from rules update stream.")

# ============================================================
#Health check endpoint
# ============================================================
@app.get("/health")
def health_check():
    """Verifica readiness del gateway per docker-compose healthcheck"""
    return {
        "status": "healthy",
        "service": "api_gateway",
        "redis": cache.ping(),
        "timestamp": datetime.utcnow().isoformat()
    }




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
