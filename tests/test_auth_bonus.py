import pytest

@pytest.mark.parametrize("header,expected", [
    ({}, 401),
    ({"Authorization": "Bearer wrong"}, 401),
    ({"Authorization": "Bearer secret123"}, 200),
])
def test_bearer_auth_paths(test_client, header, expected):
    # Turn on auth for this test only by setting the token in settings
    from app.settings import settings
    settings.API_TOKEN = "secret123"

    r = test_client.post("/api/GetEmpStatus",
                         json={"NationalNumber": "NAT1001"},
                         headers={"Content-Type": "application/json", **header})
    assert r.status_code == expected

    # Turn back off for other tests
    settings.API_TOKEN = None
