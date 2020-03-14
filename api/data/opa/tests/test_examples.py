import secrets


def test_urls(app_examples):
    response = app_examples.get("/time")
    assert response.status_code == 200


def test_redis(app_examples):
    suffix = secrets.token_urlsafe(6)
    for i in ['sync', 'async']:
        response = app_examples.get(f'/counter-{i}?key=test-{i}-{suffix}')
        assert response.text == '"Counter is 1"'
