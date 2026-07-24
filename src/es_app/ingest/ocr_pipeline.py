import re

from es_app.adapters.protocols import NoopVisionOcr, OcrPort, VisionOcrPort
from es_app.schemas.word import WordCandidate


def candidates_from_ocr_text(text: str) -> list[WordCandidate]:
    candidates: list[WordCandidate] = []
    seen: set[str] = set()
    for token in re.split(r"\s+", text.strip()):
        word = token.strip().strip(".,;:!?\"'()[]")
        if not word or word in seen:
            continue
        seen.add(word)
        candidates.append(WordCandidate(word=word, definitions=[]))
    return candidates


def run_ocr_to_candidates(
    ocr: OcrPort,
    image_bytes: bytes,
    vision: VisionOcrPort | None = None,
) -> list[WordCandidate]:
    enhancer = vision or NoopVisionOcr()
    text = ocr.extract_text(image_bytes)
    text = enhancer.enhance_text(image_bytes, text)
    return candidates_from_ocr_text(text)
