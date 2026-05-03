"""
Images blueprint.

Serves stored image binaries by id at /image/<id>. Templates use
`image.url` (a property on the model) to get the right path - they
don't construct the URL themselves, so changing this route only
requires changing the model property.
"""

from flask import Blueprint, Response, abort

from repositories.image_repository import ImageRepository


images_bp = Blueprint("images", __name__)


# Cache stored images aggressively - they are immutable for a given id.
# When you want to "edit" an image, upload a new one and update the
# referencing row instead of mutating the existing blob, so this cache
# header stays correct.
_CACHE_HEADER = "public, max-age=31536000, immutable"


@images_bp.route("/image/<int:image_id>")
def serve(image_id: int):
    """Stream a stored image. 404 if the id does not exist."""
    image = ImageRepository.get_by_id(image_id)
    if image is None:
        abort(404)

    response = Response(image.data, mimetype=image.mime_type)
    response.headers["Cache-Control"] = _CACHE_HEADER
    response.headers["Content-Length"] = str(image.size_bytes)
    # Hint a download filename if one was preserved.
    if image.filename:
        response.headers["Content-Disposition"] = (
            f'inline; filename="{image.filename}"'
        )
    return response


# FUTURE routes:
#   POST /image                upload a new image
#   DELETE /image/<id>         admin delete
#   GET   /image/<id>/thumb    on-the-fly resized variant
