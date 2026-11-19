"""Tests for MongoDB connection URI configuration."""

import importlib
from unittest.mock import MagicMock

import mongo_db


def _reload(monkeypatch, uri):
    """Reload mongo_db with MONGODB_URI set to ``uri`` (unset if None) and return the host passed to MongoClient."""
    seen = {}

    def fake_client(host, *args, **kwargs):
        """Record the connection host instead of opening a real connection."""
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
    """MONGODB_URI from the environment is used for the client."""
    assert _reload(monkeypatch, "mongodb://db.example.com:27017") == "mongodb://db.example.com:27017"


def test_client_defaults_to_localhost(monkeypatch):
    """Without MONGODB_URI the client falls back to localhost."""
    assert _reload(monkeypatch, None) == "mongodb://localhost:27017"


def teardown_module():
    """Restore mongo_db to its real configuration for other tests."""
    importlib.reload(mongo_db)
