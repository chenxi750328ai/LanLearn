from pathlib import Path
from es_app.config import get_settings
from es_app.db import get_connection, init_db


def test_settings_respect_env(monkeypatch, tmp_path):
    monkeypatch.setenv("ES_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    get_settings.cache_clear()
    s = get_settings()
    assert s.data_dir == tmp_path
    assert s.ollama_host == "http://127.0.0.1:11434"


def test_settings_bind_host(monkeypatch, tmp_path):
    monkeypatch.setenv("ES_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("ES_BIND", "0.0.0.0")
    get_settings.cache_clear()
    s = get_settings()
    assert s.bind_host == "0.0.0.0"


def test_init_db_creates_words_table(tmp_path):
    conn = get_connection(tmp_path)
    init_db(conn)
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='words'"
    ).fetchall()
    assert [tuple(r) for r in rows] == [("words",)]


def test_init_db_creates_session_tables(tmp_path):
    conn = get_connection(tmp_path)
    init_db(conn)
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name IN ('study_sessions', 'exam_sessions') ORDER BY name"
    ).fetchall()
    assert [tuple(r) for r in rows] == [("exam_sessions",), ("study_sessions",)]
