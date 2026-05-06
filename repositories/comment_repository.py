"""
Comment repository.

Public method signatures are the contract that routes / CLI rely on.
Validation rules (length, emptiness, parent-existence) live here so
HTTP and CLI entry points share them without duplication.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence

from flask import current_app
from sqlalchemy import func, select

from models.comment import Comment
from models.database import db
from models.story import Story


class CommentRepository:
    """All Comment DB access goes through here."""

    # ------------------------------------------------------------------
    # Read methods
    # ------------------------------------------------------------------
    @staticmethod
    def list_for_story(story_id: int, limit: Optional[int] = None) -> List[Comment]:
        """Comments for one story, oldest-first (chronological thread)."""
        stmt = (
            select(Comment)
            .where(Comment.story_id == story_id)
            .order_by(Comment.created_at, Comment.id)
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        return list(db.session.scalars(stmt))

    @staticmethod
    def count_for_story(story_id: int) -> int:
        """Single-story comment count. Cheap (uses indexed FK)."""
        stmt = select(func.count(Comment.id)).where(Comment.story_id == story_id)
        return int(db.session.scalar(stmt) or 0)

    @staticmethod
    def counts_for_stories(story_ids: Sequence[int]) -> Dict[int, int]:
        """Bulk count for an arbitrary set of stories.

        Used by the feed view to render comment-icon badges without an
        N+1 query. IDs not present in the result map to 0.
        """
        if not story_ids:
            return {}
        stmt = (
            select(Comment.story_id, func.count(Comment.id))
            .where(Comment.story_id.in_(story_ids))
            .group_by(Comment.story_id)
        )
        rows = db.session.execute(stmt).all()
        counts: Dict[int, int] = {sid: 0 for sid in story_ids}
        for sid, n in rows:
            counts[sid] = int(n)
        return counts

    @staticmethod
    def get_by_id(comment_id: int) -> Optional[Comment]:
        """Single-comment lookup. Returns None if not found."""
        return db.session.get(Comment, comment_id)

    # ------------------------------------------------------------------
    # Write methods
    # ------------------------------------------------------------------
    @staticmethod
    def create(
        story_id: int,
        body: str,
        author: Optional[str] = None,
    ) -> Optional[Comment]:
        """Create a comment after validating body length / non-emptiness.

        Returns the persisted Comment, or None if validation fails or
        the parent story does not exist. Callers translate None into a
        400 / 404 response (see routes/comments.py for rationale on the
        specific error mapping).
        """
        # Verify the parent story exists - we do not trust the caller
        # to have done this, and a missing FK throws an opaque
        # IntegrityError which is harder to surface as a clean 404.
        if db.session.get(Story, story_id) is None:
            return None

        body_clean = (body or "").strip()
        if not body_clean:
            return None

        max_len = int(current_app.config.get("COMMENT_MAX_LENGTH", 4000))
        if len(body_clean) > max_len:
            return None

        author_clean: Optional[str] = (author or "").strip() or None
        if author_clean is not None:
            author_max = int(
                current_app.config.get("COMMENT_AUTHOR_MAX_LENGTH", 80)
            )
            if len(author_clean) > author_max:
                # Trim instead of rejecting - usability over strictness
                # for a non-critical field. Switch to rejection if this
                # ever becomes an abuse vector.
                author_clean = author_clean[:author_max]

        comment = Comment(
            story_id=story_id,
            body=body_clean,
            author=author_clean,
        )
        db.session.add(comment)
        db.session.commit()
        return comment

    @staticmethod
    def delete(comment_id: int) -> bool:
        """Hard-delete a comment. Returns True if it was removed."""
        comment = db.session.get(Comment, comment_id)
        if comment is None:
            return False
        db.session.delete(comment)
        db.session.commit()
        return True

    # FUTURE methods to add:
    #   update(comment_id, body=...)         edit a comment
    #   soft_delete(comment_id)              moderation w/o losing history
    #   list_paginated(story_id, page, ...)  paginated thread view
    #   list_recent(limit)                   global "latest comments" feed
