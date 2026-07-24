import json

from es_app.lexicon.seed import seed_builtin_toefl
from es_app.lexicon.service import LexiconService
from es_app.lexicon.store import LexiconStore
from es_app.plans.service import PlanService
from es_app.study.service import StudyService


def _setup_plan(conn, *, daily_quota: int = 5):
    lex = LexiconService(LexiconStore(conn))
    seed_builtin_toefl(lex)
    plans = PlanService(conn, LexiconStore(conn))
    plan = plans.create_plan(exam_type="toefl", daily_quota=daily_quota)
    study = StudyService(conn, LexiconStore(conn), plans)
    return plan, study, lex


def test_study_mcq_answer(conn):
    plan, study, _lex = _setup_plan(conn)
    session = study.create_session(plan_id=plan.id, day_index=0, mode="mcq")

    assert session.mode == "mcq"
    assert len(session.cards) == plan.days[0].word_ids.__len__()
    card = session.cards[0]
    assert card.word
    assert card.options is not None
    assert len(card.options) == 4
    assert card.correct_definition in card.options

    word_id = card.word_id
    correct_def = card.correct_definition
    wrong = next(o for o in card.options if o != correct_def)

    ok = study.answer(session.id, word_id=word_id, answer=correct_def)
    assert ok.correct is True
    assert ok.correct_definition == correct_def

    bad = study.answer(session.id, word_id=word_id, answer=wrong)
    assert bad.correct is False
    assert bad.correct_definition == correct_def

    rows = conn.execute(
        "SELECT kind, word_id, payload_json FROM progress_events ORDER BY id"
    ).fetchall()
    assert len(rows) == 2
    assert all(r["kind"] == "study" for r in rows)
    payloads = [json.loads(r["payload_json"]) for r in rows]
    assert payloads[0]["correct"] is True
    assert payloads[1]["correct"] is False


def test_study_flashcard_session(conn):
    plan, study, _lex = _setup_plan(conn)
    session = study.create_session(plan_id=plan.id, day_index=0, mode="flashcard")

    assert session.mode == "flashcard"
    assert all(c.options is None for c in session.cards)

    card = session.cards[0]
    result = study.answer(session.id, word_id=card.word_id, answer=card.correct_definition)
    assert result.correct is True

    row = conn.execute(
        "SELECT COUNT(*) AS n FROM study_sessions WHERE id = ?", (session.id,)
    ).fetchone()
    assert row["n"] == 1
