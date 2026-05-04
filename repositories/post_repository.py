"""
Post repository.

All Post DB access goes through here. Public method signatures are the
contract that routes/templates rely on.

Posts and their attached image are managed together: `create()` accepts
optional image bytes and persists both rows in a single transaction.
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import desc, func, select

from models.database import db
from models.post import Post
from models.image import Image


class PostRepository:
    """All Post DB access goes through here."""

    # ------------------------------------------------------------------
    # Read methods
    # ------------------------------------------------------------------
    @staticmethod
    def list_by_blog(blog_id: int, limit: Optional[int] = None) -> List[Post]:
        """Posts in a single blog, newest-first."""
        stmt = (
            select(Post)
            .where(Post.blog_id == blog_id)
            .order_by(desc(Post.created_at), desc(Post.id))
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        return list(db.session.scalars(stmt))

    @staticmethod
    def get_by_id(post_id: int) -> Optional[Post]:
        """Single post lookup. Returns None if not found."""
        return db.session.get(Post, post_id)

    @staticmethod
    def count_for_blog(blog_id: int) -> int:
        """Number of posts in a blog. Useful for empty-state checks."""
        stmt = select(func.count(Post.id)).where(Post.blog_id == blog_id)
        return int(db.session.scalar(stmt) or 0)

    # ------------------------------------------------------------------
    # Write methods
    # ------------------------------------------------------------------
    @staticmethod
    def create(
        blog_id: int,
        text: Optional[str] = None,
        image_data: Optional[bytes] = None,
        image_mime_type: Optional[str] = None,
        image_filename: str = "",
        image_alt_text: Optional[str] = None,
    ) -> Optional[Post]:
        """Create a new post and optionally attach an image.

        At least one of `text` / `image_data` must be present (validated
        here so neither route nor template needs to guard against empty
        posts). Returns the created Post, or None if validation fails.

        Both rows are committed in a single transaction so a failure
        anywhere rolls everything back.
        """
        text_clean = (text or "").strip() or None
        if not text_clean and not image_data:
            return None
        if image_data is not None and not image_mime_type:
            # Caller forgot to supply the mime type - we will not guess
            # blindly here because that would silently mis-serve images.
            return None

        post = Post(blog_id=blog_id, text=text_clean)
        db.session.add(post)
        # Flush so post.id is populated before the image row references it.
        db.session.flush()

        if image_data is not None:
            image = Image(
                data=image_data,
                mime_type=image_mime_type,
                filename=image_filename,
                alt_text=image_alt_text,
                post_id=post.id,
            )
            db.session.add(image)

        db.session.commit()
        return post

    @staticmethod
    def delete(post_id: int) -> bool:
        """Delete a post (cascades to its image). Returns True on success."""
        post = db.session.get(Post, post_id)
        if post is None:
            return False
        db.session.delete(post)
        db.session.commit()
        return True

    # FUTURE methods to add:
    #   update(post_id, text=...)             edit text
    #   list_recent_across_blogs(limit)       site-wide "what's new" feed
    #   list_paginated(blog_id, page, ...)    pagination
    #   search(blog_id, query)                full-text search inside a blog
