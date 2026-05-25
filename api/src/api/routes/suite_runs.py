import decimal
from flask import Blueprint, request, jsonify
from ..db import get_connection

bp = Blueprint("suite_runs", __name__, url_prefix="/suite-runs")

REQUIRED = {"suite_name", "run_label", "model_name", "provider", "start_datetime"}


@bp.post("/")
def create_suite_run():
    data = request.get_json(force=True) or {}
    missing = REQUIRED - data.keys()
    if missing:
        return jsonify({"error": f"missing fields: {', '.join(sorted(missing))}"}), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO suite_runs (
                    suite_name, run_label, model_name, provider, agent_server,
                    start_datetime
                ) VALUES (
                    %(suite_name)s, %(run_label)s, %(model_name)s, %(provider)s,
                    %(agent_server)s, %(start_datetime)s
                ) RETURNING *
                """,
                {
                    "suite_name":    data["suite_name"],
                    "run_label":     data["run_label"],
                    "model_name":    data["model_name"],
                    "provider":      data["provider"],
                    "agent_server":  data.get("agent_server"),
                    "start_datetime": data["start_datetime"],
                },
            )
            row = cur.fetchone()

    return jsonify(_serialize(row)), 201


@bp.get("/")
def list_suite_runs():
    conditions, params = [], {}

    if s := request.args.get("suite"):
        conditions.append("suite_name = %(suite)s")
        params["suite"] = s
    if m := request.args.get("model"):
        conditions.append("model_name = %(model)s")
        params["model"] = m
    if p := request.args.get("provider"):
        conditions.append("provider = %(provider)s")
        params["provider"] = p
    if f := request.args.get("from"):
        conditions.append("start_datetime >= %(from_dt)s")
        params["from_dt"] = f
    if t := request.args.get("to"):
        conditions.append("start_datetime <= %(to_dt)s")
        params["to_dt"] = t

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM suite_runs {where} ORDER BY start_datetime DESC LIMIT 200",
                params,
            )
            rows = cur.fetchall()

    return jsonify([_serialize(r) for r in rows])


@bp.put("/<int:suite_run_id>/finalize")
def finalize_suite_run(suite_run_id: int):
    """Compute aggregates from child runs and update the suite_run record."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE suite_runs sr
                SET
                    total_scenarios = agg.total,
                    passed          = agg.passed,
                    failed          = agg.failed,
                    partial         = agg.partial,
                    error_count     = agg.errors,
                    avg_score       = agg.avg_score,
                    total_cost_usd  = agg.total_cost,
                    total_time      = agg.total_time,
                    end_datetime    = NOW()
                FROM (
                    SELECT
                        COUNT(*)                                          AS total,
                        COUNT(*) FILTER (WHERE pass_fail = 'pass')        AS passed,
                        COUNT(*) FILTER (WHERE pass_fail = 'fail')        AS failed,
                        COUNT(*) FILTER (WHERE pass_fail = 'partial')     AS partial,
                        COUNT(*) FILTER (WHERE pass_fail = 'error'
                                            OR error = TRUE)              AS errors,
                        AVG(score)                                        AS avg_score,
                        SUM(cost_usd)                                     AS total_cost,
                        SUM(total_time)                                   AS total_time
                    FROM runs
                    WHERE suite_run_id = %(id)s
                ) agg
                WHERE sr.id = %(id)s
                RETURNING sr.*
                """,
                {"id": suite_run_id},
            )
            row = cur.fetchone()

    if row is None:
        return jsonify({"error": "suite run not found"}), 404

    return jsonify(_serialize(row))


def _serialize(row: dict) -> dict:
    result = {}
    for k, v in row.items():
        if hasattr(v, "isoformat"):
            result[k] = v.isoformat()
        elif isinstance(v, decimal.Decimal):
            result[k] = float(v)
        else:
            result[k] = v
    return result
