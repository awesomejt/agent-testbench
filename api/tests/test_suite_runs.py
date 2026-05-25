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
        "suite_name": "math-exam",
        "run_label": "run-1",
        "model_name": "gpt-4o",
        "provider": "openai",
        "agent_server": None,
        "total_scenarios": 5,
        "passed": 4,
        "failed": 1,
        "partial": 0,
        "error_count": 0,
        "avg_score": Decimal("0.88"),
        "total_cost_usd": Decimal("0.00210000"),
        "total_time": 42.5,
        "start_datetime": now,
        "end_datetime": now,
        "created_at": now,
    }
    row.update(overrides)
    return row


VALID_PAYLOAD = {
    "suite_name": "math-exam",
    "run_label": "run-1",
    "model_name": "gpt-4o",
    "provider": "openai",
    "start_datetime": "2026-01-01T00:00:00+00:00",
}


# ── POST /suite-runs/ ─────────────────────────────────────────────────────────

@patch("src.api.routes.suite_runs.get_connection")
def test_create_suite_run_returns_201(mock_gc, client):
    mock_gc.return_value = _make_db_mock(fetchone=_sample_row())
    assert client.post("/suite-runs/", json=VALID_PAYLOAD).status_code == 201


@patch("src.api.routes.suite_runs.get_connection")
def test_create_suite_run_returns_row(mock_gc, client):
    mock_gc.return_value = _make_db_mock(fetchone=_sample_row())
    data = client.post("/suite-runs/", json=VALID_PAYLOAD).get_json()
    assert data["id"] == 1
    assert data["suite_name"] == "math-exam"


@patch("src.api.routes.suite_runs.get_connection")
def test_create_suite_run_serializes_decimal(mock_gc, client):
    mock_gc.return_value = _make_db_mock(fetchone=_sample_row())
    data = client.post("/suite-runs/", json=VALID_PAYLOAD).get_json()
    assert isinstance(data["avg_score"], float)
    assert isinstance(data["total_cost_usd"], float)


def test_create_suite_run_missing_fields(client):
    resp = client.post("/suite-runs/", json={"suite_name": "math-exam"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_create_suite_run_empty_body(client):
    assert client.post("/suite-runs/", json={}).status_code == 400


# ── GET /suite-runs/ ──────────────────────────────────────────────────────────

@patch("src.api.routes.suite_runs.get_connection")
def test_list_suite_runs_returns_200(mock_gc, client):
    mock_gc.return_value = _make_db_mock(fetchall=[])
    assert client.get("/suite-runs/").status_code == 200


@patch("src.api.routes.suite_runs.get_connection")
def test_list_suite_runs_returns_list(mock_gc, client):
    mock_gc.return_value = _make_db_mock(fetchall=[_sample_row()])
    data = client.get("/suite-runs/").get_json()
    assert isinstance(data, list)
    assert len(data) == 1


@patch("src.api.routes.suite_runs.get_connection")
def test_list_suite_runs_filters_accepted(mock_gc, client):
    mock_gc.return_value = _make_db_mock(fetchall=[])
    resp = client.get("/suite-runs/?suite=math-exam&model=gpt-4o")
    assert resp.status_code == 200


# ── PUT /suite-runs/{id}/finalize ─────────────────────────────────────────────

@patch("src.api.routes.suite_runs.get_connection")
def test_finalize_suite_run_returns_200(mock_gc, client):
    mock_gc.return_value = _make_db_mock(fetchone=_sample_row())
    assert client.put("/suite-runs/1/finalize").status_code == 200


@patch("src.api.routes.suite_runs.get_connection")
def test_finalize_suite_run_returns_aggregates(mock_gc, client):
    mock_gc.return_value = _make_db_mock(fetchone=_sample_row(passed=4, failed=1))
    data = client.put("/suite-runs/1/finalize").get_json()
    assert data["passed"] == 4
    assert data["failed"] == 1


@patch("src.api.routes.suite_runs.get_connection")
def test_finalize_suite_run_not_found_returns_404(mock_gc, client):
    mock_gc.return_value = _make_db_mock(fetchone=None)
    assert client.put("/suite-runs/999/finalize").status_code == 404
