from es_app.schemas.word import WordCandidate


def test_word_candidate_defaults():
    c = WordCandidate(word="abandon")
    assert c.phonetic is None
    assert c.definitions == []
    assert c.examples == []
