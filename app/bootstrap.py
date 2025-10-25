from pathlib import Path
from sqlalchemy import text
from .data_access import DataAccess
from .models import Base

SEED_SQL_PATH = Path(__file__).resolve().parent.parent / "db" / "seed.sql"

def init_database(data_access):
    Base.metadata.create_all(data_access.engine)

    seed_sql = Path("db/seed.sql")
    if not seed_sql.exists():
        return

    with data_access.engine.begin() as conn:
        # if users already present, skip seeding to avoid unique conflicts
        try:
            count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar() or 0
        except Exception:
            count = 0
        if count > 0:
            return

        stmts = seed_sql.read_text(encoding="utf-8")
        for stmt in filter(None, (s.strip() for s in stmts.split(";"))):
            conn.execute(text(stmt))
