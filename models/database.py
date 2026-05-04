"""
SQLAlchemy database instance.

Single source of truth for the `db` object. Models inherit from
`db.Model`; the Flask factory calls `db.init_app(app)` to bind it to
the active app config.

We use the SQLAlchemy 2.x style with a typed DeclarativeBase so models
get proper type hints (`Mapped[str]`, `mapped_column`, ...).
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Project-wide declarative base.

    Add cross-model defaults here later (e.g. naming conventions for
    indexes/constraints, soft-delete mixins, automatic `updated_at`).
    """


db = SQLAlchemy(model_class=Base)
