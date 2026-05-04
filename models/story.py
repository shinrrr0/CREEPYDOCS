"""
Story ORM model.

Public attributes (id, title, body, author, section_slug, created_at)
match what the templates already expect, so the data layer can be
swapped without touching the front end. Add new columns here to
extend a story.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.database import db

if TYPE_CHECKING:
    # Imported only for type hints to avoid circular imports at runtime.
    from models.image import Image


class Story(db.Model):
    """A single creepypasta entry."""

    __tablename__ = "stories"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)

    # Section is referenced by slug (string), not a foreign key, because
    # section metadata lives in Config.NAV_SECTIONS. Validate at write
    # time via Config.valid_section_slugs() if strictness is needed.
    section_slug: Mapped[Optional[str]] = mapped_column(
        String(64), index=True, nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True, nullable=False
    )

    # ---- Relationships ----
    # `cascade="all, delete-orphan"` mirrors the ON DELETE CASCADE on
    # Image.story_id so cleanup works whether you delete via the ORM or
    # directly via SQL.
    images: Mapped[List["Image"]] = relationship(
        back_populates="story",
        cascade="all, delete-orphan",
        order_by="Image.position",
        foreign_keys="Image.story_id",
    )

    # ---- Convenience accessors used by templates ----
    @property
    def cover_image(self) -> Optional["Image"]:
        """The cover image if any was flagged, else the first attached image."""
        for img in self.images:
            if img.is_cover:
                return img
        return self.images[0] if self.images else None

    @property
    def gallery_images(self) -> List["Image"]:
        """All non-cover images attached to this story, in position order."""
        cover = self.cover_image
        return [img for img in self.images if img is not cover]

    # FUTURE columns to add as features land:
    #   slug:          unique URL-safe identifier
    #   is_published:  draft vs published
    #   view_count:    cached counter
    #   updated_at:    last edit time
    # FUTURE relationships:
    #   comments, tags - add when those features are scheduled.

    def __repr__(self) -> str:
        return f"<Story id={self.id} title={self.title!r}>"
