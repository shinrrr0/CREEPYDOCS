"""
Domain models package.

Importing this module is what registers all model classes on the
shared `db.metadata`. Anything that calls `db.create_all()` or
`db.drop_all()` must import this first (or import the individual model
modules) so SQLAlchemy knows the tables exist.

Single tidy entrypoint:
    from models import Story, Post, Image, Comment, db
"""

from models.database import db
from models.story import Story
from models.post import Post
from models.image import Image
from models.comment import Comment

__all__ = ["db", "Story", "Post", "Image", "Comment"]
