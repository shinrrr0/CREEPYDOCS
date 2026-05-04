"""
Prefab importer.

Scans two folders next to the project root and imports their contents
into the DB:

    story_prefabs/<name>/        ->  one Story per folder
        meta.json                ->  {"title", "author"?, "section_slug"?}
        body.txt                 ->  story body
        cover.{jpg,png,webp,gif} ->  optional cover image
        gallery/                 ->  optional folder of extra images
            *.jpg / *.png / ...

    images_prefabs/              ->  flat folder, one Image per file
        *.jpg / *.png / ...      ->  added to the public /gallery feed

Idempotent by default - stories with a matching title and gallery
images with a matching filename are skipped on re-runs. Pass force=True
to replace them.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from sqlalchemy import select

from models.database import db
from models.image import Image
from models.story import Story
from repositories.image_repository import ImageRepository
from repositories.story_repository import StoryRepository


# Project root - one level up from this file's parent (services/).
_PROJECT_DIR = Path(__file__).resolve().parent.parent
_STORY_PREFABS_DIR = _PROJECT_DIR / "story_prefabs"
_IMAGE_PREFABS_DIR = _PROJECT_DIR / "images_prefabs"

_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


# =====================================================================
# Public API
# =====================================================================

def import_all_prefabs(force: bool = False, verbose: bool = True) -> dict:
    """Scan both prefab folders and import everything found.

    Returns a dict with insertion counts for the CLI to print:
        {"stories": N, "story_images": N, "gallery_images": N}
    """
    stories, story_images = _import_story_prefabs(force=force, verbose=verbose)
    gallery_images = _import_image_prefabs(force=force, verbose=verbose)
    return {
        "stories": stories,
        "story_images": story_images,
        "gallery_images": gallery_images,
    }


# =====================================================================
# Story prefabs
# =====================================================================

def _import_story_prefabs(force: bool, verbose: bool) -> tuple[int, int]:
    """Returns (stories_inserted, story_images_inserted)."""
    if not _STORY_PREFABS_DIR.is_dir():
        if verbose:
            print(f"[prefab] {_STORY_PREFABS_DIR.name}/ not found, skipping stories")
        return 0, 0

    stories_count = 0
    images_count = 0
    for entry in sorted(_STORY_PREFABS_DIR.iterdir()):
        # Skip files, hidden folders, and obvious noise.
        if not entry.is_dir() or entry.name.startswith(("_", ".")):
            continue
        result = _import_one_story(entry, force=force, verbose=verbose)
        if result is None:
            continue
        stories_count += 1
        images_count += result
    return stories_count, images_count


def _import_one_story(folder: Path, force: bool, verbose: bool) -> Optional[int]:
    """Process a single story prefab folder.

    Returns:
        - number of images attached on success
        - None if the story was skipped (missing files, duplicate, etc.)
    """
    meta_path = folder / "meta.json"
    body_path = folder / "body.txt"

    if not meta_path.is_file() or not body_path.is_file():
        if verbose:
            print(f"[prefab] {folder.name}: missing meta.json or body.txt, skipping")
        return None

    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        if verbose:
            print(f"[prefab] {folder.name}: bad meta.json - {e}")
        return None

    title = (meta.get("title") or "").strip()
    if not title:
        if verbose:
            print(f"[prefab] {folder.name}: meta.json has no title, skipping")
        return None

    body = body_path.read_text(encoding="utf-8")

    # Idempotency: skip if a story with this title already exists.
    existing = db.session.scalar(select(Story).where(Story.title == title))
    if existing is not None:
        if not force:
            if verbose:
                print(f"[prefab] story {title!r} already in DB, skipping")
            return None
        # --force path: cascade-delete the old story and its images.
        db.session.delete(existing)
        db.session.commit()

    story = StoryRepository.create(
        title=title,
        body=body,
        author=meta.get("author"),
        section_slug=meta.get("section_slug"),
    )
    if verbose:
        print(f"[prefab] + story id={story.id}: {title!r}")

    images_attached = 0

    # Optional cover - first matching extension wins.
    for ext in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
        cover_path = folder / f"cover{ext}"
        if cover_path.is_file():
            ImageRepository.create_from_path(
                cover_path,
                story_id=story.id,
                is_cover=True,
                alt_text=meta.get("cover_alt"),
            )
            images_attached += 1
            if verbose:
                print(f"          + cover: {cover_path.name}")
            break

    # Optional extra gallery images attached to this story.
    gallery_dir = folder / "gallery"
    if gallery_dir.is_dir():
        gallery_files = [
            p for p in sorted(gallery_dir.iterdir())
            if p.is_file() and p.suffix.lower() in _IMAGE_EXTS
        ]
        for position, img_path in enumerate(gallery_files):
            ImageRepository.create_from_path(
                img_path,
                story_id=story.id,
                position=position,
            )
            images_attached += 1
            if verbose:
                print(f"          + gallery image: {img_path.name}")

    return images_attached


# =====================================================================
# Image prefabs (flat folder -> public /gallery feed)
# =====================================================================

def _import_image_prefabs(force: bool, verbose: bool) -> int:
    """Returns number of gallery images inserted."""
    if not _IMAGE_PREFABS_DIR.is_dir():
        if verbose:
            print(f"[prefab] {_IMAGE_PREFABS_DIR.name}/ not found, skipping images")
        return 0

    inserted = 0
    for path in sorted(_IMAGE_PREFABS_DIR.iterdir()):
        if not path.is_file() or path.suffix.lower() not in _IMAGE_EXTS:
            continue

        # Idempotency by filename within the gallery scope.
        existing = db.session.scalar(
            select(Image).where(
                Image.is_gallery.is_(True),
                Image.filename == path.name,
            )
        )
        if existing is not None:
            if not force:
                if verbose:
                    print(f"[prefab] gallery image {path.name} already in DB, skipping")
                continue
            db.session.delete(existing)
            db.session.commit()

        img = ImageRepository.create_from_path(path, is_gallery=True)
        inserted += 1
        if verbose:
            print(f"[prefab] + gallery image id={img.id}: {path.name}")
    return inserted
