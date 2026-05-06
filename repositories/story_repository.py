"""
Story repository.

Public method signatures match the previous stub-backed version so
that routes and templates work without changes. Add new query shapes
here rather than putting raw queries in routes.
"""

from typing import List, Optional

from sqlalchemy import select, func

from models.database import db
from models.story import Story


class StoryRepository:
    """All Story DB access goes through here."""

    # ------------------------------------------------------------------
    # Read methods
    # ------------------------------------------------------------------
    @staticmethod
    def list_all(limit: Optional[int] = None) -> List[Story]:
        """Return stories ordered newest-first. `limit` caps the result."""
        stmt = select(Story).order_by(Story.created_at.desc())
        if limit is not None:
            stmt = stmt.limit(limit)
        return list(db.session.scalars(stmt))

    @staticmethod
    def get_by_id(story_id: int) -> Optional[Story]:
        """Single-story lookup. Returns None if not found."""
        return db.session.get(Story, story_id)

    @staticmethod
    def get_random() -> Optional[Story]:
        """Return one story chosen at random. Returns None if table is empty."""
        # ORDER BY RANDOM() works in SQLite and PostgreSQL; for MySQL use RAND().
        stmt = select(Story).order_by(func.random()).limit(1)
        return db.session.scalars(stmt).first()

    @staticmethod
    def list_by_section(
        section_slug: str, limit: Optional[int] = None
    ) -> List[Story]:
        """Filter by section slug (matches Config.NAV_SECTIONS)."""
        stmt = (
            select(Story)
            .where(Story.section_slug == section_slug)
            .order_by(Story.created_at.desc())
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        return list(db.session.scalars(stmt))

    # ------------------------------------------------------------------
    # Write methods
    # ------------------------------------------------------------------
    @staticmethod
    def create(
        title: str,
        body: str,
        author: Optional[str] = None,
        section_slug: Optional[str] = None,
    ) -> Story:
        """Insert a new story and return the persisted instance."""
        story = Story(
            title=title,
            body=body,
            author=author,
            section_slug=section_slug,
        )
        db.session.add(story)
        db.session.commit()
        return story

    @staticmethod
    def delete(story_id: int) -> bool:
        """Delete a story (cascades to its images). Returns True on success."""
        story = db.session.get(Story, story_id)
        if story is None:
            return False
        db.session.delete(story)
        db.session.commit()
        return True

    # FUTURE methods to add as features land:
    #   update(story_id, **fields)            edit a story
    #   list_by_tag(tag_name)                 filter by tag join
    #   search(query)                         full-text / LIKE search
    #   list_paginated(page, per_page)        pagination for the feed
