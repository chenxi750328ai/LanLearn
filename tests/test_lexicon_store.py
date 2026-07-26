from es_app.lexicon.store import LexiconStore
from es_app.schemas.word import WordCandidate


def test_add_and_list_marks_incomplete(conn):
    store = LexiconStore(conn)
    w = store.add_from_candidate(WordCandidate(word="foo", definitions=[]))
    assert w.incomplete is True
    w2 = store.add_from_candidate(
        WordCandidate(word="bar", definitions=["放弃"], examples=["He abandoned it."])
    )
    assert w2.incomplete is False
    assert len(store.list_words()) == 2
    assert len(store.list_words(complete_only=True)) == 1
