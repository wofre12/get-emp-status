import time
from typing import Any

class TTLCache:
    def __init__(self, ttl_seconds: int = 60):
        self.ttl = ttl_seconds
        self.store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str):
        val = self.store.get(key)
        if not val:
            return None
        t, data = val
        if time.time() - t > self.ttl:
            self.store.pop(key, None)
            return None
        return data

    def set(self, key: str, value: Any):
        self.store[key] = (time.time(), value)
