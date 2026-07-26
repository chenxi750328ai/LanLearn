import json
from importlib import resources

from es_app.lexicon.service import LexiconService
from es_app.schemas.word import WordCandidate


def seed_builtin_toefl(service: LexiconService) -> int:
    raw = resources.files("es_app.lexicon").joinpath("builtin_toefl.json").read_text(encoding="utf-8")
    items = json.loads(raw)
    added = 0
    for item in items:
        cand = WordCandidate.model_validate(item)
        before = service.list_words()
        words = {w.word for w in before}
        if cand.word in words:
            continue
        service.confirm_candidates([cand])
        added += 1
    return added
