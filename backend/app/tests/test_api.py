from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app


client = TestClient(app)


def solve_captcha(question: str) -> str:
    left, operator, right, *_ = question.split()
    if operator == "+":
        return str(int(left) + int(right))
    if operator == "-":
        return str(int(left) - int(right))
    return str(int(left) * int(right))


def test_overview_summary():
    response = client.get("/api/overview/summary")
    assert response.status_code == 200
    assert response.json()["job_count"] >= 10


def test_jd_parse():
    text = "大模型应用工程师，需要 Python、RAG、LangChain、向量数据库 和 Docker。"
    response = client.post("/api/jd/parse", json={"text": text})
    assert response.status_code == 200
    assert response.json()["job_name"] == "大模型应用工程师"


def test_hr_login_and_candidate_list():
    response = client.post("/api/auth/login", json={"username": "hr_admin", "password": "Demo@123"})
    assert response.status_code == 200
    token = response.json()["token"]
    assert response.json()["user"]["role"] == "hr"

    candidates = client.get("/api/hr/candidates", headers={"Authorization": f"Bearer {token}"})
    assert candidates.status_code == 200
    assert len(candidates.json()) >= 1


def test_candidate_profile_update_and_role_guard():
    response = client.post("/api/auth/login", json={"username": "student_demo", "password": "Demo@123"})
    assert response.status_code == 200
    token = response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    profile = client.put(
        "/api/profile/me",
        headers=headers,
        json={
            "real_name": "Demo Student",
            "education": "本科",
            "major": "数据科学",
            "school": "示例大学",
            "target_role": "数据分析师",
            "city": "上海",
            "expected_salary": "12k-16k",
            "skills": ["Python", "SQL", "数据可视化"],
            "certificates": ["CET-6"],
            "projects": ["校园招聘数据分析项目"],
            "internships": ["数据运营实习"],
            "awards": ["数学建模竞赛"],
            "self_summary": "关注数据分析和业务洞察。",
        },
    )
    assert profile.status_code == 200
    assert profile.json()["completeness"] > 80

    forbidden = client.get("/api/hr/candidates", headers=headers)
    assert forbidden.status_code == 403


def test_candidate_resume_scope_and_match_guard():
    hr_login = client.post("/api/auth/login", json={"username": "hr_admin", "password": "Demo@123"})
    candidate_login = client.post("/api/auth/login", json={"username": "student_demo", "password": "Demo@123"})
    assert hr_login.status_code == 200
    assert candidate_login.status_code == 200

    hr_headers = {"Authorization": f"Bearer {hr_login.json()['token']}"}
    candidate = candidate_login.json()["user"]
    candidate_headers = {"Authorization": f"Bearer {candidate_login.json()['token']}"}

    all_resumes = client.get("/api/resumes", headers=hr_headers)
    own_resumes = client.get("/api/resumes", headers=candidate_headers)
    assert all_resumes.status_code == 200
    assert own_resumes.status_code == 200
    assert all(row["user_id"] == candidate["id"] for row in own_resumes.json())

    foreign = next((row for row in all_resumes.json() if row["user_id"] != candidate["id"]), None)
    assert foreign is not None
    blocked = client.post(
        "/api/match-analysis",
        headers=candidate_headers,
        json={"resume_id": foreign["id"], "target_job_id": 1},
    )
    assert blocked.status_code == 403


def test_register_with_rules_and_math_captcha():
    captcha = client.get("/api/auth/captcha")
    assert captcha.status_code == 200
    captcha_data = captcha.json()
    username = f"u{uuid4().hex[:7]}1"
    payload = {
        "username": username,
        "password": "abc12345",
        "confirm_password": "abc12345",
        "role": "candidate",
        "display_name": "测试用户",
        "email": "demo2026@example.com",
        "organization": "示例学校",
        "captcha_token": captcha_data["token"],
        "captcha_answer": solve_captcha(captcha_data["question"]),
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 200
    assert response.json()["user"]["username"] == username


def test_register_rejects_invalid_username():
    captcha_data = client.get("/api/auth/captcha").json()
    response = client.post(
        "/api/auth/register",
        json={
            "username": "abcdef",
            "password": "abc12345",
            "confirm_password": "abc12345",
            "role": "candidate",
            "display_name": "测试用户",
            "email": "bad-name@example.com",
            "captcha_token": captcha_data["token"],
            "captcha_answer": solve_captcha(captcha_data["question"]),
        },
    )
    assert response.status_code == 400
