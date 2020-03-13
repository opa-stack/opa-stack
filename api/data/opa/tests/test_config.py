import sys


def test_name_1(app_c1):
    response = app_c1.get("/openapi.json")
    assert response.json()['info']['title'] == 'testing-1'


def test_plugin_1(app_c1):
    assert '/data/opa/plugins' in sys.path
    assert '/data/opa/demo-plugins' not in sys.path
    assert '/data/opa/tests/plugins/config_1-a' in sys.path
    assert '/data/opa/tests/plugins/config_1-b' in sys.path
    assert '/data/opa/tests/plugins/config_2-b' not in sys.path


def test_name_2(app_c2):
    response = app_c2.get("/openapi.json")
    assert response.json()['info']['title'] == 'testing-2'


def test_plugin_2(app_c2):
    assert '/data/opa/plugins' in sys.path
    assert '/data/opa/demo-plugins' not in sys.path
    assert '/data/opa/tests/plugins/config_1-a' not in sys.path
    assert '/data/opa/tests/plugins/config_2-a' not in sys.path
    assert '/data/opa/tests/plugins/config_2-b' in sys.path
