def test_auth_login(client):
    res = client.post("/api/auth/login", json={"email": "admin@veritrace.gov.in", "password": "admin123"})
    assert res.status_code == 200
    data = res.json()["data"]
    assert "access_token" in data
    assert data["role"] == "admin"

def test_case_crud_and_duplicate_conflict(client):
    # 1. Create case
    case_payload = {
        "case_number": "CASE-TEST-100",
        "title": "Integration Test Case",
        "institution_name": "Test Engineering Institute"
    }
    res = client.post("/api/cases", json=case_payload)
    assert res.status_code == 201
    case_data = res.json()["data"]
    assert case_data["case_number"] == "CASE-TEST-100"

    # 2. Duplicate case creation must return 409 Conflict
    res_dup = client.post("/api/cases", json=case_payload)
    assert res_dup.status_code == 409

    # 3. List cases
    res_list = client.get("/api/cases")
    assert res_list.status_code == 200
    assert any(c["case_number"] == "CASE-TEST-100" for c in res_list.json()["data"])

def test_rules_endpoint(client):
    res = client.get("/api/rules")
    assert res.status_code == 200
    rules = res.json()["data"]
    assert len(rules) >= 5

def test_dashboard_summary(client):
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200
    data = res.json()["data"]
    assert "findings_by_severity" in data
    assert "system_truth_states" in data
