import pytest

VALID_RUN = {
    "run_name": "integration-test",
    "scenario_name": "hello-world",
    "model_name": "test-model",
    "provider": "test",
}


def test_list_runs_200(client):
    resp = client.get("/runs/")
    assert resp.status_code == 200


def test_list_runs_returns_list(client):
    resp = client.get("/runs/")
    assert isinstance(resp.json(), list)


def test_create_run_201(client):
    resp = client.post("/runs/", json=VALID_RUN)
    assert resp.status_code == 201


def test_create_run_persists(client):
    resp = client.post("/runs/", json={**VALID_RUN, "run_name": "persist-check"})
    assert resp.status_code == 201
    body = resp.json()
    assert body.get("run_name") == "persist-check"


def test_create_run_roundtrip_fields(client):
    payload = {**VALID_RUN, "model_name": "roundtrip-model", "provider": "roundtrip"}
    resp = client.post("/runs/", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["model_name"] == "roundtrip-model"
    assert body["provider"] == "roundtrip"
