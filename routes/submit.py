"""
Submit blueprint: user-submitted creepypasta stories.

Routes:
    GET  /submit            - submission form + feed of submitted pastas
    POST /api/submit        - create a new story (JSON response)

Stories submitted here are saved with section_slug='submit' so they
can be filtered separately from the prefab content while still appearing
in the global feed on the home page.
"""

from flask import (
    Blueprint, current_app, jsonify, render_template, request,
)

from repositories.image_repository import ImageRepository
from repositories.story_repository import StoryRepository


submit_bp = Blueprint("submit", __name__)

# Section slug used for all user-submitted pastas.
# None = no section tag → pastas appear in the global feed on the home
# page (StoryRepository.list_all) at the top, alongside prefab content.
_SECTION_SLUG = "stories"

_ALLOWED_MIME_PREFIXES = ("image/",)
_ALLOWED_EXTENSIONS   = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


def _is_allowed_image(file_storage) -> bool:
    if not file_storage or not file_storage.filename:
        return False
    name = file_storage.filename.lower()
    if "." not in name:
        return False
    ext = "." + name.rsplit(".", 1)[1]
    if ext not in _ALLOWED_EXTENSIONS:
        return False
    mime = (file_storage.mimetype or "").lower()
    return mime.startswith(_ALLOWED_MIME_PREFIXES)


# -----------------------------------------------------------------------
# Page
# -----------------------------------------------------------------------

@submit_bp.route("/submit")
def submit_page():
    """Submission form + global story feed (all stories, newest first)."""
    stories = StoryRepository.list_all()
    from repositories.comment_repository import CommentRepository
    return render_template(
        "submit.html",
        stories=stories,
        comment_counts=CommentRepository.counts_for_stories(
            [s.id for s in stories]
        ),
        nav_sections=current_app.config["NAV_SECTIONS"],
        active_section=_SECTION_SLUG,
    )


# -----------------------------------------------------------------------
# API
# -----------------------------------------------------------------------

@submit_bp.route("/api/submit", methods=["POST"])
def create_submission():
    """Create a new user-submitted pasta.

    Accepts multipart/form-data with fields:
        title   (required)  - story title
        body    (required)  - story text
        author  (optional)  - author display name
        image   (optional)  - cover image file

    Returns JSON: { success, story?: {...}, error?: str }
    """
    title  = request.form.get("title",  "").strip()
    body   = request.form.get("body",   "").strip()
    author = request.form.get("author", "").strip() or None
    file   = request.files.get("image")

    # --- Validation ---
    if not title:
        return jsonify({"success": False, "error": "Заголовок не может быть пустым"}), 400

    max_title = 200
    if len(title) > max_title:
        return jsonify({
            "success": False,
            "error": f"Заголовок слишком длинный (максимум {max_title} символов)",
        }), 400

    if not body:
        return jsonify({"success": False, "error": "Текст истории не может быть пустым"}), 400

    image_data, image_mime, image_filename = None, None, ""
    if file and file.filename:
        if not _is_allowed_image(file):
            return jsonify({
                "success": False,
                "error": "Только изображения: jpg, png, gif, webp",
            }), 400
        image_data     = file.read()
        image_mime     = file.mimetype
        image_filename = file.filename

    # --- Create story ---
    story = StoryRepository.create(
        title=title,
        body=body,
        author=author,
        section_slug=_SECTION_SLUG,
    )

    # --- Attach cover image ---
    cover_url = None
    if image_data:
        img = ImageRepository.create(
            data=image_data,
            mime_type=image_mime,
            filename=image_filename,
            story_id=story.id,
            is_cover=True,
            alt_text=title,
        )
        cover_url = img.url

    return jsonify({
        "success": True,
        "story": {
            "id":         story.id,
            "title":      story.title,
            "body":       story.body,
            "author":     story.author,
            "cover_url":  cover_url,
            "created_at": story.created_at.isoformat(),
        },
    }), 201
