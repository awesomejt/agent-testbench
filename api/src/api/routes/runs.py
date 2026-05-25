from flask import Blueprint, request, jsonify

bp = Blueprint("runs", __name__, url_prefix="/runs")


@bp.post("/")
def create_run():
    data = request.get_json(force=True)
    # TODO: validate, persist to DB, return created record
    return jsonify(data), 201


@bp.get("/")
def list_runs():
    # TODO: query DB with filters (scenario, model, date range)
    return jsonify([])
