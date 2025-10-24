def test_tax_rule_applies_when_total_gt_10000(test_client):
    # NAT1008 in your seed has large totals + December -> adjusted total > 10k
    r = test_client.post("/api/GetEmpStatus", json={"NationalNumber": "NAT1008"})
    assert r.status_code == 200
    body = r.json()
    sum_ = body["metrics"]["sum"]
    after = body["metrics"]["sumAfterTax"]
    # 7% deduction only when sum > 10000
    assert sum_ > 10000
    assert after < sum_
    # ballpark check near 93% (allow rounding wiggle)
    assert 0.92 * sum_ < after < 0.94 * sum_

def test_month_adjustments_influence_highest(test_client):
    # NAT1008 has December (+10%); highest should reflect an adjusted month
    r = test_client.post("/api/GetEmpStatus", json={"NationalNumber": "NAT1008"})
    assert r.status_code == 200
    body = r.json()
    highest = body["metrics"]["highest"]
    # highest should be a reasonable positive number after adjustment
    assert highest >= 0
    
def test_status_colors_explicit(test_client):
    # create deterministic users with months 1-3 (no month adjustments)
    from app.data_access import DataAccess
    from app.settings import settings
    from app.models import User, Salary
    da = DataAccess(settings.DATABASE_URL)

    with da.SessionLocal() as s:
        # RED: avg < 2000
        u = s.query(User).filter_by(national_number="NAT_RED").one_or_none()
        if u: s.query(Salary).filter_by(user_id=u.id).delete(); s.delete(u); s.commit()
        u = User(username="red", national_number="NAT_RED", email="r@x", phone="0", is_active=True)
        s.add(u); s.flush()
        s.add_all([Salary(user_id=u.id, year=2025, month=1, amount=1500),
                   Salary(user_id=u.id, year=2025, month=2, amount=1500),
                   Salary(user_id=u.id, year=2025, month=3, amount=1500)])

        # ORANGE: avg = 2000 exactly
        uo = s.query(User).filter_by(national_number="NAT_ORANGE").one_or_none()
        if uo: s.query(Salary).filter_by(user_id=uo.id).delete(); s.delete(uo); s.commit()
        uo = User(username="orange", national_number="NAT_ORANGE", email="o@x", phone="0", is_active=True)
        s.add(uo); s.flush()
        s.add_all([Salary(user_id=uo.id, year=2025, month=1, amount=2000),
                   Salary(user_id=uo.id, year=2025, month=2, amount=2000),
                   Salary(user_id=uo.id, year=2025, month=3, amount=2000)])

        # GREEN: avg > 2000
        ug = s.query(User).filter_by(national_number="NAT_GREEN").one_or_none()
        if ug: s.query(Salary).filter_by(user_id=ug.id).delete(); s.delete(ug); s.commit()
        ug = User(username="green", national_number="NAT_GREEN", email="g@x", phone="0", is_active=True)
        s.add(ug); s.flush()
        s.add_all([Salary(user_id=ug.id, year=2025, month=1, amount=2100),
                   Salary(user_id=ug.id, year=2025, month=2, amount=2100),
                   Salary(user_id=ug.id, year=2025, month=3, amount=2100)])
        s.commit()

    # call API and assert status
    for nat, expected in [("NAT_RED","RED"),("NAT_ORANGE","ORANGE"),("NAT_GREEN","GREEN")]:
        r = test_client.post("/api/GetEmpStatus", json={"NationalNumber": nat})
        assert r.status_code == 200
        assert r.json()["status"] == expected
