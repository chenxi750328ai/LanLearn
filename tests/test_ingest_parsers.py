from pathlib import Path

from es_app.ingest.parsers import parse_csv, parse_txt

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_csv_partial_success():
    text = (FIXTURES / "words_sample.csv").read_text(encoding="utf-8")
    ok, failures = parse_csv(text)
    assert any(c.word == "diligent" for c in ok)
    assert failures  # 含空 word 行


def test_parse_txt():
    text = (FIXTURES / "words_sample.txt").read_text(encoding="utf-8")
    ok, failures = parse_txt(text)
    assert len(ok) >= 1
