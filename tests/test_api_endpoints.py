import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_and_network_ip():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "healthy"}

    ip_res = client.get("/api/network-ip")
    assert ip_res.status_code == 200
    assert "ip" in ip_res.json()
    assert "vite_port" in ip_res.json()

def test_admin_endpoints():
    # Login as admin
    admin_login = client.post("/api/auth/login/json", json={
        "email": "admin@example.com",
        "password": "Password123!"
    })
    assert admin_login.status_code == 200, admin_login.text
    token = admin_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Admin overview
    overview_res = client.get("/api/admin/overview", headers=headers)
    assert overview_res.status_code == 200, overview_res.text
    data = overview_res.json()
    assert "total_users" in data
    assert "platform_avg_score" in data

    # Admin users list
    users_res = client.get("/api/admin/users", headers=headers)
    assert users_res.status_code == 200, users_res.text
    users = users_res.json()
    assert isinstance(users, list)
    assert len(users) > 0

    # Admin quizzes list
    quizzes_res = client.get("/api/admin/quizzes", headers=headers)
    assert quizzes_res.status_code == 200, quizzes_res.text
    assert isinstance(quizzes_res.json(), list)

def test_question_validation_and_regeneration():
    prof_login = client.post("/api/auth/login/json", json={
        "email": "prof_test@example.com",
        "password": "Password123!"
    })
    token = prof_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Generate 1 question
    gen_res = client.post("/api/questions/generate", json={
        "topic": "Algorithms",
        "num_questions": 1,
        "question_type": "MCQ",
        "difficulty": "Medium",
        "style": "Conceptual"
    }, headers=headers)
    assert gen_res.status_code == 200
    q = gen_res.json()[0]
    qid = q["id"]

    # Validate
    val_res = client.post("/api/questions/validate", json={"question_id": qid}, headers=headers)
    assert val_res.status_code == 200
    assert "is_valid" in val_res.json()

    # Regenerate
    regen_res = client.post("/api/questions/regenerate", json={"question_id": qid}, headers=headers)
    assert regen_res.status_code == 200
    assert regen_res.json()["id"] == qid
