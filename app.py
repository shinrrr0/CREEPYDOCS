"""
CreepyDocs - Flask application entry point.

This is the composition root: it wires together config, blueprints, and
(eventually) database initialization. Keep this file thin - put logic in
routes/, services/, repositories/, models/.
"""

from flask import Flask

from config import Config
from routes.main import main_bp
from routes.gallery import gallery_bp  # лента изображений
from routes.blog import blog_bp  # блог посты


def create_app(config_class: type = Config) -> Flask:
    """Application factory. Use this so tests can build isolated app instances."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Register blueprints. Add new blueprints here as the site grows
    # (e.g. auth_bp, admin_bp, api_bp).
    app.register_blueprint(main_bp)
    app.register_blueprint(gallery_bp)  # /gallery route
    app.register_blueprint(blog_bp)     # /blog route

    # FUTURE: initialize SQLAlchemy here once models/database.py is wired up:
    #     from models.database import db
    #     db.init_app(app)

    return app


if __name__ == "__main__":
    app = create_app()
    # Debug=True is dev-only; remove for production.
    app.run(debug=True, host="127.0.0.1", port=5000)
