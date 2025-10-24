from .models import Log
import json

class DBLogger:
    def __init__(self, session_factory, enabled: bool = True):
        self.session_factory = session_factory
        self.enabled = enabled

    def log(self, level: str, message: str, context: dict | None = None):
        if not self.enabled:
            return
        with self.session_factory() as session:
            rec = Log(
                level=level.upper()[:10],
                message=message[:255],
                context_json=json.dumps(context) if context else None
            )
            session.add(rec)
            session.commit()
