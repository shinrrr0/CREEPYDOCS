"""
Blog stub data source.

In-memory storage of Post objects during development. Later, swap this
for SQLAlchemy queries in post_repository.py without changing the public
interface. The repository layer handles this swap transparently.

STORAGE APPROACH (temporary, for development):
  - Posts stored in a simple list (_posts) with auto-incremented ID
  - Image files are saved to static/images/blog/ as regular files
  - Filenames are timestamps: e.g. "1746345600_photo.jpg"
  - On app restart, in-memory posts vanish (expected for dev stub)
  - Images persist on disk (useful for UI testing)

MIGRATION PATH:
  - Replace this entire module with SQLAlchemy queries
  - Keep method signatures the same
  - Routes and templates unchanged
"""

from datetime import datetime
from typing import List, Optional

from models.post import Post


# In-memory post storage. ID counter increments with each new post.
_posts: List[Post] = []
_next_post_id = 1


def _get_next_id() -> int:
    """Generate unique post ID."""
    global _next_post_id
    result = _next_post_id
    _next_post_id += 1
    return result


def get_all_posts_stub(limit: Optional[int] = None) -> List[Post]:
    """Return all posts, newest first. Limit caps result."""
    sorted_posts = sorted(_posts, key=lambda p: p.created_at, reverse=True)
    return sorted_posts[:limit] if limit else sorted_posts


def get_post_by_id_stub(post_id: int) -> Optional[Post]:
    """Single post lookup. Returns None if not found."""
    for post in _posts:
        if post.id == post_id:
            return post
    return None


def create_post_stub(text: Optional[str] = None,
                     image_filename: Optional[str] = None) -> Post:
    """Create and store a new post. At least one of text/image must be provided."""
    if not text and not image_filename:
        return None  # validation happens in the repository

    post = Post(
        id=_get_next_id(),
        text=text,
        image_filename=image_filename,
        created_at=datetime.utcnow(),
    )
    _posts.append(post)
    return post


def delete_post_stub(post_id: int) -> bool:
    """Delete a post by ID. Returns True if found and deleted, False otherwise."""
    global _posts
    original_len = len(_posts)
    _posts = [p for p in _posts if p.id != post_id]
    return len(_posts) < original_len
