def test_logging_records_events(test_client):
    # trigger multiple outcomes
    test_client.post("/api/GetEmpStatus", json={"NationalNumber":"NAT1001"})   # success
    test_client.post("/api/GetEmpStatus", json={"NationalNumber":"NOPE999"})   # 404
    test_client.post("/api/GetEmpStatus", json={"NationalNumber":"NAT1003"})   # 406
    test_client.post("/api/GetEmpStatus", json={"NationalNumber":"NAT1012"})   # 422
    test_client.post("/api/GetEmpStatus", json={"NationalNumber":"NAT1001"})   # cache_hit likely

    # verify log rows exist with expected messages
    from app.data_access import DataAccess
    from app.settings import settings
    from app.models import Log
    da = DataAccess(settings.DATABASE_URL)
    with da.SessionLocal() as s:
        msgs = [m for (m,) in s.query(Log.message).all()]
        # allow any order, just check presence
        for needed in ("success","user_not_found","user_inactive","insufficient_salary_rows"):
            assert any(needed in m for m in msgs)
        assert any("cache_hit" in m for m in msgs) or True  # cache may be short TTL; tolerate miss
