"""
Database seeder.

Reads STORY_FIXTURES from services/stub_data.py and writes them to
the database. Idempotent by default - fixtures whose title already
exists are skipped (use force=True to replace them).

Also attaches a placeholder cover image to one of the seed stories so
the image-storage path can be exercised end-to-end without external
asset files.

Invoke via the `flask seed-db` CLI command (see cli.py).
"""

from sqlalchemy import select

from models.database import db
from models.story import Story
from repositories.image_repository import ImageRepository
from services.stub_data import STORY_FIXTURES


# ---------------------------------------------------------------------
# Placeholder image generation.
# Building the SVG inline keeps the repo self-contained - no asset
# files needed to demonstrate that the image pipeline works.
# Swap this for real fixture files once art is ready.
# ---------------------------------------------------------------------
def _placeholder_svg(label: str) -> bytes:
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


# Map fixture titles to seed-image specs. Add entries here to attach
# placeholder images to other fixtures.
_SEED_IMAGES: dict[str, dict] = {
    "THE STATIC ON THE LINE": {
        "label": "STATIC",
        "alt_text": "Placeholder cover with the word STATIC",
        "is_cover": True,
    },
    "THE DEER ON THE RIDGE": {
        "label": "RIDGE",
        "alt_text": "Placeholder cover with the word RIDGE",
        "is_cover": True,
    },
}


def seed_database(force: bool = False) -> int:
    """Populate the database with fixture stories and their covers.

    Args:
        force: If True, replace any existing stories whose titles match
               a fixture (deletes the old row + cascade-deletes its
               images, then re-inserts).

    Returns:
        Number of stories inserted.
    """
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

        # Attach a placeholder cover if one is configured for this title.
        image_spec = _SEED_IMAGES.get(fixture["title"])
        if image_spec:
            ImageRepository.create(
                data=_placeholder_svg(image_spec["label"]),
                mime_type="image/svg+xml",
                filename=f"{image_spec['label'].lower()}-cover.svg",
                story_id=story.id,
                alt_text=image_spec.get("alt_text"),
                is_cover=image_spec.get("is_cover", False),
            )

        inserted += 1

    return inserted
