"""
Main blueprint: home page and section listings.

Keep view functions thin: they fetch data through repositories and pass
it to templates. Don't put business logic here - extract it into
services/ if it grows.
"""

from flask import Blueprint, current_app, render_template, abort

from repositories.comment_repository import CommentRepository
from repositories.story_repository import StoryRepository


main_bp = Blueprint("main", __name__)


def _comment_counts_for(stories) -> dict:
    """Pre-compute story_id -> comment count for a feed of stories.

    Centralised here because both index() and section() need it. One
    grouped query instead of N per-story queries.
    """
    return CommentRepository.counts_for_stories([s.id for s in stories])


@main_bp.route("/")
def index():
    """Home: feed of all stories, newest first."""
    stories = StoryRepository.list_all()
    return render_template(
        "index.html",
        stories=stories,
        comment_counts=_comment_counts_for(stories),
        nav_sections=current_app.config["NAV_SECTIONS"],
        active_section=None,
    )


@main_bp.route("/section/<slug>")
def section(slug: str):
    """Per-section feed. Slug must match an entry in Config.NAV_SECTIONS."""
    nav_sections = current_app.config["NAV_SECTIONS"]
    if not any(s["slug"] == slug for s in nav_sections):
        abort(404)

    stories = StoryRepository.list_by_section(slug)
    return render_template(
        "index.html",
        stories=stories,
        comment_counts=_comment_counts_for(stories),
        nav_sections=nav_sections,
        active_section=slug,
    )


# FUTURE routes to add:
#   @main_bp.route("/story/<int:story_id>")     - full single-story page
#   @main_bp.route("/submit", methods=["POST"]) - new submissions
#   @main_bp.route("/api/stories")              - JSON for infinite scroll
