"""
Domain models package.

Importing this module is what registers all model classes on the
shared `db.metadata`. Anything that calls `db.create_all()` or
`db.drop_all()` must import this first (or import the individual model
modules) so SQLAlchemy knows the tables exist.

Single tidy entrypoint:
    from models import Story, Image, db
"""

from models.database import db
from models.story import Story
from models.image import Image

__all__ = ["db", "Story", "Image"]
