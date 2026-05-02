"""
Image stub data source.

Scans static/images/gallery/ and returns Image objects built from the
filenames found there. Drop new images into that folder and they appear
automatically – no code changes needed.

FUTURE: Replace get_all_images_stub / get_image_by_id_stub with real
SQLAlchemy queries. The ImageRepository calls only these two functions,
so the swap is a one-file change.
"""

import os
import random
from typing import List, Optional

from models.image import Image


# ---------------------------------------------------------------------------
# Resolve gallery directory relative to this file – works regardless of cwd.
# FUTURE: move this path into Config once the upload system is in place.
# ---------------------------------------------------------------------------
_GALLERY_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "static", "images", "gallery")
)

_SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


def _filename_to_title(filename: str) -> str:
    """Convert 'creepy_face.jpg' → 'CREEPY FACE'."""
    stem, _ = os.path.splitext(filename)
    return stem.replace("_", " ").replace("-", " ").upper()


def get_all_images_stub(shuffle: bool = True) -> List[Image]:
    """
    Return Image objects for every supported file in _GALLERY_DIR.

    shuffle=True randomises order so the masonry grid feels organic.
    Pass shuffle=False in tests for deterministic ordering.

    FUTURE (SQLAlchemy):
        from sqlalchemy import func
        query = Image.query.order_by(func.random())
        return query.all()
    """
    images: List[Image] = []

    if not os.path.isdir(_GALLERY_DIR):
        return images  # directory missing – return empty; no crash

    entries = sorted(os.listdir(_GALLERY_DIR))
    idx = 1
    for fname in entries:
        _, ext = os.path.splitext(fname)
        if ext.lower() not in _SUPPORTED_EXTENSIONS:
            continue
        images.append(
            Image(
                id=idx,
                filename=fname,
                title=_filename_to_title(fname),
                alt=_filename_to_title(fname),
            )
        )
        idx += 1

    if shuffle:
        random.shuffle(images)
    return images


def get_image_by_id_stub(image_id: int) -> Optional[Image]:
    """
    Single-image lookup stub.

    Scans the full list – acceptable for a small local gallery.

    FUTURE (SQLAlchemy):
        return Image.query.get(image_id)
    """
    for img in get_all_images_stub(shuffle=False):
        if img.id == image_id:
            return img
    return None
