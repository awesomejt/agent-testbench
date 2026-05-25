import pytest
from src.api import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_create_run_returns_201(client):
    resp = client.post("/runs/", json={"run_name": "smoke", "scenario_name": "test"})
    assert resp.status_code == 201


def test_list_runs_returns_empty(client):
    resp = client.get("/runs/")
    assert resp.status_code == 200
    assert resp.get_json() == []
