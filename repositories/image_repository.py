"""
Image repository.

All Image DB access goes through here. Public method signatures are
the contract that routes/templates rely on - keep them stable.

The Image table stores binaries for several owner kinds. Helpers below
are organised by owner type so callers do not need to know the schema:

  Story  -> create_for_story / list_for_story / get_cover_for_story / set_as_cover
  Post   -> create_for_post  / list_for_post
  Gallery-> create_gallery   / list_gallery
  Generic-> get_by_id, delete, reorder, create (low-level)
"""

from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import List, Optional

from sqlalchemy import desc, select, update

from models.database import db
from models.image import Image


# Default mime type used when nothing better can be inferred.
_FALLBACK_MIME = "application/octet-stream"


def _guess_mime(filename: str) -> str:
    """Best-effort mime type inference from filename."""
    mime, _ = mimetypes.guess_type(filename)
    return mime or _FALLBACK_MIME


def _filename_to_title(filename: str) -> str:
    """Convert 'creepy_face.jpg' -> 'CREEPY FACE'. Used as a default title
    for gallery items uploaded by filename."""
    if not filename:
        return ""
    stem = filename.rsplit(".", 1)[0]
    return stem.replace("_", " ").replace("-", " ").upper()


class ImageRepository:
    """All Image DB access goes through here."""

    # ==================================================================
    # Generic read / write
    # ==================================================================
    @staticmethod
    def get_by_id(image_id: int) -> Optional[Image]:
        """Fetch a single image. Returns None if not found."""
        return db.session.get(Image, image_id)

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
    def create(
        data: bytes,
        mime_type: str,
        filename: str = "",
        title: Optional[str] = None,
        alt_text: Optional[str] = None,
        story_id: Optional[int] = None,
        post_id: Optional[int] = None,
        is_gallery: bool = False,
        is_cover: bool = False,
        position: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> Image:
        """Low-level insert. Most callers should use the dedicated
        create_for_* / create_gallery helpers below."""
        # Cover semantics: at most one cover per story. Demote any
        # existing cover before inserting the new one.
        if is_cover and story_id is not None:
            ImageRepository._clear_existing_cover(story_id)

        image = Image(
            data=data,
            mime_type=mime_type,
            filename=filename,
            title=title,
            alt_text=alt_text,
            story_id=story_id,
            post_id=post_id,
            is_gallery=is_gallery,
            is_cover=is_cover,
            position=position,
            width=width,
            height=height,
        )
        db.session.add(image)
        db.session.commit()
        return image

    # ==================================================================
    # Story images
    # ==================================================================
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
    def create_for_story(
        story_id: int,
        data: bytes,
        mime_type: str,
        filename: str = "",
        alt_text: Optional[str] = None,
        is_cover: bool = False,
        position: int = 0,
    ) -> Image:
        """Attach a new image to a Story."""
        return ImageRepository.create(
            data=data,
            mime_type=mime_type,
            filename=filename,
            alt_text=alt_text,
            story_id=story_id,
            is_cover=is_cover,
            position=position,
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

    # ==================================================================
    # Post images (blog)
    # ==================================================================
    @staticmethod
    def list_for_post(post_id: int) -> List[Image]:
        """All images attached to a single post, in display order."""
        stmt = (
            select(Image)
            .where(Image.post_id == post_id)
            .order_by(Image.position, Image.id)
        )
        return list(db.session.scalars(stmt))

    @staticmethod
    def create_for_post(
        post_id: int,
        data: bytes,
        mime_type: str,
        filename: str = "",
        alt_text: Optional[str] = None,
        position: int = 0,
    ) -> Image:
        """Attach a new image to a blog Post."""
        return ImageRepository.create(
            data=data,
            mime_type=mime_type,
            filename=filename,
            alt_text=alt_text,
            post_id=post_id,
            position=position,
        )

    # ==================================================================
    # Gallery images (free-standing, shown at /gallery)
    # ==================================================================
    @staticmethod
    def list_gallery(limit: Optional[int] = None) -> List[Image]:
        """All images flagged for the public gallery feed.

        Newest-first by default. The route shuffles the result for
        the masonry layout, so ordering here is mostly a tie-breaker.
        """
        stmt = (
            select(Image)
            .where(Image.is_gallery.is_(True))
            .order_by(desc(Image.created_at), Image.id)
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        return list(db.session.scalars(stmt))

    @staticmethod
    def create_gallery(
        data: bytes,
        mime_type: str,
        filename: str = "",
        title: Optional[str] = None,
        alt_text: Optional[str] = None,
    ) -> Image:
        """Insert a free-standing gallery image (no parent story/post)."""
        if title is None:
            title = _filename_to_title(filename)
        if alt_text is None:
            alt_text = title or filename or None
        return ImageRepository.create(
            data=data,
            mime_type=mime_type,
            filename=filename,
            title=title,
            alt_text=alt_text,
            is_gallery=True,
        )

    # ==================================================================
    # File-system helpers (handy for seeders / one-off ingest)
    # ==================================================================
    @staticmethod
    def create_from_path(
        path: Path | str,
        story_id: Optional[int] = None,
        post_id: Optional[int] = None,
        is_gallery: bool = False,
        is_cover: bool = False,
        title: Optional[str] = None,
        alt_text: Optional[str] = None,
        position: int = 0,
    ) -> Image:
        """Read a file from disk and store its bytes. Useful for seeding
        fixtures and admin/CLI ingest. Production upload flows should
        call .create() / .create_for_post() / etc. with bytes already
        in memory.
        """
        path = Path(path)
        return ImageRepository.create(
            data=path.read_bytes(),
            mime_type=_guess_mime(path.name),
            filename=path.name,
            title=title if title is not None else (
                _filename_to_title(path.name) if is_gallery else None
            ),
            alt_text=alt_text,
            story_id=story_id,
            post_id=post_id,
            is_gallery=is_gallery,
            is_cover=is_cover,
            position=position,
        )

    @staticmethod
    def reorder(
        image_ids_in_order: List[int],
        story_id: Optional[int] = None,
        post_id: Optional[int] = None,
    ) -> None:
        """Bulk update positions for a set of images belonging to one
        owner. Pass image ids in the desired display order. The optional
        owner filter prevents cross-owner reordering by mistake.
        """
        for index, image_id in enumerate(image_ids_in_order):
            stmt = update(Image).where(Image.id == image_id)
            if story_id is not None:
                stmt = stmt.where(Image.story_id == story_id)
            if post_id is not None:
                stmt = stmt.where(Image.post_id == post_id)
            db.session.execute(stmt.values(position=index))
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
    #   search_by_title(query)                    gallery search
