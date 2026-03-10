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


@app.patch("/api/actuators/{name}/status")
def patch_actuator_status(name: str, payload: dict):
    new_status = payload.get("status")
    if new_status not in ["ON", "OFF"]:
        raise HTTPException(status_code=400, detail="Usa 'ON' o 'OFF'")
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 1. Aggiorna lo stato nel DB Postgres
            cur.execute("""
                UPDATE actuators 
                SET status = %s, last_update = CURRENT_TIMESTAMP 
                WHERE name = %s RETURNING *
            """, (new_status, name))
            res = cur.fetchone()
            conn.commit()
            
            if not res:
                raise HTTPException(status_code=404, detail="Attuatore non trovato")
            
            # 2. Invia il comando al simulatore (Host: simulator)
            try:
                print(f"DEBUG: Invio comando a simulator: {name} -> {new_status}", flush=True)
                sim_url = f"http://simulator:8080/api/actuators/{name}"
                r = requests.post(sim_url, json={"status": new_status}, timeout=2)
                print(f"DEBUG: Risposta simulator: {r.status_code}", flush=True)
            except Exception as e:
                print(f"CRITICAL: Errore simulatore: {e}", flush=True)

            # 3. Notifica via Redis
            cache.publish("actuator_updates", json.dumps(res, cls=MarsEncoder))
            return res
    finally:
        conn.close()

@app.delete("/api/rules/{rule_id}")
def delete_rule(rule_id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM automation_rules WHERE id = %s RETURNING *;", (rule_id,))
            res = cur.fetchone()
            conn.commit()
            if not res:
                raise HTTPException(status_code=404, detail="Regola non trovata")
            
            # Notifica il frontend e il rule_engine della cancellazione
            cache.publish("rules_update", json.dumps({"action": "delete", "id": rule_id}))
            return {"message": "Regola eliminata", "rule": res}
    finally:
        conn.close()


@app.patch("/api/rules/{rule_id}")
def update_rule(rule_id: int, payload: dict):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Costruiamo la query dinamicamente in base a cosa invia Andrea
            fields = [f"{k} = %s" for k in payload.keys()]
            values = list(payload.values())
            values.append(rule_id)
            
            query = f"UPDATE automation_rules SET {', '.join(fields)} WHERE id = %s RETURNING *;"
            cur.execute(query, values)
            res = cur.fetchone()
            conn.commit()
            
            if not res:
                raise HTTPException(status_code=404, detail="Regola non trovata")
            
            # Notifica il cambiamento
            cache.publish("rules_update", json.dumps({"action": "update", "data": res}, cls=MarsEncoder))
            return res
    finally:
        conn.close()

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