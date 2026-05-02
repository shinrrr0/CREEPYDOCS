"""
Story repository.

Public interface that routes call. Right now it delegates to the stub
data source; later it will run SQLAlchemy queries. The signatures here
are the contract - keep them stable when migrating to the real DB.
"""

from typing import List, Optional

from models.story import Story
from services import stub_data


class StoryRepository:
    """All Story DB access goes through here."""

    # ------------------------------------------------------------------
    # Read methods
    # ------------------------------------------------------------------
    @staticmethod
    def list_all(limit: Optional[int] = None) -> List[Story]:
        """Return stories ordered newest-first. `limit` caps the result."""
        # FUTURE (SQLAlchemy):
        #     query = Story.query.order_by(Story.created_at.desc())
        #     if limit is not None:
        #         query = query.limit(limit)
        #     return query.all()
        stories = sorted(
            stub_data.get_all_stories_stub(),
            key=lambda s: s.created_at,
            reverse=True,
        )
        return stories[:limit] if limit is not None else stories

    @staticmethod
    def get_by_id(story_id: int) -> Optional[Story]:
        """Single-story lookup. Returns None if not found."""
        # FUTURE (SQLAlchemy):
        #     return Story.query.get(story_id)
        return stub_data.get_story_by_id_stub(story_id)

    @staticmethod
    def list_by_section(section_slug: str, limit: Optional[int] = None) -> List[Story]:
        """Filter by section slug (matches Config.NAV_SECTIONS).

        Currently returns everything because the stub has no section field.
        Wire up properly once the schema includes `section_slug`.
        """
        # FUTURE (SQLAlchemy):
        #     query = Story.query.filter_by(section_slug=section_slug) ...
        return StoryRepository.list_all(limit=limit)

    # ------------------------------------------------------------------
    # Write methods - placeholders, fill in once DB is live.
    # ------------------------------------------------------------------
    @staticmethod
    def create(title: str, body: str, author: Optional[str] = None) -> Story:
        """Create a new story. NotImplemented until DB is wired up."""
        raise NotImplementedError("StoryRepository.create needs the DB layer")

    @staticmethod
    def delete(story_id: int) -> bool:
        """Delete by id. Returns True on success."""
        raise NotImplementedError("StoryRepository.delete needs the DB layer")
