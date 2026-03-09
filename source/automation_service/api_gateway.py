from fastapi import FastAPI, HTTPException, WebSocket, Body
from fastapi.middleware.cors import CORSMiddleware
import redis, json, uvicorn, asyncio, requests
from persistence_layer import get_db_connection
from datetime import datetime
from decimal import Decimal

app = FastAPI(title="Mars Habitat API Gateway - Final")

# 1. FIX SERIALIZZAZIONE: Gestisce Decimal (Postgres) e Datetime nel JSON
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

# Helper per inviare dati a Redis Pub/Sub in modo sicuro
def safe_publish(channel, data):
    cache.publish(channel, json.dumps(data, cls=MarsEncoder))

# --- 1. STATO ATTUALE (REST) ---
@app.get("/api/state")
def get_current_state():
    """Recupera l'ultimo stato noto dei sensori ambientali da Redis"""
    keys = cache.keys("sensor:*")
    result = []
    for k in sorted(keys):
        raw = cache.get(k)
        if raw:
            try: result.append(json.loads(raw))
            except: continue
    return result

# --- 2. GESTIONE REGOLE (CRUD COMPLETO) ---

@app.get("/api/rules")
def get_all_rules():
    """Ottiene tutte le regole di automazione dal DB"""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM automation_rules ORDER BY id ASC")
        res = cur.fetchall()
    conn.close()
    return res

@app.post("/api/rules")
def create_rule(rule: dict):
    """Crea una nuova regola"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO automation_rules (sensor_name, operator, threshold_value, actuator_name, target_state)
                VALUES (%s, %s, %s, %s, %s) RETURNING *;
            """, (rule['sensor_name'], rule['operator'], rule['threshold_value'], rule['actuator_name'], rule['target_state']))
            res = cur.fetchone()
            conn.commit()
            safe_publish("rules_update", {"action": "create", "data": res})
            return res
    finally:
        conn.close()

@app.patch("/api/rules/{rule_id}")
def patch_rule(rule_id: int, updates: dict):
    """Modifica parziale di una regola (es. solo la soglia)"""
    if not updates: raise HTTPException(status_code=400, detail="Dati mancanti")
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Query dinamica basata sui campi inviati
            fields = [f"{k} = %s" for k in updates.keys()]
            values = list(updates.values())
            values.append(rule_id)
            query = f"UPDATE automation_rules SET {', '.join(fields)} WHERE id = %s RETURNING *;"
            cur.execute(query, tuple(values))
            res = cur.fetchone()
            if not res: raise HTTPException(status_code=404, detail="Regola non trovata")
            conn.commit()
            safe_publish("rules_update", {"action": "update", "data": res})
            return res
    finally:
        conn.close()

@app.delete("/api/rules/{rule_id}")
def delete_rule(rule_id: int):
    """Cancella una regola"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM automation_rules WHERE id = %s RETURNING id;", (rule_id,))
            if not cur.fetchone(): raise HTTPException(status_code=404, detail="Regola non trovata")
            conn.commit()
            safe_publish("rules_update", {"action": "delete", "rule_id": rule_id})
            return {"status": "deleted", "id": rule_id}
    finally:
        conn.close()

# --- 3. GESTIONE ATTUATORI (US-12/13) ---

@app.get("/api/actuators")
def get_actuators():
    """Ritorna la lista attuatori, stato e modalità (AUTO/MANUAL)"""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM actuators ORDER BY name ASC")
        res = cur.fetchall()
    conn.close()
    return res

@app.patch("/api/actuators/{name}/mode")
def patch_actuator_mode(name: str, payload: dict):
    """Cambia la modalità operativa (AUTO/MANUAL)"""
    new_mode = payload.get("mode")
    if new_mode not in ["AUTO", "MANUAL"]:
        raise HTTPException(status_code=400, detail="Modalità non valida")
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE actuators SET mode = %s, last_update = CURRENT_TIMESTAMP WHERE name = %s RETURNING *;", (new_mode, name))
            res = cur.fetchone()
            if not res: raise HTTPException(status_code=404, detail="Attuatore non trovato")
            conn.commit()
            safe_publish("actuator_updates", res)
            return res
    finally:
        conn.close()

# --- 4. TELEMETRY STREAM (WEBSOCKET) ---
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

# --- 5. SYSTEM HEALTH ---
@app.get("/health")
def health_check():
    return {"status": "healthy", "redis": cache.ping(), "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)