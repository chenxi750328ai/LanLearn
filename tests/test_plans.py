import pytest

from es_app.errors import AppError
from es_app.lexicon.seed import seed_builtin_toefl
from es_app.lexicon.service import LexiconService
from es_app.lexicon.store import LexiconStore
from es_app.plans.service import PlanService


def test_create_toefl_plan_slices_days(conn):
    lex = LexiconService(LexiconStore(conn))
    seed_builtin_toefl(lex)
    plans = PlanService(conn, LexiconStore(conn))
    plan = plans.create_plan(exam_type="toefl", daily_quota=5)
    assert plan.exam_type == "toefl"
    assert plan.daily_quota == 5
    assert len(plan.days) >= 1
    assert sum(len(d.word_ids) for d in plan.days) == len(lex.list_words(complete_only=True))


def test_create_plan_empty_lexicon_400(conn):
    plans = PlanService(conn, LexiconStore(conn))
    with pytest.raises(AppError) as exc_info:
        plans.create_plan(exam_type="toefl", daily_quota=5)
    assert exc_info.value.status_code == 400
    assert exc_info.value.code == "empty_lexicon"
