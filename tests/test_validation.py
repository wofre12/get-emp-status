def test_missing_field(test_client):
    r = test_client.post("/api/GetEmpStatus", json={})
    assert r.status_code == 422

def test_wrong_type(test_client):
    r = test_client.post("/api/GetEmpStatus", json={"NationalNumber": 12345})
    assert r.status_code == 422

def test_empty_string(test_client):
    r = test_client.post("/api/GetEmpStatus", json={"NationalNumber": ""})
    assert r.status_code == 422
