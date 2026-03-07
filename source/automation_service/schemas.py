from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SensorState(BaseModel):
    value: float
    unit: str
    timestamp: datetime

class RuleCreate(BaseModel):
    sensor_name: str
    operator: str
    threshold_value: float
    threshold_unit: str
    actuator_name: str
    target_state: str

class RuleResponse(RuleCreate):
    id: int
    created_at: datetime