from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import redis, json, uvicorn, asyncio, requests
from persistence_layer import get_db_connection
from datetime import datetime
from decimal import Decimal

app = FastAPI(title="Mars Habitat API Gateway - Final Merged")

# FIX: Encoder per gestire Decimal e Datetime
class MarsEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal): return float(obj)
        if isinstance(obj, datetime): return obj.isoformat()
        return super().default(obj)

cache = redis.Redis(host="mars_redis", port=6379, decode_responses=True)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

@app.get("/api/state")
def get_current_state():
    keys = cache.keys("sensor:*")
    result = []
    for k in sorted(keys):
        raw = cache.get(k)
        if raw:
            try: result.append(json.loads(raw))
            except: continue
    return result

# --- GESTIONE REGOLE ---
@app.get("/api/rules")
def get_all_rules():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM automation_rules ORDER BY id ASC")
        res = cur.fetchall()
    conn.close()
    return res

@app.post("/api/rules")
def create_rule(rule: dict):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO automation_rules (sensor_name, operator, threshold_value, actuator_name, target_state)
                VALUES (%s, %s, %s, %s, %s) RETURNING *;
            """, (rule['sensor_name'], rule['operator'], rule['threshold_value'], rule['actuator_name'], rule['target_state']))
            res = cur.fetchone()
            conn.commit()
            cache.publish("rules_update", json.dumps({"action": "create", "data": res}, cls=MarsEncoder))
            return res
    finally: conn.close()

# --- GESTIONE ATTUATORI (CON MODALITA' AUTO/MANUAL) ---
@app.get("/api/actuators")
def get_actuators():
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM actuators ORDER BY name ASC")
            res = cur.fetchall()
        conn.close()
        # Restituiamo il JSON usando l'encoder per i Decimali
        return json.loads(json.dumps(res, cls=MarsEncoder))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore DB: {str(e)}")

@app.patch("/api/actuators/{name}/mode")
def patch_actuator_mode(name: str, payload: dict):
    new_mode = payload.get("mode")
    if new_mode not in ["AUTO", "MANUAL"]:
        raise HTTPException(status_code=400, detail="Usa 'AUTO' o 'MANUAL'")
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE actuators SET mode=%s, last_update=CURRENT_TIMESTAMP WHERE name=%s RETURNING *", (new_mode, name))
            res = cur.fetchone()
            conn.commit()
            if not res: raise HTTPException(status_code=404, detail="Non trovato")
            cache.publish("actuator_updates", json.dumps(res, cls=MarsEncoder))
            return res
    finally: conn.close()

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    pubsub = cache.pubsub()
    pubsub.subscribe("mars_telemetry_stream")
    try:
        for m in pubsub.listen():
            if m['type'] == 'message': await websocket.send_text(m['data'])
            await asyncio.sleep(0.01)
    except: pass
    finally: pubsub.unsubscribe()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)