from es_app.lexicon.store import LexiconStore
from es_app.schemas.word import Word, WordCandidate


class LexiconService:
    def __init__(self, store: LexiconStore):
        self._store = store

    def list_words(self, complete_only: bool = False) -> list[Word]:
        return self._store.list_words(complete_only=complete_only)

    def confirm_candidates(self, candidates: list[WordCandidate]) -> list[Word]:
        out: list[Word] = []
        for c in candidates:
            existing = self._store.get_by_word(c.word.strip())
            if existing:
                out.append(existing)
                continue
            out.append(self._store.add_from_candidate(c))
        return out
