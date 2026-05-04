"""
Database seeder.

What it does on `flask seed-db`:
  1. Inserts STORY_FIXTURES from stub_data, generating an SVG placeholder
     cover for some of them.
  2. Ingests every supported image file in static/images/gallery/ into
     the `images` table with is_gallery=True. Re-runs are idempotent
     (filenames already in the table are skipped).
  3. Inserts BLOG_POST_FIXTURES, attaching gallery images to a couple
     of them so the blog feed has visual content to test against.

All steps are idempotent unless `force=True` is passed. With `force=True`
the existing fixture rows that match by title (stories) or composite
identity (posts) are deleted and replaced.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from sqlalchemy import select

from models.database import db
from models.image import Image
from models.post import Post
from models.story import Story
from repositories.image_repository import ImageRepository
from services.stub_data import BLOG_POST_FIXTURES, STORY_FIXTURES


# ---------------------------------------------------------------------
# Resolve the gallery directory relative to this file - works regardless
# of cwd. Replace with a Config value once the upload system is in place.
# ---------------------------------------------------------------------
_GALLERY_DIR = (
    Path(__file__).resolve().parent.parent / "static" / "images" / "gallery"
)
_SUPPORTED_GALLERY_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


# ---------------------------------------------------------------------
# Placeholder cover SVG.
# Building it inline keeps the repo self-contained - no asset files
# needed to demonstrate that the cover-image pipeline works.
# ---------------------------------------------------------------------
def _placeholder_cover_svg(label: str) -> bytes:
    """Generate a small black/red SVG suitable as a story cover."""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" preserveAspectRatio="xMidYMid slice">
  <defs>
    <radialGradient id="g" cx="50%" cy="50%" r="65%">
      <stop offset="0%" stop-color="#2a0000"/>
      <stop offset="100%" stop-color="#0a0a0a"/>
    </radialGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#g)"/>
  <g stroke="#5c0000" stroke-width="1" opacity="0.35">
    <line x1="0" y1="80" x2="800" y2="80"/>
    <line x1="0" y1="160" x2="800" y2="160"/>
    <line x1="0" y1="240" x2="800" y2="240"/>
    <line x1="0" y1="320" x2="800" y2="320"/>
    <line x1="0" y1="400" x2="800" y2="400"/>
  </g>
  <text x="50%" y="50%" fill="#b30000"
        font-family="Courier New, monospace" font-size="42"
        font-weight="700" letter-spacing="6"
        text-anchor="middle" dominant-baseline="middle">{label}</text>
  <text x="50%" y="62%" fill="#5c0000"
        font-family="Courier New, monospace" font-size="14"
        letter-spacing="4"
        text-anchor="middle" dominant-baseline="middle">// CREEPYDOCS ARCHIVE //</text>
</svg>'''
    return svg.encode("utf-8")


# Map fixture story titles -> seed-cover specs.
_SEED_COVERS: dict[str, dict] = {
    "THE STATIC ON THE LINE": {"label": "STATIC"},
    "THE DEER ON THE RIDGE":  {"label": "RIDGE"},
}

# Filenames (must exist in static/images/gallery/) to attach to specific
# blog post fixtures, addressed by their `blog_id` for simplicity.
_SEED_BLOG_IMAGES: dict[int, str] = {
    7:  "family.jpg",
    42: "scary_night.jpg",
}


# =====================================================================
# Helpers per concern
# =====================================================================

def _seed_stories(force: bool) -> int:
    """Insert STORY_FIXTURES + their seed covers. Returns # inserted."""
    inserted = 0
    for fixture in STORY_FIXTURES:
        existing = db.session.scalar(
            select(Story).where(Story.title == fixture["title"])
        )
        if existing is not None:
            if not force:
                continue
            db.session.delete(existing)
            db.session.commit()

        story = Story(**fixture)
        db.session.add(story)
        db.session.commit()  # commit so story.id is populated

        cover_spec = _SEED_COVERS.get(fixture["title"])
        if cover_spec:
            ImageRepository.create_for_story(
                story_id=story.id,
                data=_placeholder_cover_svg(cover_spec["label"]),
                mime_type="image/svg+xml",
                filename=f"{cover_spec['label'].lower()}-cover.svg",
                alt_text=f"Placeholder cover labeled {cover_spec['label']}",
                is_cover=True,
            )

        inserted += 1
    return inserted


def _iter_gallery_files() -> Iterable[Path]:
    """Yield every supported image file in the on-disk gallery folder."""
    if not _GALLERY_DIR.is_dir():
        return
    for entry in sorted(os.listdir(_GALLERY_DIR)):
        path = _GALLERY_DIR / entry
        if not path.is_file():
            continue
        if path.suffix.lower() not in _SUPPORTED_GALLERY_EXTS:
            continue
        yield path


def _seed_gallery(force: bool) -> int:
    """Ingest static/images/gallery/* into the gallery table.

    Idempotent: filenames already present in the gallery are skipped
    unless `force=True`, in which case the prior row is deleted first.
    """
    inserted = 0
    for path in _iter_gallery_files():
        existing = db.session.scalar(
            select(Image).where(
                Image.is_gallery.is_(True),
                Image.filename == path.name,
            )
        )
        if existing is not None:
            if not force:
                continue
            db.session.delete(existing)
            db.session.commit()

        ImageRepository.create_from_path(path, is_gallery=True)
        inserted += 1
    return inserted


def _seed_blog_posts(force: bool) -> int:
    """Insert BLOG_POST_FIXTURES, attaching gallery images where mapped.

    Idempotency strategy: identify a fixture row by `(blog_id, text)`.
    Fixtures with text=None are identified by `(blog_id, text=None)`,
    which assumes at most one image-only fixture per blog (true for
    BLOG_POST_FIXTURES today; revisit if that changes).
    """
    inserted = 0
    for fixture in BLOG_POST_FIXTURES:
        text = fixture.get("text")
        if text is None:
            existing_q = select(Post).where(
                Post.blog_id == fixture["blog_id"],
                Post.text.is_(None),
            )
        else:
            existing_q = select(Post).where(
                Post.blog_id == fixture["blog_id"],
                Post.text == text,
            )
        existing = db.session.scalar(existing_q)
        if existing is not None:
            if not force:
                continue
            db.session.delete(existing)
            db.session.commit()

        post = Post(**fixture)
        db.session.add(post)
        db.session.commit()

        # Attach an image if mapped for this blog. We look up a previously
        # ingested gallery image by filename and clone its bytes onto the
        # post, so the post owns its own copy (cleaner cascade semantics).
        seed_image_filename = _SEED_BLOG_IMAGES.get(fixture["blog_id"])
        if seed_image_filename:
            source = db.session.scalar(
                select(Image).where(
                    Image.is_gallery.is_(True),
                    Image.filename == seed_image_filename,
                )
            )
            if source is not None:
                ImageRepository.create_for_post(
                    post_id=post.id,
                    data=source.data,
                    mime_type=source.mime_type,
                    filename=source.filename,
                    alt_text=source.alt_text,
                )

        inserted += 1
    return inserted


# =====================================================================
# Public API
# =====================================================================

def seed_database(
    force: bool = False,
    seed_gallery: bool = True,
    seed_posts: bool = True,
) -> dict:
    """Populate the database with all fixture data.

    Args:
        force:        Replace fixture rows that already exist (destructive
                      for those rows; cascades through their images).
        seed_gallery: Ingest static/images/gallery/* into the gallery
                      table. Off-by-default-False if those files are
                      huge or already imported.
        seed_posts:   Insert BLOG_POST_FIXTURES with sample posts.

    Returns:
        Dict with insertion counts: {"stories": N, "gallery": N, "posts": N}
    """
    return {
        "stories": _seed_stories(force=force),
        "gallery": _seed_gallery(force=force) if seed_gallery else 0,
        "posts":   _seed_blog_posts(force=force) if seed_posts else 0,
    }
