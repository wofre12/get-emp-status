import os
import pathlib
import time
import pytest
from fastapi.testclient import TestClient

TEST_DB = pathlib.Path("test.db")

@pytest.fixture(scope="session")
def test_client():
    os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
    os.environ["API_TOKEN"] = "secret123"

    from app.main import app
    from app.bootstrap import init_database
    from app.data_access import DataAccess

    # Fresh start
    if TEST_DB.exists():
        # dispose any old engine holding a lock
        try:
            DataAccess(os.environ["DATABASE_URL"]).engine.dispose()
        except Exception:
            pass
        try:
            TEST_DB.unlink()
        except Exception:
            pass

    da = DataAccess(os.environ["DATABASE_URL"])
    init_database(da)

    with TestClient(app) as c:
        yield c

    # ---- TEARDOWN ----
    # 1) dispose engine to release SQLite file lock
    try:
        DataAccess(os.environ["DATABASE_URL"]).engine.dispose()
    except Exception:
        pass

    # 2) remove the file with a short retry (Windows)
    for _ in range(5):
        try:
            if TEST_DB.exists():
                TEST_DB.unlink()
            break
        except PermissionError:
            time.sleep(0.2)
