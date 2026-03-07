from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import redis, json, uvicorn
from persistence_layer import get_db_connection
import requests

app = FastAPI()
cache = redis.Redis(host="mars_redis", port=6379, decode_responses=True)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/api/state")
def get_current_state():
    keys = cache.keys("sensor:*")
    return [json.loads(cache.get(k)) for k in keys if cache.get(k)]

# Accetta sia /api/rules che /api/rules/
@app.get("/api/rules")
@app.get("/api/rules/")
def get_rules():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM automation_rules")
    res = cur.fetchall()
    conn.close()
    return [dict(r) for r in res]

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
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/api/actuators/{name}/dispatch")
def manual_control(name: str, command: dict):
    """US-10: Allows the operator to manually override actuator state from dashboard"""
    state = command.get("state") # Expects {"state": "ON"} or {"state": "OFF"}
    try:
        # Forwards the command directly to the simulator
        res = requests.post(f"http://simulator:8080/api/actuators/{name}", json={"state": state}, timeout=2)
        if res.status_code == 200:
            return {"status": "dispatched", "target": name, "state": state}
        else:
            raise HTTPException(status_code=res.status_code, detail="Simulator rejected the command")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not reach simulator: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)