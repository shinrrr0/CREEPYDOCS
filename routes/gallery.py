"""
Gallery blueprint: image masonry feed.

Thin view functions - fetch data through ImageRepository, pass to
templates. Business logic (filtering, pagination, ordering) lives in
the repository, not here.
"""

import random

from flask import Blueprint, current_app, render_template

from repositories.image_repository import ImageRepository


gallery_bp = Blueprint("gallery", __name__)


@gallery_bp.route("/gallery")
def gallery():
    """Masonry image feed - all gallery images in shuffled order."""
    images = ImageRepository.list_gallery()
    # Shuffle for the organic masonry feel; ordering in the DB is just
    # a deterministic tie-breaker so two visits look different.
    random.shuffle(images)
    return render_template(
        "gallery.html",
        images=images,
        nav_sections=current_app.config["NAV_SECTIONS"],
        active_section="gallery",
    )


# FUTURE routes:
#   GET  /gallery/<int:image_id>            full detail page
#   GET  /api/gallery                       JSON for infinite scroll
#   POST /gallery/upload                    image submission
