AUTH = {"Authorization": "Bearer secret123"}

def test_health(test_client):
    # Health typically does not require auth
    r = test_client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"ok": True}

def test_happy_nat1001(test_client):
    r = test_client.post("/api/GetEmpStatus", json={"NationalNumber": "NAT1001"}, headers=AUTH)
    assert r.status_code == 200
    body = r.json()
    # flat, PascalCase payload assertions
    for k in ["EmployeeName", "NationalNumber", "HighestSalary", "AverageSalary", "Status", "IsActive", "LastUpdated"]:
        assert k in body
    assert body["NationalNumber"] == "NAT1001"
    assert body["Status"] in ("RED", "ORANGE", "GREEN")
    assert isinstance(body["HighestSalary"], (int, float))
    assert isinstance(body["AverageSalary"], (int, float))
    assert isinstance(body["IsActive"], bool)
    assert "T" in body["LastUpdated"] and body["LastUpdated"].endswith("Z")

def test_not_found(test_client):
    r = test_client.post("/api/GetEmpStatus", json={"NationalNumber": "NOPE999"}, headers=AUTH)
    assert r.status_code == 404

def test_inactive(test_client):
    r = test_client.post("/api/GetEmpStatus", json={"NationalNumber": "NAT1003"}, headers=AUTH)
    assert r.status_code == 406

def test_insufficient_data(test_client):
    # from your seed: NAT1012 is active with <3 salary rows
    r = test_client.post("/api/GetEmpStatus", json={"NationalNumber": "NAT1012"}, headers=AUTH)
    assert r.status_code == 422
    assert r.json()["error"] == "INSUFFICIENT_DATA"
