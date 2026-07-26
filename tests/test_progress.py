import json
from datetime import datetime, timezone

from es_app.exam.service import ExamService
from es_app.lexicon.seed import seed_builtin_toefl
from es_app.lexicon.service import LexiconService
from es_app.lexicon.store import LexiconStore
from es_app.plans.service import PlanService
from es_app.progress.router import get_summary
from es_app.progress.service import ProgressService
from es_app.study.service import StudyService


def _setup(conn, *, daily_quota: int = 10):
    store = LexiconStore(conn)
    lex = LexiconService(store)
    seed_builtin_toefl(lex)
    plans = PlanService(conn, store)
    plan = plans.create_plan(exam_type="toefl", daily_quota=daily_quota)
    study = StudyService(conn, store, plans)
    exam = ExamService(conn, store, plans)
    progress = ProgressService(conn)
    return plan, study, exam, progress


def _insert_event(conn, *, kind: str, word_id: int, correct: bool) -> None:
    created_at = datetime.now(timezone.utc).isoformat()
    payload = {"correct": correct}
    conn.execute(
        """
        INSERT INTO progress_events (kind, word_id, payload_json, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (kind, word_id, json.dumps(payload), created_at),
    )
    conn.commit()


def test_progress_summary_empty(conn):
    progress = ProgressService(conn)
    summary = progress.get_summary()
    assert summary.study_answered == 0
    assert summary.study_correct == 0
    assert summary.exam_sessions == 0
    assert summary.weak_word_ids == []


def test_progress_summary_aggregates_study_and_exam(conn):
    plan, study, exam, progress = _setup(conn)
    session = study.create_session(plan_id=plan.id, day_index=0, mode="flashcard")
    cards = session.cards

    study.answer(session.id, word_id=cards[0].word_id, answer=cards[0].correct_definition)
    study.answer(session.id, word_id=cards[1].word_id, answer="wrong answer")

    exam_session = exam.create_session(plan_id=plan.id, question_count=2)
    answers = []
    for q in exam_session.questions:
        row = conn.execute(
            "SELECT questions_json FROM exam_sessions WHERE id = ?", (exam_session.id,)
        ).fetchone()
        stored = {item["id"]: item for item in json.loads(row["questions_json"])}
        wrong = next(o for o in stored[q.id]["options"] if o != stored[q.id]["correct_choice"])
        answers.append({"question_id": q.id, "choice": wrong})
    exam.submit(exam_session.id, answers=answers)

    summary = progress.get_summary()
    assert summary.study_answered == 2
    assert summary.study_correct == 1
    assert summary.exam_sessions == 1
    assert cards[1].word_id in summary.weak_word_ids
    for q in exam_session.questions:
        assert q.word_id in summary.weak_word_ids


def test_weak_word_ids_ranked_and_capped(conn):
    for _ in range(5):
        _insert_event(conn, kind="study", word_id=1, correct=False)
    for _ in range(3):
        _insert_event(conn, kind="exam", word_id=2, correct=False)
    _insert_event(conn, kind="study", word_id=3, correct=False)
    _insert_event(conn, kind="study", word_id=4, correct=True)

    summary = ProgressService(conn).get_summary()
    assert summary.weak_word_ids == [1, 2, 3]

    for word_id in range(1, 26):
        for _ in range(26 - word_id):
            _insert_event(conn, kind="study", word_id=word_id, correct=False)

    capped = ProgressService(conn).get_summary()
    assert len(capped.weak_word_ids) == 20
    assert capped.weak_word_ids == list(range(1, 21))


def test_progress_summary_endpoint(conn):
    progress = ProgressService(conn)
    summary = get_summary(svc=progress)
    assert summary.study_answered == 0
    assert summary.study_correct == 0
    assert summary.exam_sessions == 0
    assert summary.weak_word_ids == []
