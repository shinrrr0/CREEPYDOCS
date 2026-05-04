"""
Blog blueprint: multi-blog posts with random blog redirection.

Architecture:
  - Multiple blogs identified by numeric IDs (1..MAX_BLOGS)
  - Blogs are lazy-created (no empty rows in DB until first post)
  - Multiple users can post to the same blog and see each other's posts
  - /blog/random redirects to a random blog number
  - /blog/<id>  shows posts for blog <id> (empty is OK)
  - /api/blog/<id>/post  AJAX endpoint for the post form

Image bytes go straight into the `images` table via the repository -
no files written to /static/. The post_card template renders them via
`post.image.url` which resolves to the images blueprint.
"""

import random

from flask import (
    Blueprint, abort, current_app, jsonify, redirect, render_template,
    request, url_for,
)

from repositories.post_repository import PostRepository


blog_bp = Blueprint("blog", __name__)


# Same allow-list as before; mime_type is detected from the upload's
# own header which is more accurate than guessing from the extension.
_ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
_ALLOWED_MIME_PREFIXES = ("image/",)


def _is_allowed_upload(file_storage) -> bool:
    """Sanity-check an uploaded werkzeug FileStorage."""
    if not file_storage or not file_storage.filename:
        return False
    name = file_storage.filename.lower()
    if "." not in name:
        return False
    ext = "." + name.rsplit(".", 1)[1]
    if ext not in _ALLOWED_EXTENSIONS:
        return False
    mime = (file_storage.mimetype or "").lower()
    if not mime.startswith(_ALLOWED_MIME_PREFIXES):
        return False
    return True


def _validate_blog_id(blog_id: int) -> bool:
    """Range-check against MAX_BLOGS (1..MAX_BLOGS, inclusive)."""
    max_blogs = current_app.config.get("MAX_BLOGS", 100)
    return 1 <= blog_id <= max_blogs


# ---------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------
@blog_bp.route("/blog/random")
def random_blog():
    """Redirect to a random blog (1..MAX_BLOGS)."""
    max_blogs = current_app.config.get("MAX_BLOGS", 100)
    return redirect(url_for("blog.blog_detail", blog_id=random.randint(1, max_blogs)))


@blog_bp.route("/blog/<int:blog_id>")
def blog_detail(blog_id: int):
    """Posts feed for one blog plus the create-post form."""
    if not _validate_blog_id(blog_id):
        abort(404)

    posts = PostRepository.list_by_blog(blog_id)
    return render_template(
        "blog.html",
        blog_id=blog_id,
        posts=posts,
        nav_sections=current_app.config["NAV_SECTIONS"],
        active_section=None,
    )


# ---------------------------------------------------------------------
# JSON API
# ---------------------------------------------------------------------
@blog_bp.route("/api/blog/<int:blog_id>/post", methods=["POST"])
def create_post(blog_id: int):
    """Create a new post.

    Multipart form fields:
        text   - post body (optional if image present)
        image  - uploaded image file (optional if text present)

    Returns JSON: { success: bool, post?: {...}, error?: str }
    """
    if not _validate_blog_id(blog_id):
        return jsonify({"success": False, "error": "Invalid blog ID"}), 400

    text = request.form.get("text", "").strip()
    file_storage = request.files.get("image")

    image_bytes = None
    image_mime = None
    image_filename = ""

    if file_storage and file_storage.filename:
        if not _is_allowed_upload(file_storage):
            return jsonify({
                "success": False,
                "error": "Only images allowed: jpg, png, gif, webp",
            }), 400

        # Read the entire upload into memory. Fine for small/medium
        # images; for big ones swap to streaming + max_content_length.
        image_bytes = file_storage.read()
        image_mime = file_storage.mimetype
        image_filename = file_storage.filename

    if not text and image_bytes is None:
        return jsonify({
            "success": False,
            "error": "Post must have text or an image",
        }), 400

    post = PostRepository.create(
        blog_id=blog_id,
        text=text or None,
        image_data=image_bytes,
        image_mime_type=image_mime,
        image_filename=image_filename,
    )
    if post is None:
        return jsonify({"success": False, "error": "Failed to create post"}), 500

    return jsonify({
        "success": True,
        "post": {
            "id": post.id,
            "blog_id": post.blog_id,
            "text": post.text,
            "image_url": post.image.url if post.image else None,
            "created_at": post.created_at.isoformat(),
        },
    }), 201


# FUTURE routes:
#   GET    /blog/<int:blog_id>/<int:post_id>          single-post page
#   DELETE /api/blog/<int:blog_id>/post/<int:post_id> delete post
#   POST   /api/blog/<int:blog_id>/post/<int:post_id>/like
