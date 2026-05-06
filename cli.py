"""
Flask CLI commands.

Wired into the app via `register_cli(app)` in app.py. After exporting
`FLASK_APP=app:create_app`, the dev workflow is:

    # Schema and seed data
    flask init-db                  # create tables (idempotent)
    flask seed-db                  # insert sample data (idempotent)
    flask seed-db --force          # replace fixtures with matching titles
    flask reset-db                 # drop everything, recreate, re-seed

    # Content management (Path 1 from the chat)
    flask add-story \
        --title "TITLE" \
        --body-file path/to/body.txt \
        --author "anonymous" \
        --section-slug stories \
        --cover path/to/cover.jpg     # cover is optional

    flask add-gallery-image path/to/photo.jpg \
        --title "DISPLAY TITLE" \
        --alt "alt text"

    flask list-stories
    flask delete-story <id>

    # Comments
    flask add-comment <story_id> --body "текст"          # inline body
    flask add-comment <story_id> --body-file body.txt    # from a file (UTF-8)
    flask add-comment <story_id> --body "..." --author "anon"
    flask list-comments <story_id>
    flask delete-comment <comment_id>

    # Bulk import from prefab folders (story_prefabs/, images_prefabs/)
    flask import-prefabs           # idempotent
    flask import-prefabs --force   # replace existing rows that match

For real-world schema migrations beyond drop/recreate, add Flask-Migrate
(Alembic) - see README for the recipe.
"""

from pathlib import Path

import click
from flask import Flask
from flask.cli import with_appcontext

from models.database import db
from repositories.comment_repository import CommentRepository
from repositories.image_repository import ImageRepository
from repositories.story_repository import StoryRepository
from services.seeder import seed_database
from services.prefab_importer import import_all_prefabs


# =====================================================================
# Schema / seed
# =====================================================================

@click.command("init-db")
@with_appcontext
def init_db_cmd():
    """Create all tables. Existing tables are left intact."""
    db.create_all()
    click.echo("Tables created.")


@click.command("seed-db")
@click.option(
    "--force", is_flag=True,
    help="Replace fixtures with matching titles (destructive for those rows).",
)
@click.option(
    "--skip-gallery", is_flag=True,
    help="Do not ingest images from static/images/gallery/.",
)
@click.option(
    "--skip-posts", is_flag=True,
    help="Do not seed sample blog posts.",
)
@with_appcontext
def seed_db_cmd(force: bool, skip_gallery: bool, skip_posts: bool):
    """Insert fixture data. Idempotent unless --force is set."""
    result = seed_database(
        force=force,
        seed_gallery=not skip_gallery,
        seed_posts=not skip_posts,
    )
    click.echo(
        f"Inserted {result['stories']} stories, "
        f"{result['gallery']} gallery images, "
        f"{result['posts']} blog posts."
    )


@click.command("reset-db")
@with_appcontext
def reset_db_cmd():
    """Drop all tables, recreate, and re-seed. Destructive."""
    db.drop_all()
    db.create_all()
    result = seed_database()
    click.echo(
        f"DB reset; inserted {result['stories']} stories, "
        f"{result['gallery']} gallery images, "
        f"{result['posts']} blog posts."
    )


# =====================================================================
# Content management - one-off commands
# =====================================================================

@click.command("add-story")
@click.option("--title", required=True, help="Story title (must be unique).")
@click.option(
    "--body-file",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    required=True,
    help="Path to a UTF-8 .txt file containing the story body.",
)
@click.option("--author", default=None, help="Author name (optional).")
@click.option(
    "--section-slug", default=None,
    help="Section slug from Config.NAV_SECTIONS (default: stories).",
)
@click.option(
    "--cover",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    default=None,
    help="Path to a cover image file (optional).",
)
@with_appcontext
def add_story_cmd(title, body_file, author, section_slug, cover):
    """Create a new story from a body text file, optionally with a cover."""
    body = Path(body_file).read_text(encoding="utf-8")
    story = StoryRepository.create(
        title=title,
        body=body,
        author=author,
        section_slug=section_slug,
    )
    click.echo(f"Created story id={story.id} title={title!r}")

    if cover:
        img = ImageRepository.create_from_path(
            cover, story_id=story.id, is_cover=True,
        )
        click.echo(f"Attached cover image id={img.id} ({Path(cover).name})")


@click.command("add-gallery-image")
@click.argument(
    "path",
    type=click.Path(exists=True, dir_okay=False, readable=True),
)
@click.option("--title", default=None, help="Display title (default: filename).")
@click.option("--alt", default=None, help="Alt text for accessibility.")
@with_appcontext
def add_gallery_image_cmd(path, title, alt):
    """Add an image file to the public /gallery feed."""
    img = ImageRepository.create_from_path(
        path,
        is_gallery=True,
        title=title,
        alt_text=alt,
    )
    click.echo(f"Created gallery image id={img.id} filename={Path(path).name}")


@click.command("list-stories")
@with_appcontext
def list_stories_cmd():
    """Show every story currently in the DB, newest first."""
    stories = StoryRepository.list_all()
    if not stories:
        click.echo("No stories.")
        return
    for s in stories:
        cover_marker = "[cover]" if s.cover_image else "       "
        author = f"by {s.author}" if s.author else ""
        click.echo(
            f"  {s.id:>4}  {s.created_at.strftime('%Y-%m-%d')}  "
            f"{cover_marker}  {s.title!r:<40} {author}"
        )


@click.command("delete-story")
@click.argument("story_id", type=int)
@with_appcontext
def delete_story_cmd(story_id):
    """Delete a story by id. Cascades to its images and comments."""
    if StoryRepository.delete(story_id):
        click.echo(f"Deleted story {story_id}")
    else:
        click.echo(f"Story {story_id} not found", err=True)
        raise click.exceptions.Exit(code=1)


@click.command("import-prefabs")
@click.option(
    "--force", is_flag=True,
    help="Replace existing rows that match by title (stories) or filename "
         "(gallery images).",
)
@click.option(
    "--quiet", is_flag=True,
    help="Suppress per-item progress output.",
)
@with_appcontext
def import_prefabs_cmd(force: bool, quiet: bool):
    """Bulk import from story_prefabs/ and images_prefabs/ folders."""
    result = import_all_prefabs(force=force, verbose=not quiet)
    click.echo(
        f"Imported {result['stories']} stories "
        f"(+{result['story_images']} attached images), "
        f"{result['gallery_images']} gallery images."
    )


# =====================================================================
# Comments - one-off commands
# =====================================================================

@click.command("add-comment")
@click.argument("story_id", type=int)
@click.option(
    "--body",
    default=None,
    help="Comment body (use --body-file for long text or non-Latin scripts).",
)
@click.option(
    "--body-file",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    default=None,
    help="Path to a UTF-8 .txt file containing the comment body.",
)
@click.option(
    "--author",
    default=None,
    help='Author display name (default: anon).',
)
@with_appcontext
def add_comment_cmd(story_id, body, body_file, author):
    """Add a comment to a story.

    One of --body / --body-file is required. Use --body-file for any
    multi-line / multi-paragraph content - shells often mangle quoted
    Cyrillic on Windows, while reading from a UTF-8 file is reliable.
    """
    if body is None and body_file is None:
        click.echo("Either --body or --body-file is required.", err=True)
        raise click.exceptions.Exit(code=2)
    if body is not None and body_file is not None:
        click.echo("Pass only one of --body / --body-file.", err=True)
        raise click.exceptions.Exit(code=2)

    if body_file is not None:
        body = Path(body_file).read_text(encoding="utf-8")

    comment = CommentRepository.create(
        story_id=story_id, body=body, author=author,
    )
    if comment is None:
        click.echo(
            f"Failed to add comment to story {story_id} "
            f"(empty body, too long, or story does not exist).",
            err=True,
        )
        raise click.exceptions.Exit(code=1)

    click.echo(
        f"Created comment id={comment.id} on story {story_id} "
        f"by {comment.author or 'anon'}"
    )


@click.command("list-comments")
@click.argument("story_id", type=int)
@with_appcontext
def list_comments_cmd(story_id):
    """Show every comment on a story, oldest-first."""
    comments = CommentRepository.list_for_story(story_id)
    if not comments:
        click.echo(f"No comments for story {story_id}.")
        return
    for c in comments:
        stamp = c.created_at.strftime("%Y-%m-%d %H:%M")
        author = c.author or "anon"
        click.echo(f"  {c.id:>4}  {stamp}  {author!r:<20}  {c.body!r}")


@click.command("delete-comment")
@click.argument("comment_id", type=int)
@with_appcontext
def delete_comment_cmd(comment_id):
    """Delete a comment by id."""
    if CommentRepository.delete(comment_id):
        click.echo(f"Deleted comment {comment_id}")
    else:
        click.echo(f"Comment {comment_id} not found", err=True)
        raise click.exceptions.Exit(code=1)


# =====================================================================
# Wiring
# =====================================================================

def register_cli(app: Flask) -> None:
    """Wire CLI commands into the Flask app."""
    for cmd in (
        init_db_cmd,
        seed_db_cmd,
        reset_db_cmd,
        add_story_cmd,
        add_gallery_image_cmd,
        list_stories_cmd,
        delete_story_cmd,
        import_prefabs_cmd,
        # Comments
        add_comment_cmd,
        list_comments_cmd,
        delete_comment_cmd,
    ):
        app.cli.add_command(cmd)
