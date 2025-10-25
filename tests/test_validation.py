AUTH = {"Authorization": "Bearer secret123"}

def test_missing_field(test_client):
    r = test_client.post("/api/GetEmpStatus", json={}, headers=AUTH)
    assert r.status_code == 422

def test_wrong_type(test_client):
    r = test_client.post("/api/GetEmpStatus", json={"NationalNumber": 12345}, headers=AUTH)
    assert r.status_code == 422

def test_empty_string(test_client):
    r = test_client.post("/api/GetEmpStatus", json={"NationalNumber": ""}, headers=AUTH)
    assert r.status_code == 422
