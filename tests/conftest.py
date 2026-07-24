import pytest
from es_app.db import get_connection, init_db
from es_app.config import get_settings


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ES_DATA_DIR", str(tmp_path))
    get_settings.cache_clear()
    return tmp_path


@pytest.fixture
def conn(data_dir):
    c = get_connection(data_dir)
    init_db(c)
    yield c
    c.close()
