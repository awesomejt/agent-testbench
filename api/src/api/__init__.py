from flask import Flask
from .routes import health, runs


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(health.bp)
    app.register_blueprint(runs.bp)
    return app
