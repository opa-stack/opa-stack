import pytest
from starlette.testclient import TestClient

from .. import main


@pytest.fixture(scope="function")
def test_app():
    client = TestClient(main.get_app())
    yield client


def test_404(test_app):
    response = test_app.get("/404")
    assert response.status_code == 404
