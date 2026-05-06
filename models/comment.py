"""
Comment ORM model.

Each comment belongs to exactly one Story. Plain text only - no
attachments, no formatting markup (per spec).

Encoding: `body` is mapped to SQLAlchemy Text -> TEXT in SQLite /
Postgres / MySQL. TEXT is binary-safe for UTF-8 in all of them, so
Cyrillic and other non-ASCII content survives a round trip without
extra configuration.

FUTURE columns (add when those features land):
  parent_id   - threaded replies (self-FK to comments.id)
  is_deleted  - soft delete for moderation history
  edited_at   - last-edit timestamp
  ip_hash     - rate-limit / spam detection
  user_id     - link to a real auth user once that exists
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.database import db

if TYPE_CHECKING:
    # Imported only for type hints to avoid circular imports at runtime.
    from models.story import Story


class Comment(db.Model):
    """A single user comment attached to a Story."""

    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)

    # ON DELETE CASCADE: when the parent story is deleted its comments
    # are removed too. Mirrors how images are tied to stories so a
    # raw-SQL delete behaves the same as an ORM delete.
    story_id: Mapped[int] = mapped_column(
        ForeignKey("stories.id", ondelete="CASCADE"),
        index=True, nullable=False,
    )

    # Body is required and stored as TEXT so the column itself imposes
    # no length cap. The application-level cap lives in
    # Config.COMMENT_MAX_LENGTH and is enforced by CommentRepository.
    body: Mapped[str] = mapped_column(Text, nullable=False)

    # Optional display name. Repository normalises blank/None on write.
    author: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True, nullable=False,
    )

    # ---- Relationship ----
    story: Mapped["Story"] = relationship(back_populates="comments")

    # ---- Convenience for JSON serialisation (used by API + JS) ----
    def to_dict(self) -> dict:
        """Serialisable shape for the JSON API and the JS renderer."""
        return {
            "id": self.id,
            "story_id": self.story_id,
            "body": self.body,
            # Falling back to "anon" here keeps the front-end simple:
            # it can render `comment.author` directly without guards.
            "author": self.author or "anon",
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<Comment id={self.id} story_id={self.story_id}>"
