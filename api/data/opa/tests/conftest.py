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


@pytest.fixture(scope="function")
def app():
    with TestClient(main.start_api()) as client:
        yield client


@pytest.fixture(scope="function")
def app_c1(monkeypatch):
    monkeypatch.setenv('ENV', 'testing_1')
    with TestClient(main.start_api()) as client:
        yield client


@pytest.fixture(scope="function")
def app_c2(monkeypatch):
    monkeypatch.setenv('ENV', 'testing_2')
    with TestClient(main.start_api()) as client:
        yield client


@pytest.fixture(scope="function")
def app_dev(monkeypatch):
    monkeypatch.setenv('ENV', 'dev')
    with TestClient(main.start_api()) as client:
        yield client


@pytest.fixture(scope="function")
def app_examples(monkeypatch):
    monkeypatch.setenv('ENV', 'testing_examples')
    with TestClient(main.start_api()) as client:
        yield client
