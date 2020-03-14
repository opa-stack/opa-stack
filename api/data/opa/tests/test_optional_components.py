import pytest
from starlette.testclient import TestClient

from socket import gaierror
from pymongo.errors import OperationFailure

from opa import main
from opa.utils import redis


def test_bogus_mongo(monkeypatch):
    monkeypatch.setenv('ENV', 'testing_optional_components_mongo_bogus')

    with pytest.raises(OperationFailure, match=r".*Authentication failed.*"):
        with TestClient(main.get_app()):
            pass


def test_bogus_redis(monkeypatch):
    monkeypatch.setenv('ENV', 'testing_optional_components_redis_bogus')

    with pytest.raises(ConnectionRefusedError, match=r".*Connect call failed.*"):
        with TestClient(main.get_app()):
            pass


def test_nonexist_redis_auto(monkeypatch):
    monkeypatch.setenv('ENV', 'testing_optional_components_redis_nonexisting_auto')

    with TestClient(main.get_app()):
        pass


def test_nonexist_redis_required(monkeypatch):
    monkeypatch.setenv('ENV', 'testing_optional_components_redis_nonexisting_required')

    with pytest.raises(gaierror, match=r".*Name or service not known.*"):
        with TestClient(main.get_app()):
            pass
