import json
import random
from unittest.mock import patch

from es_app.config import get_settings
from es_app.db import get_connection, init_db
from es_app.exam.service import ExamService
from es_app.exam.templates import build_contextual_blank, build_synonym_mcq
from es_app.lexicon.seed import seed_builtin_toefl
from es_app.lexicon.service import LexiconService
from es_app.lexicon.store import LexiconStore
from es_app.plans.service import PlanService
from es_app.quiz.distractors import pick_definition_distractors
from es_app.schemas.word import WordCandidate


def _setup_exam(conn, *, daily_quota: int = 10):
    store = LexiconStore(conn)
    lex = LexiconService(store)
    seed_builtin_toefl(lex)
    plans = PlanService(conn, store)
    plan = plans.create_plan(exam_type="toefl", daily_quota=daily_quota)
    exam = ExamService(conn, store, plans)
    return plan, exam, store


def _plan_words(store, plan):
    words = []
    for day in plan.days:
        for wid in day.word_ids:
            words.append(store.get_by_id(wid))
    return words


def test_build_synonym_mcq_has_four_options(conn):
    plan, _, store = _setup_exam(conn)
    words = _plan_words(store, plan)
    word = words[0]
    pool = [w.definitions[0] for w in words if w.definitions]

    with patch(
        "es_app.exam.templates.pick_definition_distractors",
        wraps=pick_definition_distractors,
    ) as mock_pick:
        q = build_synonym_mcq(word, pool, rng=random.Random(0))

    assert q is not None
    assert q["type"] == "synonym_mcq"
    assert q["word_id"] == word.id
    assert q["stem"] == word.word
    assert len(q["options"]) == 4
    assert q["correct_choice"] == word.definitions[0]
    assert q["correct_choice"] in q["options"]
    mock_pick.assert_called_once()
    correct, passed_pool = mock_pick.call_args.args[0], mock_pick.call_args.args[1]
    assert correct == word.definitions[0]
    assert passed_pool == pool
    wrong = [o for o in q["options"] if o != q["correct_choice"]]
    assert len(wrong) == 3
    assert all(o in pool for o in wrong)


def test_contextual_skips_word_without_examples(conn):
    store = LexiconStore(conn)
    no_ex = store.add_from_candidate(
        WordCandidate(word="noexample", definitions=["无例句词"], examples=[])
    )
    assert build_contextual_blank(no_ex) is None

    with_ex = store.add_from_candidate(
        WordCandidate(
            word="sample",
            definitions=["a specimen"],
            examples=["This is a sample sentence for testing."],
        )
    )
    q = build_contextual_blank(
        with_ex,
        word_pool=["other", "sample", "words", "alpha", "beta"],
    )
    assert q is not None
    assert q["type"] == "contextual_blank"
    assert "____" in q["stem"]
    assert "sample" not in q["stem"].lower()
    assert q["correct_choice"] == "sample"
    assert len(q["options"]) == 4
    assert "sample" in q["options"]


def test_exam_session_survives_new_connection(data_dir, monkeypatch):
    """同一 ES_DATA_DIR，第二次新连接仍能 submit。"""
    monkeypatch.setenv("ES_DATA_DIR", str(data_dir))
    get_settings.cache_clear()

    conn1 = get_connection(data_dir)
    init_db(conn1)
    store1 = LexiconStore(conn1)
    seed_builtin_toefl(LexiconService(store1))
    plans1 = PlanService(conn1, store1)
    plan = plans1.create_plan(exam_type="toefl", daily_quota=5)
    exam1 = ExamService(conn1, store1, plans1)
    session = exam1.create_session(plan_id=plan.id, question_count=3)
    session_id = session.id
    questions = session.questions
    answers = [
        {"question_id": q.id, "choice": _correct_choice(conn1, session_id, q.id)}
        for q in questions
    ]
    conn1.close()

    conn2 = get_connection(data_dir)
    store2 = LexiconStore(conn2)
    exam2 = ExamService(conn2, store2, PlanService(conn2, store2))
    report = exam2.submit(session_id, answers=answers)
    assert report.score == report.total
    assert report.wrong_word_ids == []

    row = conn2.execute(
        "SELECT questions_json FROM exam_sessions WHERE id = ?", (session_id,)
    ).fetchone()
    assert row is not None
    stored = json.loads(row["questions_json"])
    assert len(stored) == len(questions)

    events = conn2.execute(
        "SELECT kind, word_id, payload_json FROM progress_events ORDER BY id"
    ).fetchall()
    assert len(events) == len(questions)
    assert all(e["kind"] == "exam" for e in events)
    conn2.close()


def test_exam_report_scores(conn):
    plan, exam, _store = _setup_exam(conn)
    session = exam.create_session(plan_id=plan.id, question_count=4)
    assert len(session.questions) == 4
    types = {q.type for q in session.questions}
    assert "synonym_mcq" in types
    assert "contextual_blank" in types

    row = conn.execute(
        "SELECT COUNT(*) AS n FROM exam_sessions WHERE id = ?", (session.id,)
    ).fetchone()
    assert row["n"] == 1

    q0 = session.questions[0]
    correct = _correct_choice(conn, session.id, q0.id)

    answers = []
    for i, q in enumerate(session.questions):
        choice = correct if q.id == q0.id else _wrong_choice(conn, session.id, q.id)
        answers.append({"question_id": q.id, "choice": choice})

    report = exam.submit(session.id, answers=answers)
    assert report.total == 4
    assert report.score == 1
    assert len(report.wrong_word_ids) == 3
    assert q0.word_id not in report.wrong_word_ids

    wrong_ids_set = set()
    for i, q in enumerate(session.questions):
        if i != 0:
            wrong_ids_set.add(q.word_id)
    assert set(report.wrong_word_ids) == wrong_ids_set

    events = conn.execute(
        "SELECT kind, word_id, payload_json FROM progress_events ORDER BY id"
    ).fetchall()
    assert len(events) == 4
    assert all(e["kind"] == "exam" for e in events)
    payloads = [json.loads(e["payload_json"]) for e in events]
    assert sum(1 for p in payloads if p["correct"]) == 1
    assert all(p["session_id"] == session.id for p in payloads)


def _stored_questions(conn, session_id):
    row = conn.execute(
        "SELECT questions_json FROM exam_sessions WHERE id = ?", (session_id,)
    ).fetchone()
    return json.loads(row["questions_json"])


def _question_by_id(conn, session_id, question_id):
    for q in _stored_questions(conn, session_id):
        if q["id"] == question_id:
            return q
    raise AssertionError(f"question {question_id} not found")


def _correct_choice(conn, session_id, question_id):
    return _question_by_id(conn, session_id, question_id)["correct_choice"]


def _options(conn, session_id, question_id):
    return _question_by_id(conn, session_id, question_id)["options"]


def _wrong_choice(conn, session_id, question_id):
    q = _question_by_id(conn, session_id, question_id)
    return next(o for o in q["options"] if o != q["correct_choice"])
