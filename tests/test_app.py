from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "EduGenie" in response.text


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_task_validation():
    response = client.post("/task", json={"task": "bad", "text": "hello"})
    assert response.status_code == 400
    assert response.json()["detail"]


def test_qna_route(monkeypatch):
    monkeypatch.setattr(main, "answer_question", lambda q: "Mock answer")
    response = client.post("/qa", json={"question": "What is AI?"})
    assert response.status_code == 200
    assert response.json()["result"] == "Mock answer"


def test_explain_route(monkeypatch):
    monkeypatch.setattr(main, "explain_concept", lambda q: "Simple explanation")
    response = client.post("/explain", json={"text": "Photosynthesis"})
    assert response.status_code == 200
    assert response.json()["result"] == "Simple explanation"


def test_quiz_route(monkeypatch):
    sample = {
        "questions": [
            {
                "question": "Q1",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
            }
        ] * 3
    }
    monkeypatch.setattr(main, "generate_quiz", lambda q: sample)
    response = client.post("/quiz", json={"text": "A passage"})
    assert response.status_code == 200
    assert len(response.json()["result"]["questions"]) == 3


def test_summary_route(monkeypatch):
    monkeypatch.setattr(main, "summarize_text", lambda q: "Summary")
    response = client.post("/summarize", json={"text": "Long passage"})
    assert response.status_code == 200
    assert response.json()["result"] == "Summary"


def test_learning_route(monkeypatch):
    monkeypatch.setattr(main, "get_learning_recommendations", lambda q: "Learning path")
    response = client.post("/learn/recommendations", json={"text": "SQL"})
    assert response.status_code == 200
    assert response.json()["result"] == "Learning path"


def test_unified_task_success(monkeypatch):
    monkeypatch.setattr(main, "answer_question", lambda q: "Mock unified answer")
    response = client.post("/task", json={"task": "qa", "text": "What is AI?"})

    assert response.status_code == 200
    assert response.json() == {"task": "qa", "result": "Mock unified answer"}


def test_unified_task_returns_json_on_ai_error(monkeypatch):
    def fail(_text):
        raise RuntimeError("Gemini service is temporarily unavailable")

    monkeypatch.setattr(main, "generate_quiz", fail)
    response = client.post("/task", json={"task": "quiz", "text": "AI"})

    assert response.status_code == 503
    body = response.json()
    assert body["task"] == "quiz"
    assert "temporarily unavailable" in body["detail"]


def test_validation_error_is_json():
    response = client.post("/task", json={"task": "quiz", "text": ""})
    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/json")
    assert response.json()["detail"]
