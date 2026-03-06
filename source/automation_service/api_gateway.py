from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from schemas import SensorState, RuleCreate, RuleResponse
from persistence_layer import get_db_connection
from state_cache import sensor_memory

app = FastAPI(title="Mars Automation Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/state")
def get_current_state():
    return sensor_memory


@app.get("/api/rules", response_model=List[RuleResponse])
def get_automation_rules():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM automation_rules ORDER BY created_at DESC")
        rules = cursor.fetchall()
        return [dict(rule) for rule in rules]
    finally:
        conn.close()

@app.post("/api/rules", response_model=RuleResponse)
def create_rule(rule: RuleCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO automation_rules 
            (sensor_name, operator, threshold_value, threshold_unit, actuator_name, target_state)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *;
        """, (
            rule.sensor_name, rule.operator, rule.threshold_value, 
            rule.threshold_unit, rule.actuator_name, rule.target_state
        ))
        new_rule = cursor.fetchone()
        conn.commit()
        return dict(new_rule)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
