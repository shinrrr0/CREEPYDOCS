"""
Story model.

Right now this is a plain dataclass so the rest of the app can be developed
independently from the database. When SQLAlchemy is wired up, replace this
with an ORM model that exposes the same public attributes (id, title, body,
created_at, ...). Routes and templates only depend on those attributes,
not on whether this is a dataclass or an ORM row.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Story:
    """A single creepypasta entry."""

    id: int
    title: str
    body: str
    author: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    # FUTURE fields to add when extending:
    #   tags: list[str]
    #   section_slug: str            # which NAV_SECTION it belongs to
    #   comment_count: int
    #   rating: float
