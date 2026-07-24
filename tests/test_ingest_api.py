from io import BytesIO

from fastapi.testclient import TestClient

from es_app.config import get_settings
from es_app.main import create_app


def test_ingest_file_and_confirm(data_dir, monkeypatch):
    monkeypatch.setenv("ES_DATA_DIR", str(data_dir))
    get_settings.cache_clear()
    client = TestClient(create_app())

    csv_body = (
        "word,phonetic,audio,definitions,examples\n"
        "imported,/ɪmˈpɔːrtɪd/,,导入词,An imported word.\n"
        ",bad,,,\n"
    )
    resp = client.post(
        "/ingest/file",
        files={"file": ("words.csv", BytesIO(csv_body.encode("utf-8")), "text/csv")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["candidates"]) == 1
    assert data["candidates"][0]["word"] == "imported"
    assert data["failures"]

    before = len(client.get("/lexicon/words").json())
    confirm = client.post("/ingest/confirm", json={"candidates": data["candidates"]})
    assert confirm.status_code == 200
    words = confirm.json()
    assert len(words) == 1
    assert words[0]["word"] == "imported"
    assert len(client.get("/lexicon/words").json()) == before + 1
