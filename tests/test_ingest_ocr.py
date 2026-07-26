from io import BytesIO

from fastapi.testclient import TestClient

from es_app.adapters.fake_ocr import FakeOcr
from es_app.adapters.protocols import NoopVisionOcr
from es_app.config import get_settings
from es_app.db import get_connection, init_db
from es_app.ingest.ocr_pipeline import candidates_from_ocr_text, run_ocr_to_candidates
from es_app.ingest.router import get_ingest_service
from es_app.ingest.service import IngestService
from es_app.lexicon.service import LexiconService
from es_app.lexicon.store import LexiconStore
from es_app.main import create_app


def test_fake_ocr_to_candidates():
    ocr = FakeOcr(text="abandon\nbenefit\n")
    cands = run_ocr_to_candidates(ocr, b"fake")
    assert {c.word for c in cands} == {"abandon", "benefit"}
    assert all(c.definitions == [] for c in cands)


def test_candidates_from_ocr_text_splits_whitespace():
    cands = candidates_from_ocr_text("alpha  beta\ngamma")
    assert [c.word for c in cands] == ["alpha", "beta", "gamma"]
    assert all(c.definitions == [] for c in cands)


def test_noop_vision_ocr_passthrough():
    vision = NoopVisionOcr()
    assert vision.enhance_text(b"x", "hello") == "hello"


def test_ingest_image_api(data_dir, monkeypatch):
    monkeypatch.setenv("ES_DATA_DIR", str(data_dir))
    get_settings.cache_clear()

    conn = get_connection(data_dir)
    init_db(conn)
    lexicon = LexiconService(LexiconStore(conn))
    ingest = IngestService(lexicon, ocr=FakeOcr(text="ocrword\nanother\n"))

    app = create_app()
    app.dependency_overrides[get_ingest_service] = lambda: ingest
    client = TestClient(app)

    resp = client.post(
        "/ingest/image",
        files={"file": ("sample.png", BytesIO(b"fake-image"), "image/png")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert {c["word"] for c in data["candidates"]} == {"ocrword", "another"}
    assert all(c["definitions"] == [] for c in data["candidates"])
