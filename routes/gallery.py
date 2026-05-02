"""
Gallery blueprint: image masonry feed.

Thin view functions – fetch data through ImageRepository, pass to templates.
Business logic (filtering, pagination, ordering) lives in the repository
and service layers, not here.
"""

from flask import Blueprint, current_app, render_template

from repositories.image_repository import ImageRepository


gallery_bp = Blueprint("gallery", __name__)


@gallery_bp.route("/gallery")
def gallery():
    """Masonry image feed – all gallery images in random order."""
    images = ImageRepository.list_all()
    return render_template(
        "gallery.html",
        images=images,
        nav_sections=current_app.config["NAV_SECTIONS"],
        active_section="gallery",
    )


# FUTURE routes to add:
#   @gallery_bp.route("/gallery/<int:image_id>")         – full detail page
#   @gallery_bp.route("/api/gallery")                    – JSON for infinite scroll
#   @gallery_bp.route("/api/gallery/page/<int:page>")    – paginated JSON
#   @gallery_bp.route("/gallery/upload", methods=["POST"])  – image submission
