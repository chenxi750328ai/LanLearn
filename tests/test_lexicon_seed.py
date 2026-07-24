from es_app.lexicon.store import LexiconStore
from es_app.lexicon.service import LexiconService
from es_app.lexicon.seed import seed_builtin_toefl


def test_seed_inserts_at_least_20(conn):
    svc = LexiconService(LexiconStore(conn))
    n = seed_builtin_toefl(svc)
    assert n >= 20
    assert len(svc.list_words()) >= 20
    assert seed_builtin_toefl(svc) == 0  # idempotent
