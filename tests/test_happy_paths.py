import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
from app.main import init_db, app
from fastapi.testclient import TestClient

init_db()
client = TestClient(app)

def test_happy_nat1001():
    r = client.post("/api/GetEmpStatus", json={"NationalNumber":"NAT1001"})
    assert r.status_code == 200
    body = r.json()
    assert body["user"]["nationalNumber"] == "NAT1001"
    assert body["metrics"]["count"] >= 3
    assert body["status"] in ("RED","ORANGE","GREEN")
