"""
Post model.

Represents a single blog post. Can contain text, image, or both.
Dataclass now; will become ORM model when DB is wired up.
Routes and templates only depend on public attributes, so the swap
will be transparent.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Post:
    """A single blog post."""

    id: int
    text: Optional[str] = None          # post body text (can be None if image-only)
    image_filename: Optional[str] = None  # relative to static/images/blog/ (can be None if text-only)
    created_at: datetime = field(default_factory=datetime.utcnow)

    # FUTURE fields:
    #   author: str
    #   likes_count: int
    #   comments_count: int
    #   tags: list[str]
