class FakeOcr:
    """Deterministic OCR for tests and environments without Tesseract."""

    def __init__(self, text: str = ""):
        self._text = text

    def extract_text(self, image_bytes: bytes) -> str:
        return self._text
