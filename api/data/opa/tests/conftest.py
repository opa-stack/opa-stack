import sys
import pytest
from starlette.testclient import TestClient

from opa import main

original_path = sys.path.copy()


@pytest.fixture(autouse=True)
def fix_syspath():
    """
    We are modifying sys.path when handling plugins.
    This might bleed over to other test-envs (the ENV we monkeypatch below).
    We need a fresh sys.path for the different env's if we want to test them in
    a good way.
    """
    sys.path = original_path


"""
Different app configurations below this point..

If we use with-blocks, we allow FastAPI to run startup/shutdown events, ie, it connects
to available databases and does some extra work. We do that on some tests, but only when
needed.
"""


@pytest.fixture(scope="function")
def app():
    yield TestClient(main.get_app())


@pytest.fixture(scope="function")
def app_c1(monkeypatch):
    monkeypatch.setenv('ENV', 'testing_1')
    yield TestClient(main.get_app())


@pytest.fixture(scope="function")
def app_c2(monkeypatch):
    monkeypatch.setenv('ENV', 'testing_2')
    yield TestClient(main.get_app())


@pytest.fixture(scope="function")
def app_dev(monkeypatch):
    monkeypatch.setenv('ENV', 'dev')
    yield TestClient(main.get_app())


@pytest.fixture(scope="function")
def app_examples(monkeypatch):
    monkeypatch.setenv('ENV', 'testing_examples')
    with TestClient(main.get_app()) as client:
        yield client
