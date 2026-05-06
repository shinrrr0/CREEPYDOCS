"""
Comments blueprint.

Endpoints
    GET  /api/stories/<id>/comments    list comments for one story
    POST /api/stories/<id>/comments    create a new comment

JSON in, JSON out. No multipart - comments are plain text only per
the spec, so there are no file uploads to handle.

Encoding notes (the Cyrillic-must-not-break requirement from the
team-lead):
  - The HTTP request body is parsed as UTF-8 by default in both
    `request.get_json()` (which respects the request charset, falling
    back to UTF-8) and `request.form` (Werkzeug uses the request
    charset, which is UTF-8 unless overridden).
  - Responses go through `jsonify`. App-level config sets
    `app.json.ensure_ascii = False` so non-ASCII characters appear
    literal in the response body instead of as \\uXXXX escapes - both
    forms are valid JSON and decode identically in JS, but the
    literal form is easier to inspect in DevTools / curl.
"""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from repositories.comment_repository import CommentRepository
from repositories.story_repository import StoryRepository


comments_bp = Blueprint("comments", __name__)


# =====================================================================
# Routes
# =====================================================================

@comments_bp.route("/api/stories/<int:story_id>/comments", methods=["GET"])
def list_comments(story_id: int):
    """Return every comment attached to one story, oldest-first."""
    if StoryRepository.get_by_id(story_id) is None:
        return jsonify({"success": False, "error": "Story not found"}), 404

    comments = CommentRepository.list_for_story(story_id)
    return jsonify({
        "success": True,
        "story_id": story_id,
        "count": len(comments),
        "comments": [c.to_dict() for c in comments],
    })


@comments_bp.route("/api/stories/<int:story_id>/comments", methods=["POST"])
def create_comment(story_id: int):
    """Create a new comment on a story.

    Accepts JSON `{"body": "...", "author": "..."}` (preferred) or the
    same fields as form data for forgiving curl smoke tests.
    """
    if StoryRepository.get_by_id(story_id) is None:
        return jsonify({"success": False, "error": "Story not found"}), 404

    payload = _read_payload()
    body = (payload.get("body") or "").strip()
    author = (payload.get("author") or "").strip() or None

    # 400-class validation that we want to surface with a specific
    # message - the repository's None return is reserved for "anything
    # else went wrong" so the user always gets a useful error.
    if not body:
        return jsonify({
            "success": False,
            "error": "Текст комментария не может быть пустым",
        }), 400

    max_len = int(current_app.config.get("COMMENT_MAX_LENGTH", 4000))
    if len(body) > max_len:
        return jsonify({
            "success": False,
            "error": (
                f"Комментарий слишком длинный (максимум {max_len} символов)"
            ),
        }), 400

    comment = CommentRepository.create(
        story_id=story_id, body=body, author=author,
    )
    if comment is None:
        return jsonify({
            "success": False,
            "error": "Не удалось создать комментарий",
        }), 500

    # Returning the persisted shape lets the JS prepend the new comment
    # to the thread without a follow-up GET round trip.
    return jsonify({"success": True, "comment": comment.to_dict()}), 201


# =====================================================================
# Helpers
# =====================================================================

def _read_payload() -> dict:
    """Accept JSON or form-urlencoded bodies transparently.

    Werkzeug decodes form data with the request charset (UTF-8 by
    default) and `request.get_json(force=True, silent=True)` decodes
    JSON bodies as UTF-8, so non-ASCII content survives either route.
    """
    if request.is_json:
        data = request.get_json(force=True, silent=True) or {}
        return data if isinstance(data, dict) else {}
    if request.form:
        return request.form.to_dict()
    return {}


# FUTURE routes:
#   DELETE /api/stories/<id>/comments/<comment_id>   moderator delete
#   PATCH  /api/stories/<id>/comments/<comment_id>   edit own comment
#   GET    /api/stories/<id>/comments?page=N         paginated thread
