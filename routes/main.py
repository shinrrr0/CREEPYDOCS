"""
Main blueprint: home page and section listings.

Keep view functions thin: they fetch data through repositories and pass
it to templates. Don't put business logic here - extract it into
services/ if it grows.
"""

from flask import Blueprint, current_app, render_template, abort, redirect, url_for

from repositories.story_repository import StoryRepository


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Home: feed of all stories, newest first."""
    stories = StoryRepository.list_all()
    return render_template(
        "index.html",
        stories=stories,
        nav_sections=current_app.config["NAV_SECTIONS"],
        active_section=None,
    )


@main_bp.route("/story/random")
def random_story():
    """Redirect to a random story. Returns 404 if the DB is empty."""
    story = StoryRepository.get_random()
    if story is None:
        abort(404)
    # When a dedicated story page lands, change target to 'main.story_detail'.
    # For now we anchor-scroll to the story card on the home feed.
    return redirect(url_for("main.index") + f"#story-{story.id}")


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
        nav_sections=nav_sections,
        active_section=slug,
    )


# FUTURE routes to add:
#   @main_bp.route("/story/<int:story_id>")     - full single-story page
#   @main_bp.route("/submit", methods=["POST"]) - new submissions
#   @main_bp.route("/api/stories")              - JSON for infinite scroll
