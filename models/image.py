"""
Image model.

A plain dataclass that mirrors the Story pattern.
When SQLAlchemy is wired in, replace with an ORM model that exposes
the same public attributes – routes and templates won't need changes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Image:
    """A single gallery image entry."""

    id: int
    filename: str          # e.g. "ghost_face.jpg" – relative to static/images/gallery/
    title: str             # display label shown beneath the image
    alt: str = ""          # accessibility alt text
    created_at: datetime = field(default_factory=datetime.utcnow)

    # FUTURE fields to add when extending:
    #   section_slug: str        – which NAV_SECTION this belongs to
    #   tags: list[str]          – filterable keywords
    #   uploaded_by: str         – author / curator handle
    #   story_id: Optional[int]  – links image to a related Story
    #   nsfl: bool               – content-warning flag
