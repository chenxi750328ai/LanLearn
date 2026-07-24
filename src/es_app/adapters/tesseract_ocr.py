from io import BytesIO

try:
    import pytesseract
    from PIL import Image
except ImportError:  # pragma: no cover - exercised when deps missing
    pytesseract = None  # type: ignore[assignment,misc]
    Image = None  # type: ignore[assignment,misc]


def tesseract_available() -> bool:
    return pytesseract is not None and Image is not None


class TesseractOcr:
    """Tesseract-backed OCR. Requires pytesseract and Pillow; otherwise use FakeOcr."""

    def extract_text(self, image_bytes: bytes) -> str:
        if not tesseract_available():
            raise RuntimeError(
                "pytesseract/Pillow not installed; use FakeOcr for tests or install OCR deps"
            )
        img = Image.open(BytesIO(image_bytes))
        return pytesseract.image_to_string(img)
