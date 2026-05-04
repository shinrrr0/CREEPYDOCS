"""
Image ORM model.

One table, several roles - the role is determined by which FK is set:

  story_id NOT NULL  ............ image belongs to a Story
                                  (cover if is_cover=True, gallery item otherwise)
  post_id  NOT NULL  ............ image belongs to a blog Post
  is_gallery=True (both NULL) ... shows up in the global /gallery feed
  everything else NULL/False .... standalone site asset (banner, decoration)

Stores image bytes directly in the database (LargeBinary). Backups,
replication, and ops are all single-source-of-truth. For very large
libraries this can be migrated to filesystem/object storage by swapping
`data` for a `storage_key` column without changing the rest of the app -
templates only consume `image.url`, never `image.data`.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from flask import url_for
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.database import db

if TYPE_CHECKING:
    from models.story import Story
    from models.post import Post


class Image(db.Model):
    """A single binary image asset."""

    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True)

    # ---- Ownership FKs ----
    # Optional. ON DELETE CASCADE: when a parent Story / Post row is
    # deleted, its images go too. At most one of these should be set on
    # any given row; the application layer enforces this.
    story_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("stories.id", ondelete="CASCADE"),
        index=True, nullable=True,
    )
    post_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        index=True, nullable=True,
    )

    # ---- Display flags ----
    # True for images that should appear in the global /gallery feed.
    # Only meaningful when the image is not attached to a story or post,
    # but the column is checked unconditionally so a story/post image
    # can also be promoted into the public gallery if desired.
    is_gallery: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True,
    )

    # At most one cover per story (enforced at the application layer in
    # ImageRepository.set_as_cover; the schema does not enforce it so
    # bulk inserts stay simple).
    is_cover: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
    )

    # ---- Metadata ----
    # Original filename at upload time (display + download hint, not
    # used for storage path since data lives in the DB).
    filename: Mapped[str] = mapped_column(String(255), nullable=False, default="")

    # Required so the image-serving route can set Content-Type correctly.
    # Examples: "image/png", "image/jpeg", "image/webp", "image/svg+xml".
    mime_type: Mapped[str] = mapped_column(String(80), nullable=False)

    # Display title, primarily for gallery cards. Falls back to filename
    # if blank when the template asks for a title.
    title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Accessibility text. Always provide one when uploading user content.
    alt_text: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Optional dimensions, populated at upload time when known. Useful
    # for reserving layout space and avoiding CLS on the front end.
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Lower position renders first inside whichever owner the image
    # belongs to (story gallery, blog post slot, public gallery feed).
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # ---- Binary payload ----
    # The actual image bytes. SQLAlchemy maps to BLOB / BYTEA depending
    # on the dialect. SQLite handles a few MB without complaint; for
    # heavier workloads consider Postgres + pg_largeobject or external
    # storage (see module docstring).
    data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True,
    )

    # ---- Relationships ----
    story: Mapped[Optional["Story"]] = relationship(
        back_populates="images", foreign_keys=[story_id],
    )
    post: Mapped[Optional["Post"]] = relationship(
        back_populates="images", foreign_keys=[post_id],
    )

    # ---- Convenience accessors used by templates ----
    @property
    def url(self) -> str:
        """Public URL where the binary can be fetched (routes/images.py)."""
        return url_for("images.serve", image_id=self.id)

    @property
    def display_title(self) -> str:
        """Human-friendly label - title if set, else filename stem."""
        if self.title:
            return self.title
        if self.filename:
            stem = self.filename.rsplit(".", 1)[0]
            return stem.replace("_", " ").replace("-", " ").upper()
        return f"IMAGE {self.id}"

    @property
    def size_bytes(self) -> int:
        return len(self.data) if self.data else 0

    def __repr__(self) -> str:
        owner = (
            f"story={self.story_id}" if self.story_id is not None
            else f"post={self.post_id}" if self.post_id is not None
            else "gallery" if self.is_gallery
            else "standalone"
        )
        return (
            f"<Image id={self.id} {owner} "
            f"mime={self.mime_type} bytes={self.size_bytes}>"
        )
