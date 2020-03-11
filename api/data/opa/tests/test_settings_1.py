import pytest
from starlette.testclient import TestClient

from opa import main


@pytest.fixture(scope="function")
def test_app(monkeypatch):
    monkeypatch.setenv('ENV', 'testing_1')
    client = TestClient(main.get_app())
    yield client


def test_name(test_app):
    response = test_app.get("/openapi.json")
    assert response.json()['info']['title'] == 'testing-1'
