from __future__ import annotations

import urllib.error
import urllib.request


class OllamaClient:
    """Ollama adapter stub: soft health check only; evaluate deferred to pronunciation plan."""

    def __init__(self, host: str) -> None:
        self._host = host.rstrip("/")

    def health_check(self) -> bool:
        url = f"{self._host}/api/tags"
        try:
            with urllib.request.urlopen(url, timeout=1.0) as resp:
                return 200 <= resp.status < 300
        except (OSError, urllib.error.URLError, ValueError):
            return False
