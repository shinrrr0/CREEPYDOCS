"""
Flask CLI commands.

Wired into the app via `register_cli(app)` in app.py. After exporting
`FLASK_APP=app`, the dev workflow is:

    flask init-db        # create tables (idempotent)
    flask seed-db        # insert sample stories (idempotent)
    flask seed-db --force  # replace fixtures with matching titles
    flask reset-db       # drop everything, recreate, re-seed (destructive)

For real-world schema migrations beyond drop/recreate, add Flask-Migrate
(Alembic) - see README for the recipe.
"""

import click
from flask import Flask
from flask.cli import with_appcontext

from models.database import db
from services.seeder import seed_database


@click.command("init-db")
@with_appcontext
def init_db_cmd():
    """Create all tables. Existing tables are left intact."""
    db.create_all()
    click.echo("Tables created.")


@click.command("seed-db")
@click.option(
    "--force",
    is_flag=True,
    help="Replace fixtures with matching titles (destructive for those rows).",
)
@with_appcontext
def seed_db_cmd(force: bool):
    """Insert fixture stories. Idempotent unless --force is set."""
    n = seed_database(force=force)
    click.echo(f"Inserted {n} stories.")


@click.command("reset-db")
@with_appcontext
def reset_db_cmd():
    """Drop all tables, recreate, and re-seed. Destructive."""
    db.drop_all()
    db.create_all()
    n = seed_database()
    click.echo(f"DB reset; inserted {n} stories.")


def register_cli(app: Flask) -> None:
    """Wire CLI commands into the Flask app."""
    app.cli.add_command(init_db_cmd)
    app.cli.add_command(seed_db_cmd)
    app.cli.add_command(reset_db_cmd)
