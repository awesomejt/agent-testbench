import pytest
from src.api import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_health_returns_200(client):
    resp = client.get("/health")
    assert resp.status_code == 200


def test_health_body(client):
    resp = client.get("/health")
    assert resp.get_json() == {"status": "ok"}


def test_health_content_type(client):
    resp = client.get("/health")
    assert resp.content_type == "application/json"
