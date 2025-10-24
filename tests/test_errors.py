import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
from app.main import init_db, app
from fastapi.testclient import TestClient

init_db()
client = TestClient(app)

def test_not_found():
    r = client.post("/api/GetEmpStatus", json={"NationalNumber":"NOPE999"})
    assert r.status_code == 404

def test_inactive():
    r = client.post("/api/GetEmpStatus", json={"NationalNumber":"NAT1003"})
    assert r.status_code == 406

def test_insufficient():
    r = client.post("/api/GetEmpStatus", json={"NationalNumber":"NAT2001"})
    assert r.status_code == 422
