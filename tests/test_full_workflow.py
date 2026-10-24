import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_workflow():
    # 1. Register & Login Professor
    prof_email = "prof_test@example.com"
    prof_password = "Password123!"
    
    register_prof_res = client.post("/api/auth/register", json={
        "email": prof_email,
        "password": prof_password,
        "full_name": "Professor Test",
        "role_id": 1  # Professor
    })
    # If already registered in DB, login directly
    login_prof_res = client.post("/api/auth/login", data={
        "username": prof_email,
        "password": prof_password
    })
    assert login_prof_res.status_code == 200, login_prof_res.text
    prof_token = login_prof_res.json()["access_token"]
    prof_headers = {"Authorization": f"Bearer {prof_token}"}

    # 2. Generate AI Questions
    gen_res = client.post("/api/questions/generate", json={
        "topic": "Python Fundamentals",
        "num_questions": 3,
        "question_type": "MCQ",
        "difficulty": "Easy",
        "style": "Normal"
    }, headers=prof_headers)
    assert gen_res.status_code == 200, gen_res.text
    questions = gen_res.json()
    assert len(questions) > 0
    q_ids = [q["id"] for q in questions]

    # Approve questions so they can be added to quiz
    from app.core.database import SessionLocal
    from app.models.question import Question
    db = SessionLocal()
    for qid in q_ids:
        q_obj = db.query(Question).filter(Question.id == qid).first()
        if q_obj:
            q_obj.is_approved = True
    db.commit()
    db.close()

    # 3. Add to Question Bank
    bank_res = client.post("/api/questions/bank", json={"question_id": q_ids[0]}, headers=prof_headers)
    assert bank_res.status_code == 200, bank_res.text

    # 4. Create Quiz
    quiz_res = client.post("/api/quizzes/create", json={
        "title": "Python Basics Quiz",
        "description": "Test your Python knowledge",
        "topic": "Python",
        "time_limit": 15,
        "passing_percentage": 50.0,
        "question_ids": q_ids
    }, headers=prof_headers)
    assert quiz_res.status_code == 200, quiz_res.text
    quiz_data = quiz_res.json()
    quiz_id = quiz_data["id"]
    quiz_code = quiz_data["quiz_code"]

    # 5. Register & Login Student
    student_email = "student_test@example.com"
    student_password = "Password123!"
    
    register_stud_res = client.post("/api/auth/register", json={
        "email": student_email,
        "password": student_password,
        "full_name": "Student Test",
        "role_id": 2  # Student
    })
    login_stud_res = client.post("/api/auth/login", data={
        "username": student_email,
        "password": student_password
    })
    assert login_stud_res.status_code == 200, login_stud_res.text
    student_token = login_stud_res.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}

    # 6. Join Quiz via Code
    join_res = client.get(f"/api/quizzes/code/{quiz_code}", headers=student_headers)
    assert join_res.status_code == 200, join_res.text

    # 7. Start Quiz Attempt
    start_res = client.post("/api/attempts/start", json={"quiz_id": quiz_id}, headers=student_headers)
    assert start_res.status_code == 200, start_res.text
    attempt_id = start_res.json()["id"]

    # 8. Submit Quiz Attempt
    # Match correct answer for first question
    first_q_answer = questions[0]["correct_answer"]
    submit_res = client.post("/api/attempts/submit", json={
        "attempt_id": attempt_id,
        "answers": [
            {
                "question_id": q_ids[0],
                "answer": first_q_answer,
                "time_spent": 10
            }
        ]
    }, headers=student_headers)
    assert submit_res.status_code == 200, submit_res.text
    result_data = submit_res.json()
    assert result_data["total_questions"] == 3
    assert result_data["correct_answers"] == 1

    # 9. Student Analytics Overview
    stud_analytics = client.get("/api/analytics/student/overview", headers=student_headers)
    assert stud_analytics.status_code == 200, stud_analytics.text

    # 10. Professor Analytics Overview
    prof_analytics = client.get("/api/analytics/professor/overview", headers=prof_headers)
    assert prof_analytics.status_code == 200, prof_analytics.text

    # 11. Topic Explain
    explain_res = client.post("/api/topics/explain", json={"topic": "Recursion"}, headers=student_headers)
    assert explain_res.status_code == 200, explain_res.text

    print("\nSUCCESS: ALL API WORKFLOW TESTS PASSED PERFECTLY!")

if __name__ == "__main__":
    test_full_workflow()
