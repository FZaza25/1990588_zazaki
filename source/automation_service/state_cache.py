import redis
import json
import os

REDIS_HOST = os.getenv("REDIS_HOST", "state_store")
_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

def get_all_states():
    keys = _client.keys("sensor:*")
    states = {}
    for k in keys:
        sensor_id = k.split(":")[1]
        try:
            states[sensor_id] = json.loads(_client.get(k))
        except:
            continue
    return states

# Creiamo un proxy per far sì che il tuo 'import sensor_memory' funzioni come previsto
class SensorMemoryProxy:
    def __iter__(self): return iter(get_all_states().items())
    def __dict__(self): return get_all_states()
    def __repr__(self): return str(get_all_states())
    # FastAPI userà questo per la risposta JSON
    def items(self): return get_all_states().items()

sensor_memory = get_all_states() # Per ora lo passiamo come funzione o dizionario dinamico