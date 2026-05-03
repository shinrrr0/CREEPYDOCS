"""
Post repository.

Public interface for post data access. Routes call this, not the stub directly.
Signatures are stable so they won't change when migrating to a real DB.
"""

from typing import List, Optional

from models.post import Post
from services import blog_stub_data


class PostRepository:
    """All Post data access goes through here."""

    # ------------------------------------------------------------------
    # Read methods
    # ------------------------------------------------------------------
    @staticmethod
    def list_by_blog(blog_id: int, limit: Optional[int] = None) -> List[Post]:
        """Return all posts for a blog, newest first. Limit caps result."""
        # FUTURE (SQLAlchemy):
        #     query = Post.query.filter_by(blog_id=blog_id).order_by(Post.created_at.desc())
        #     if limit:
        #         query = query.limit(limit)
        #     return query.all()
        return blog_stub_data.get_posts_for_blog(blog_id, limit=limit)

    @staticmethod
    def get_by_id(post_id: int) -> Optional[Post]:
        """Single post lookup. Returns None if not found."""
        # FUTURE (SQLAlchemy):
        #     return Post.query.get(post_id)
        return blog_stub_data.get_post_by_id_stub(post_id)

    # ------------------------------------------------------------------
    # Write methods
    # ------------------------------------------------------------------
    @staticmethod
    def create(blog_id: int,
               text: Optional[str] = None,
               image_filename: Optional[str] = None) -> Optional[Post]:
        """
        Create a new post in a blog. At least one of text/image must be provided.
        Validation happens here, not in the stub.

        Returns the created Post, or None if validation fails.

        FUTURE (SQLAlchemy):
            post = Post(blog_id=blog_id, text=text, image_filename=image_filename)
            db.session.add(post)
            db.session.commit()
            return post
        """
        if not text and not image_filename:
            return None

        return blog_stub_data.create_post_stub(blog_id=blog_id, text=text, image_filename=image_filename)

    @staticmethod
    def delete(post_id: int) -> bool:
        """Delete a post by ID. Returns True if deleted, False if not found."""
        # FUTURE (SQLAlchemy):
        #     post = Post.query.get(post_id)
        #     if post:
        #         db.session.delete(post)
        #         db.session.commit()
        #         return True
        #     return False
        return blog_stub_data.delete_post_stub(post_id)
