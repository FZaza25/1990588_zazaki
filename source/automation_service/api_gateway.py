from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import redis, json, uvicorn, asyncio
from persistence_layer import get_db_connection
import requests

app = FastAPI()

# Redis connection setup
cache = redis.Redis(host="mars_redis", port=6379, decode_responses=True)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# --- 1. CURRENT STATE (REST) ---
@app.get("/api/state")
def get_current_state():
    keys = cache.keys("sensor:*")
    return [json.loads(cache.get(k)) for k in sorted(keys) if cache.get(k)]

# --- 2. LIVE TELEMETRY (WEBSOCKET) ---
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
        return dict(res)
    except Exception as e:
        conn.rollback()
        print(f"ERROR: Failed to create rule: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during rule creation.")
    finally:
        conn.close()

# --- 4. ACTUATOR CONTROL (HTTP DISPATCH) ---
@app.post("/api/actuators/{name}/dispatch")
def manual_control(name: str, command: dict):
    state = command.get("state")
    try:
        # Forwarding command to the simulator service
        requests.post(f"http://simulator:8080/api/actuators/{name}", json={"state": state}, timeout=2)
        print(f"INFO: Command '{state}' dispatched to actuator '{name}'.")
        return {"status": "dispatched", "target": name, "state": state}
    except Exception as e:
        print(f"ERROR: Actuator dispatch failed for '{name}': {e}")
        raise HTTPException(status_code=500, detail="Failed to communicate with simulator.")

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
        return {"status": "deleted", "rule": deleted_rule}  # ✓ Non serve dict() con RealDictCursor
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete rule: {e}")
    finally:
        conn.close()



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)