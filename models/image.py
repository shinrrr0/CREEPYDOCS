"""
Image ORM model.

Stores image binary directly in the database (LargeBinary column) so
backups, replication, and ops are all single-source-of-truth. For very
large libraries this can be migrated to filesystem/object storage by
swapping `data` for a `storage_key` column without changing the rest
of the app - templates only consume `image.url`, never `image.data`.

Usage shapes:
- Attached to a story (story_id set): part of a story's gallery.
- Standalone (story_id NULL): site assets like banners, decorative art.
- Cover (is_cover=True): the lead image for a story; at most one per story.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from flask import url_for
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.database import db

if TYPE_CHECKING:
    from models.story import Story


class Image(db.Model):
    """A single binary image asset."""

    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Optional parent story. Nullable on purpose - the same table also
    # holds standalone site images (banners, decorative assets, etc.).
    # ON DELETE CASCADE: when a Story row is deleted, its images go too.
    story_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("stories.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )

    # ---- Metadata ----
    # Original filename at upload time (display + download hint, not used
    # for storage path since data lives in the DB).
    filename: Mapped[str] = mapped_column(String(255), nullable=False, default="")

    # Required so the image-serving route can set Content-Type correctly.
    # Examples: "image/png", "image/jpeg", "image/webp", "image/svg+xml".
    mime_type: Mapped[str] = mapped_column(String(80), nullable=False)

    # Accessibility text. Always provide one when uploading user content.
    alt_text: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Optional dimensions, populated at upload time when known. Useful
    # for reserving layout space and avoiding CLS on the front end.
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # ---- Gallery ordering / cover flag ----
    # Lower position renders first. Default 0; assign explicitly when
    # uploading multiple images for one story.
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # At most one cover per story (enforced at the application layer in
    # ImageRepository.set_as_cover; the schema does not enforce it so
    # bulk inserts stay simple).
    is_cover: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # ---- Binary payload ----
    # The actual image bytes. SQLAlchemy maps to BLOB / BYTEA depending
    # on the dialect. SQLite handles a few MB without complaint; for
    # heavier workloads consider Postgres + pg_largeobject or external
    # storage (see module docstring).
    data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # ---- Relationships ----
    story: Mapped[Optional["Story"]] = relationship(back_populates="images")

    # ---- Convenience accessors used by templates ----
    @property
    def url(self) -> str:
        """Public URL where the binary can be fetched (routes/images.py)."""
        return url_for("images.serve", image_id=self.id)

    @property
    def size_bytes(self) -> int:
        return len(self.data) if self.data else 0

    def __repr__(self) -> str:
        return (
            f"<Image id={self.id} story_id={self.story_id} "
            f"mime={self.mime_type} bytes={self.size_bytes}>"
        )
