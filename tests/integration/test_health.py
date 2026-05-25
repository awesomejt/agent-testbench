def test_health_status_200(client):
    resp = client.get("/health")
    assert resp.status_code == 200


def test_health_body_ok(client):
    resp = client.get("/health")
    assert resp.json() == {"status": "ok"}


def test_health_content_type(client):
    resp = client.get("/health")
    assert "application/json" in resp.headers["content-type"]
