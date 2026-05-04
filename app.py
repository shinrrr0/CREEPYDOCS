"""
CreepyDocs - Flask application entry point.

Composition root: wires config, database, blueprints, and CLI commands.
Keep this file thin - put logic in routes/, services/, repositories/,
models/.
"""

import os
import subprocess
import sys
from pathlib import Path

from flask import Flask

from config import Config
from models.database import db
import models  # noqa: F401  - registers all model classes on db.metadata
from routes.main import main_bp
from routes.gallery import gallery_bp
from routes.blog import blog_bp
from routes.images import images_bp
from cli import register_cli


_PROJECT_DIR = Path(__file__).resolve().parent


def create_app(config_class: type = Config) -> Flask:
    """Application factory. Use this so tests can build isolated app instances."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # SQLite (the default URI) lives in instance/. Make sure the folder
    # exists before SQLAlchemy tries to open the file.
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    # Database - bind to the active app config.
    db.init_app(app)

    # Auto-create tables on first startup so `python app.py` works
    # without a separate `flask init-db` step. Idempotent: existing
    # tables are left intact. For production migrations use Alembic /
    # Flask-Migrate instead.
    with app.app_context():
        db.create_all()

    # CLI: init-db, seed-db, reset-db, add-story, add-gallery-image,
    # list-stories, delete-story, import-prefabs.
    register_cli(app)

    # Blueprints. Add new ones here as the site grows
    # (e.g. auth_bp, admin_bp, api_bp).
    app.register_blueprint(main_bp)
    app.register_blueprint(gallery_bp)   # /gallery
    app.register_blueprint(blog_bp)      # /blog/* + /api/blog/*
    app.register_blueprint(images_bp)    # /image/<id>

    return app


# =====================================================================
# Prefab auto-import on dev-server startup
# =====================================================================

def _run_prefab_import_batch() -> None:
    """Invoke import_prefabs.bat sitting next to this file.

    The batch file activates the venv and runs `flask import-prefabs`
    which is idempotent, so calling it on every restart is safe.

    Notes:
      - The batch sets CREEPYDOCS_AUTOIMPORT_RUNNING=1 before invoking
        flask, which is how we avoid recursion: we only launch the
        batch when that variable is NOT set.
      - On non-Windows hosts there is no .bat to run; we silently fall
        back to calling the importer in-process so the convenience is
        not Windows-only.
    """
    # Recursion guard - the batch script itself sets this.
    if os.environ.get("CREEPYDOCS_AUTOIMPORT_RUNNING") == "1":
        return

    bat_path = _PROJECT_DIR / "import_prefabs.bat"

    if sys.platform.startswith("win") and bat_path.is_file():
        try:
            print(f"[creepydocs] running {bat_path.name} ...")
            subprocess.run(
                [str(bat_path)],
                cwd=str(_PROJECT_DIR),
                check=False,
                shell=False,
                timeout=120,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            print(f"[creepydocs] prefab import skipped: {exc}")
        return

    # Non-Windows fallback: import directly so the feature still works
    # on macOS / Linux dev machines.
    try:
        from services.prefab_importer import import_all_prefabs
        app = create_app()
        with app.app_context():
            result = import_all_prefabs(verbose=True)
        print(
            f"[creepydocs] prefabs imported: "
            f"{result['stories']} stories, "
            f"{result['gallery_images']} gallery images."
        )
    except Exception as exc:  # noqa: BLE001 - never crash the dev server
        print(f"[creepydocs] prefab import skipped: {exc}")


if __name__ == "__main__":
    # Werkzeug's debug reloader spawns a child process; we run the
    # prefab import in that child (WERKZEUG_RUN_MAIN=true) so it fires
    # exactly once per restart instead of on every reloader spawn.
    # In non-debug mode WERKZEUG_RUN_MAIN is absent and we run anyway.
    debug_mode = True
    is_reloader_child = os.environ.get("WERKZEUG_RUN_MAIN") == "true"
    if is_reloader_child or not debug_mode:
        _run_prefab_import_batch()

    app = create_app()
    # Debug=True is dev-only; remove for production.
    app.run(debug=debug_mode, host="127.0.0.1", port=5000)
