from pathlib import Path
from sqlalchemy import text
from .data_access import DataAccess
from .models import Base

SEED_SQL_PATH = Path(__file__).resolve().parent.parent / "db" / "seed.sql"

def init_database(da: DataAccess) -> None:
    # Create schema
    Base.metadata.create_all(da.engine)
    # Seed strictly from db/seed.sql (no fallback)
    sql = SEED_SQL_PATH.read_text(encoding="utf-8")
    if not sql.strip():
        return
    # Execute each statement 
    with da.engine.begin() as conn:
        # Enable FKs for SQLite
        if da.engine.url.get_backend_name() == "sqlite":
            conn.exec_driver_sql("PRAGMA foreign_keys=ON")
        # Split on semicolons; ignore blanks
        for stmt in filter(None, (seg.strip() for seg in sql.split(";"))):
            conn.execute(text(stmt))
