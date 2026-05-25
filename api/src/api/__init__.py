from flask import Flask
from .routes import runs

def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(runs.bp)
    return app
