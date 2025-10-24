def test_health(test_client):
    r = test_client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"ok": True}

def test_happy_nat1001(test_client):
    r = test_client.post("/api/GetEmpStatus", json={"NationalNumber": "NAT1001"})
    assert r.status_code == 200
    body = r.json()
    assert body["user"]["nationalNumber"] == "NAT1001"
    assert body["metrics"]["count"] >= 3
    assert body["status"] in ("RED", "ORANGE", "GREEN")

def test_not_found(test_client):
    r = test_client.post("/api/GetEmpStatus", json={"NationalNumber": "NOPE999"})
    assert r.status_code == 404

def test_inactive(test_client):
    r = test_client.post("/api/GetEmpStatus", json={"NationalNumber": "NAT1003"})
    assert r.status_code == 406

def test_insufficient_data(test_client):
    # from your seed: NAT1012 is active with <3 salary rows
    r = test_client.post("/api/GetEmpStatus", json={"NationalNumber": "NAT1012"})
    assert r.status_code == 422
    assert r.json()["detail"] == "INSUFFICIENT_DATA"
