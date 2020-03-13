import sys


def test_config(app_dev):
    assert '/data/opa/demo-plugins' in sys.path


def test_urls(app_dev):
    response = app_dev.get("/demo-requestdata")
    assert response.status_code == 200


def test_import(app_dev):
    from demo_util import double

    assert double(2) == 4
