from fastapi.testclient import TestClient

from es_app.config import get_settings
from es_app.main import create_app


def test_toefl_loop(data_dir, monkeypatch):
    monkeypatch.setenv("ES_DATA_DIR", str(data_dir))
    get_settings.cache_clear()
    client = TestClient(create_app())

    plan_resp = client.post("/plans", json={"exam_type": "toefl", "daily_quota": 5})
    assert plan_resp.status_code == 200
    plan = plan_resp.json()
    plan_id = plan["id"]

    words = client.get("/lexicon/words").json()
    assert len(words) >= 20

    speech = client.post("/speech/evaluate", json={"word_id": words[0]["id"]})
    assert speech.status_code == 503
    assert speech.json()["code"] == "ollama_unavailable"

    study_resp = client.post(
        "/study/sessions",
        json={"plan_id": plan_id, "day_index": 0, "mode": "mcq"},
    )
    assert study_resp.status_code == 200
    session = study_resp.json()
    card = session["cards"][0]
    answer_resp = client.post(
        f"/study/sessions/{session['id']}/answer",
        json={"word_id": card["word_id"], "answer": card["correct_definition"]},
    )
    assert answer_resp.status_code == 200
    assert answer_resp.json()["correct"] is True

    exam_resp = client.post(
        "/exam/sessions",
        json={"plan_id": plan_id, "question_count": 2},
    )
    assert exam_resp.status_code == 200
    exam = exam_resp.json()
    answers = [{"question_id": q["id"], "choice": q["options"][0]} for q in exam["questions"]]
    submit_resp = client.post(
        f"/exam/sessions/{exam['id']}/submit",
        json={"answers": answers},
    )
    assert submit_resp.status_code == 200

    progress = client.get("/progress/summary").json()
    assert progress["study_answered"] >= 1
    assert progress["exam_sessions"] >= 1

    assert client.get("/ui/").status_code == 200

    root = client.get("/", follow_redirects=False)
    assert root.status_code in (302, 307)
    assert root.headers["location"].endswith("/ui/")

    get_plan = client.get(f"/plans/{plan_id}")
    assert get_plan.status_code == 200
    assert get_plan.json()["id"] == plan_id


def test_study_session_persists_across_app_instances(data_dir, monkeypatch):
    monkeypatch.setenv("ES_DATA_DIR", str(data_dir))
    get_settings.cache_clear()

    client1 = TestClient(create_app())
    plan = client1.post("/plans", json={"exam_type": "toefl", "daily_quota": 5}).json()
    session = client1.post(
        "/study/sessions",
        json={"plan_id": plan["id"], "day_index": 0, "mode": "mcq"},
    ).json()
    card = session["cards"][0]

    get_settings.cache_clear()
    client2 = TestClient(create_app())
    answer = client2.post(
        f"/study/sessions/{session['id']}/answer",
        json={"word_id": card["word_id"], "answer": card["correct_definition"]},
    )
    assert answer.status_code == 200
    assert answer.json()["correct"] is True


def test_exam_session_persists_across_app_instances(data_dir, monkeypatch):
    """同一 ES_DATA_DIR，第二次 create_app/新连接仍能 submit。"""
    monkeypatch.setenv("ES_DATA_DIR", str(data_dir))
    get_settings.cache_clear()

    client1 = TestClient(create_app())
    plan = client1.post("/plans", json={"exam_type": "toefl", "daily_quota": 5}).json()
    exam = client1.post(
        "/exam/sessions",
        json={"plan_id": plan["id"], "question_count": 3},
    ).json()

    get_settings.cache_clear()
    client2 = TestClient(create_app())
    answers = [
        {"question_id": q["id"], "choice": q["options"][0]} for q in exam["questions"]
    ]
    submit = client2.post(
        f"/exam/sessions/{exam['id']}/submit",
        json={"answers": answers},
    )
    assert submit.status_code == 200
    report = submit.json()
    assert report["total"] == len(exam["questions"])
    assert 0 <= report["score"] <= report["total"]
