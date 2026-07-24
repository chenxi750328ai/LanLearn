from es_app.config import get_settings
from es_app.db import get_connection, init_db
from es_app.lexicon.seed import seed_builtin_toefl
from es_app.lexicon.service import LexiconService
from es_app.lexicon.store import LexiconStore
from es_app.plans.service import PlanService
from es_app.study.service import StudyService


def test_study_session_survives_new_connection(data_dir, monkeypatch):
    """同一 ES_DATA_DIR，第二次 create_app/新连接仍能 answer。"""
    monkeypatch.setenv("ES_DATA_DIR", str(data_dir))
    get_settings.cache_clear()

    conn1 = get_connection(data_dir)
    init_db(conn1)
    lex1 = LexiconService(LexiconStore(conn1))
    seed_builtin_toefl(lex1)
    plans1 = PlanService(conn1, LexiconStore(conn1))
    plan = plans1.create_plan(exam_type="toefl", daily_quota=5)
    study1 = StudyService(conn1, LexiconStore(conn1), plans1)
    session = study1.create_session(plan_id=plan.id, day_index=0, mode="mcq")
    card = session.cards[0]
    session_id = session.id
    word_id = card.word_id
    correct_def = card.correct_definition
    conn1.close()

    conn2 = get_connection(data_dir)
    plans2 = PlanService(conn2, LexiconStore(conn2))
    study2 = StudyService(conn2, LexiconStore(conn2), plans2)
    result = study2.answer(session_id, word_id=word_id, answer=correct_def)
    assert result.correct is True
    assert result.correct_definition == correct_def
    conn2.close()
