import pytest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch
from src.api import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _make_db_mock(fetchone=None, fetchall=None):
    cur = MagicMock()
    cur.__enter__.return_value = cur
    cur.fetchone.return_value = fetchone
    cur.fetchall.return_value = fetchall or []

    conn = MagicMock()
    conn.__enter__.return_value = conn
    conn.cursor.return_value = cur
    return conn


def _sample_row(**overrides):
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    row = {
        "id": 1,
        "run_name": "r1",
        "scenario_name": "s1",
        "model_name": "m1",
        "provider": "p1",
        "agent_server": None,
        "start_datetime": now,
        "end_datetime": datetime(2026, 1, 1, 0, 0, 10, tzinfo=timezone.utc),
        "total_time": 10.0,
        "tokens_per_second": 20.0,
        "follow_up_prompts": 0,
        "input_tokens": 100,
        "output_tokens": 200,
        "total_tokens": 300,
        "cost_usd": Decimal("0.00042000"),
        "pass_fail": None,
        "score": None,
        "error": False,
        "error_message": None,
        "created_at": now,
    }
    row.update(overrides)
    return row


VALID_PAYLOAD = {
    "run_name": "r1",
    "scenario_name": "s1",
    "model_name": "m1",
    "provider": "p1",
    "start_datetime": "2026-01-01T00:00:00+00:00",
    "end_datetime": "2026-01-01T00:00:10+00:00",
    "total_time": 10.0,
}


# ── POST /runs/ ───────────────────────────────────────────────────────────────

@patch("src.api.routes.runs.get_connection")
def test_create_run_returns_201(mock_gc, client):
    mock_gc.return_value = _make_db_mock(fetchone=_sample_row())
    resp = client.post("/runs/", json=VALID_PAYLOAD)
    assert resp.status_code == 201


@patch("src.api.routes.runs.get_connection")
def test_create_run_returns_db_row(mock_gc, client):
    mock_gc.return_value = _make_db_mock(fetchone=_sample_row())
    resp = client.post("/runs/", json=VALID_PAYLOAD)
    data = resp.get_json()
    assert data["id"] == 1
    assert data["run_name"] == "r1"
    assert data["scenario_name"] == "s1"


@patch("src.api.routes.runs.get_connection")
def test_create_run_serializes_datetime(mock_gc, client):
    mock_gc.return_value = _make_db_mock(fetchone=_sample_row())
    data = client.post("/runs/", json=VALID_PAYLOAD).get_json()
    assert isinstance(data["start_datetime"], str)
    assert "2026" in data["start_datetime"]


@patch("src.api.routes.runs.get_connection")
def test_create_run_serializes_decimal(mock_gc, client):
    mock_gc.return_value = _make_db_mock(fetchone=_sample_row())
    data = client.post("/runs/", json=VALID_PAYLOAD).get_json()
    assert isinstance(data["cost_usd"], float)


@patch("src.api.routes.runs.get_connection")
def test_create_run_content_type(mock_gc, client):
    mock_gc.return_value = _make_db_mock(fetchone=_sample_row())
    resp = client.post("/runs/", json=VALID_PAYLOAD)
    assert "application/json" in resp.content_type


def test_create_run_missing_required_fields(client):
    resp = client.post("/runs/", json={"run_name": "r1"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_create_run_empty_body(client):
    resp = client.post("/runs/", json={})
    assert resp.status_code == 400


def test_create_run_non_json_body(client):
    resp = client.post("/runs/", data="not-json", content_type="text/plain")
    assert resp.status_code == 400


# ── GET /runs/ ────────────────────────────────────────────────────────────────

@patch("src.api.routes.runs.get_connection")
def test_list_runs_returns_200(mock_gc, client):
    mock_gc.return_value = _make_db_mock(fetchall=[])
    assert client.get("/runs/").status_code == 200


@patch("src.api.routes.runs.get_connection")
def test_list_runs_returns_list(mock_gc, client):
    mock_gc.return_value = _make_db_mock(fetchall=[_sample_row()])
    data = client.get("/runs/").get_json()
    assert isinstance(data, list)
    assert len(data) == 1


@patch("src.api.routes.runs.get_connection")
def test_list_runs_content_type(mock_gc, client):
    mock_gc.return_value = _make_db_mock(fetchall=[])
    assert "application/json" in client.get("/runs/").content_type


@patch("src.api.routes.runs.get_connection")
def test_list_runs_filters_accepted(mock_gc, client):
    mock_gc.return_value = _make_db_mock(fetchall=[])
    resp = client.get("/runs/?scenario=hello-world&model=gpt-4o&provider=openai")
    assert resp.status_code == 200


@patch("src.api.routes.runs.get_connection")
def test_list_runs_date_filters_accepted(mock_gc, client):
    mock_gc.return_value = _make_db_mock(fetchall=[])
    resp = client.get("/runs/?from=2026-01-01&to=2026-12-31")
    assert resp.status_code == 200
