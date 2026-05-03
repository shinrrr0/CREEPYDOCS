"""
Image repository.

All Image DB access goes through here. Public method signatures are
the contract that routes/templates rely on - keep them stable.
"""

from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import List, Optional

from sqlalchemy import select, update

from models.database import db
from models.image import Image


# Default mime type used when nothing better can be inferred.
_FALLBACK_MIME = "application/octet-stream"


def _guess_mime(filename: str) -> str:
    """Best-effort mime type inference from filename. Used by helpers
    that accept a path/filename without an explicit mime."""
    mime, _ = mimetypes.guess_type(filename)
    return mime or _FALLBACK_MIME


class ImageRepository:
    """All Image DB access goes through here."""

    # ------------------------------------------------------------------
    # Read methods
    # ------------------------------------------------------------------
    @staticmethod
    def get_by_id(image_id: int) -> Optional[Image]:
        """Fetch a single image. Returns None if not found."""
        return db.session.get(Image, image_id)

    @staticmethod
    def list_for_story(story_id: int) -> List[Image]:
        """All images attached to a story, in display order."""
        stmt = (
            select(Image)
            .where(Image.story_id == story_id)
            .order_by(Image.position, Image.id)
        )
        return list(db.session.scalars(stmt))

    @staticmethod
    def get_cover_for_story(story_id: int) -> Optional[Image]:
        """Cover image for a story, if any has been flagged."""
        stmt = (
            select(Image)
            .where(Image.story_id == story_id, Image.is_cover.is_(True))
            .limit(1)
        )
        return db.session.scalars(stmt).first()

    @staticmethod
    def list_standalone() -> List[Image]:
        """Images not attached to any story (banners, decorative assets)."""
        stmt = select(Image).where(Image.story_id.is_(None)).order_by(Image.id)
        return list(db.session.scalars(stmt))

    # ------------------------------------------------------------------
    # Write methods
    # ------------------------------------------------------------------
    @staticmethod
    def create(
        data: bytes,
        mime_type: str,
        filename: str = "",
        story_id: Optional[int] = None,
        alt_text: Optional[str] = None,
        position: int = 0,
        is_cover: bool = False,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> Image:
        """Insert a new image and return the persisted instance.

        If `is_cover=True`, any existing cover for the same story is
        un-flagged first so only one cover survives.
        """
        if is_cover and story_id is not None:
            ImageRepository._clear_existing_cover(story_id)

        image = Image(
            data=data,
            mime_type=mime_type,
            filename=filename,
            story_id=story_id,
            alt_text=alt_text,
            position=position,
            is_cover=is_cover,
            width=width,
            height=height,
        )
        db.session.add(image)
        db.session.commit()
        return image

    @staticmethod
    def create_from_path(
        path: Path | str,
        story_id: Optional[int] = None,
        alt_text: Optional[str] = None,
        position: int = 0,
        is_cover: bool = False,
    ) -> Image:
        """Convenience helper: read a file from disk and store its bytes.

        Useful for seeding fixtures and admin/CLI ingest. Production
        upload flows should call .create() directly with the bytes
        already in memory.
        """
        path = Path(path)
        return ImageRepository.create(
            data=path.read_bytes(),
            mime_type=_guess_mime(path.name),
            filename=path.name,
            story_id=story_id,
            alt_text=alt_text,
            position=position,
            is_cover=is_cover,
        )

    @staticmethod
    def set_as_cover(image_id: int) -> bool:
        """Promote `image_id` to cover, demoting any other cover on the
        same story. Returns True on success."""
        image = db.session.get(Image, image_id)
        if image is None or image.story_id is None:
            return False

        ImageRepository._clear_existing_cover(image.story_id)
        image.is_cover = True
        db.session.commit()
        return True

    @staticmethod
    def delete(image_id: int) -> bool:
        """Delete a single image. Returns True if it was removed."""
        image = db.session.get(Image, image_id)
        if image is None:
            return False
        db.session.delete(image)
        db.session.commit()
        return True

    @staticmethod
    def reorder(story_id: int, image_ids_in_order: List[int]) -> None:
        """Bulk update positions for a story's gallery. Pass image ids in
        the desired display order."""
        for index, image_id in enumerate(image_ids_in_order):
            db.session.execute(
                update(Image)
                .where(Image.id == image_id, Image.story_id == story_id)
                .values(position=index)
            )
        db.session.commit()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _clear_existing_cover(story_id: int) -> None:
        """Un-flag any current cover for the given story."""
        db.session.execute(
            update(Image)
            .where(Image.story_id == story_id, Image.is_cover.is_(True))
            .values(is_cover=False)
        )

    # FUTURE methods to add:
    #   replace_data(image_id, data, mime_type)   in-place edit
    #   bulk_create_for_story(story_id, files)    multi-upload helper
    #   list_paginated(page, per_page)            admin galleries
