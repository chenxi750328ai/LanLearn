from typing import Protocol


class OcrPort(Protocol):
    def extract_text(self, image_bytes: bytes) -> str: ...


class VisionOcrPort(Protocol):
    def enhance_text(self, image_bytes: bytes, base_text: str) -> str: ...


class NoopVisionOcr:
    def enhance_text(self, image_bytes: bytes, base_text: str) -> str:
        return base_text
