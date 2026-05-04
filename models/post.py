"""
Post ORM model.

Represents a single blog post. A post can carry text, image, or both.
Public attributes (id, blog_id, text, created_at, image, image_filename)
match what `templates/components/post_card.html` already expects, so
the front end did not need to change beyond URL-construction.

Architecture note: blog_id is just an integer (1..MAX_BLOGS). Blogs
themselves have no row in the DB - they are lazy-created the moment
the first post in that blog appears, and disappear naturally when no
posts reference them.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.database import db

if TYPE_CHECKING:
    from models.image import Image


class Post(db.Model):
    """A single blog post inside one of the numbered blogs."""

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Indexed because the blog feed query is `WHERE blog_id = ?`.
    blog_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)

    # Either text or an attached image must be present (validated at
    # write time in the repository / route, not in the schema, to keep
    # the SQL portable).
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True, nullable=False
    )

    # ---- Relationships ----
    # A post currently uses at most one image (matches the UI in
    # post_card.html). The relationship is a list so multi-image posts
    # are a one-line change later.
    images: Mapped[List["Image"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
        order_by="Image.position",
        foreign_keys="Image.post_id",
    )

    # ---- Convenience accessors used by templates ----
    @property
    def image(self) -> Optional["Image"]:
        """First (and currently only) attached image, or None."""
        return self.images[0] if self.images else None

    @property
    def image_filename(self) -> Optional[str]:
        """Back-compat shim - templates that still look at this attribute
        keep working. New code should use `.image.url` directly."""
        return self.image.filename if self.image else None

    # FUTURE columns to add when extending:
    #   author:          who posted (once auth lands)
    #   likes_count:     denormalised counter
    #   parent_post_id:  threading / replies
    # FUTURE methods:
    #   word_count, has_image, is_text_only - presentation helpers

    def __repr__(self) -> str:
        return f"<Post id={self.id} blog_id={self.blog_id}>"
