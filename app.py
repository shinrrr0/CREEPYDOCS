"""
CreepyDocs - Flask application entry point.

Composition root: wires config, database, blueprints, and CLI commands.
Keep this file thin - put logic in routes/, services/, repositories/,
models/.
"""

from pathlib import Path

from flask import Flask

from config import Config
from models.database import db
import models  # noqa: F401  - registers all model classes on db.metadata
from routes.main import main_bp
from routes.images import images_bp
from cli import register_cli


def create_app(config_class: type = Config) -> Flask:
    """Application factory. Use this so tests can build isolated app instances."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # SQLite (the default URI) lives in instance/. Make sure the folder
    # exists before SQLAlchemy tries to open the file.
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    # Database - call init_app once we have a config to bind to.
    db.init_app(app)

    # CLI: init-db, seed-db, reset-db.
    register_cli(app)

    # Blueprints. Add new ones here as the site grows
    # (e.g. auth_bp, admin_bp, api_bp).
    app.register_blueprint(main_bp)
    app.register_blueprint(images_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    # Debug=True is dev-only; remove for production.
    app.run(debug=True, host="127.0.0.1", port=5000)
