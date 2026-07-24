from es_app.adapters.protocols import OcrPort, VisionOcrPort
from es_app.ingest.ocr_pipeline import run_ocr_to_candidates
from es_app.ingest.parsers import parse_csv, parse_txt
from es_app.lexicon.service import LexiconService
from es_app.schemas.word import Word, WordCandidate


class IngestService:
    def __init__(
        self,
        lexicon: LexiconService,
        ocr: OcrPort | None = None,
        vision: VisionOcrPort | None = None,
    ):
        self._lexicon = lexicon
        self._ocr = ocr
        self._vision = vision

    def parse_file(self, filename: str, content: str) -> tuple[list[WordCandidate], list[dict]]:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext == "csv":
            return parse_csv(content)
        if ext == "txt":
            return parse_txt(content)
        raise ValueError(f"unsupported file type: {ext or filename}")

    def parse_image(self, image_bytes: bytes) -> list[WordCandidate]:
        if self._ocr is None:
            raise RuntimeError("OCR adapter not configured")
        return run_ocr_to_candidates(self._ocr, image_bytes, self._vision)

    def confirm(self, candidates: list[WordCandidate]) -> list[Word]:
        return self._lexicon.confirm_candidates(candidates)
