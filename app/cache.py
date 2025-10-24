import time
from typing import Any
from threading import RLock
 
class TTLCache:
    def __init__(self, ttl_seconds: int = 60):
        self.ttl = ttl_seconds
        self.store: dict[str, tuple[float, Any]] = {}
        self._lock = RLock()

    def get(self, key: str):
        with self._lock:
            val = self.store.get(key)
            if not val:
                return None
            t, data = val
            if time.time() - t > self.ttl:
                self.store.pop(key, None)
                return None
            return data
 

    def set(self, key: str, value: Any):
        with self._lock:
            self.store[key] = (time.time(), value)
