import importlib
from unittest.mock import MagicMock

import mongo_db


def _reload(monkeypatch, uri):
    seen = {}

    def fake_client(host, *args, **kwargs):
        seen["host"] = host
        return MagicMock()

    monkeypatch.setattr("dotenv.load_dotenv", lambda *args, **kwargs: False)
    monkeypatch.setattr("pymongo.MongoClient", fake_client)
    if uri is None:
        monkeypatch.delenv("MONGODB_URI", raising=False)
    else:
        monkeypatch.setenv("MONGODB_URI", uri)
    importlib.reload(mongo_db)
    return seen["host"]


def test_client_uses_mongodb_uri_from_environment(monkeypatch):
    assert _reload(monkeypatch, "mongodb://db.example.com:27017") == "mongodb://db.example.com:27017"


def test_client_defaults_to_localhost(monkeypatch):
    assert _reload(monkeypatch, None) == "mongodb://localhost:27017"


def teardown_module():
    importlib.reload(mongo_db)
