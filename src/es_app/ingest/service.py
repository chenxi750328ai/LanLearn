from es_app.ingest.parsers import parse_csv, parse_txt
from es_app.lexicon.service import LexiconService
from es_app.schemas.word import Word, WordCandidate


class IngestService:
    def __init__(self, lexicon: LexiconService):
        self._lexicon = lexicon

    def parse_file(self, filename: str, content: str) -> tuple[list[WordCandidate], list[dict]]:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext == "csv":
            return parse_csv(content)
        if ext == "txt":
            return parse_txt(content)
        raise ValueError(f"unsupported file type: {ext or filename}")

    def confirm(self, candidates: list[WordCandidate]) -> list[Word]:
        return self._lexicon.confirm_candidates(candidates)
