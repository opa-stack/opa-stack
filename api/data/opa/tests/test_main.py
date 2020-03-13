def test_404(app):
    response = app.get("/404")
    assert response.status_code == 404
