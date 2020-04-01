import pytest
from starlette.testclient import TestClient

from socket import gaierror
from pymongo.errors import OperationFailure
from redis.exceptions import ConnectionError

from opa import main
from opa.utils import redis


def test_bogus_mongo(monkeypatch):
    monkeypatch.setenv('ENV', 'testing_optional_components_mongo_bogus')

    with pytest.raises(OperationFailure, match=r".*Authentication failed.*"):
        with TestClient(main.start_app()):
            pass


def test_bogus_redis(monkeypatch):
    monkeypatch.setenv('ENV', 'testing_optional_components_redis_bogus')

    with pytest.raises(
        ConnectionError,
        match=r".*Error 111 connecting to mongo:6379. Connection refused.*",
    ):
        with TestClient(main.start_app()):
            pass


def test_nonexist_redis_auto(monkeypatch):
    monkeypatch.setenv('ENV', 'testing_optional_components_redis_nonexisting_auto')

    with TestClient(main.start_app()):
        pass


def test_nonexist_redis_required(monkeypatch):
    monkeypatch.setenv('ENV', 'testing_optional_components_redis_nonexisting_required')

    with pytest.raises(Exception, match=r".*Connect pre-check failed for.*"):
        with TestClient(main.start_app()):
            pass
