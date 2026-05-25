import decimal
from flask import Blueprint, request, jsonify
from ..db import get_connection

bp = Blueprint("runs", __name__, url_prefix="/runs")

REQUIRED = {"run_name", "scenario_name", "model_name", "provider",
            "start_datetime", "end_datetime", "total_time"}

GRADING_FIELDS = {"pass_fail", "score", "grader_model", "grader_rationale", "suite_run_id"}


@bp.post("/")
def create_run():
    data = request.get_json(force=True) or {}
    missing = REQUIRED - data.keys()
    if missing:
        return jsonify({"error": f"missing fields: {', '.join(sorted(missing))}"}), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO runs (
                    run_name, scenario_name, model_name, provider, agent_server,
                    start_datetime, end_datetime, total_time, tokens_per_second,
                    follow_up_prompts, input_tokens, output_tokens, total_tokens,
                    cost_usd, pass_fail, score, error, error_message,
                    grader_model, grader_rationale, suite_run_id
                ) VALUES (
                    %(run_name)s, %(scenario_name)s, %(model_name)s, %(provider)s,
                    %(agent_server)s, %(start_datetime)s, %(end_datetime)s,
                    %(total_time)s, %(tokens_per_second)s, %(follow_up_prompts)s,
                    %(input_tokens)s, %(output_tokens)s, %(total_tokens)s,
                    %(cost_usd)s, %(pass_fail)s, %(score)s, %(error)s, %(error_message)s,
                    %(grader_model)s, %(grader_rationale)s, %(suite_run_id)s
                ) RETURNING *
                """,
                {
                    "run_name":          data["run_name"],
                    "scenario_name":     data["scenario_name"],
                    "model_name":        data["model_name"],
                    "provider":          data["provider"],
                    "agent_server":      data.get("agent_server"),
                    "start_datetime":    data["start_datetime"],
                    "end_datetime":      data["end_datetime"],
                    "total_time":        data["total_time"],
                    "tokens_per_second": data.get("tokens_per_second"),
                    "follow_up_prompts": data.get("follow_up_prompts", 0),
                    "input_tokens":      data.get("input_tokens", 0),
                    "output_tokens":     data.get("output_tokens", 0),
                    "total_tokens":      data.get("total_tokens", 0),
                    "cost_usd":          data.get("cost_usd"),
                    "pass_fail":         data.get("pass_fail"),
                    "score":             data.get("score"),
                    "error":             data.get("error", False),
                    "error_message":     data.get("error_message"),
                    "grader_model":      data.get("grader_model"),
                    "grader_rationale":  data.get("grader_rationale"),
                    "suite_run_id":      data.get("suite_run_id"),
                },
            )
            row = cur.fetchone()

    return jsonify(_serialize(row)), 201


@bp.get("/")
def list_runs():
    conditions, params = [], {}

    if s := request.args.get("scenario"):
        conditions.append("scenario_name = %(scenario)s")
        params["scenario"] = s
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
                f"SELECT * FROM runs {where} ORDER BY start_datetime DESC LIMIT 500",
                params,
            )
            rows = cur.fetchall()

    return jsonify([_serialize(r) for r in rows])


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
