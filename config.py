"""
Application configuration.

NAV_SECTIONS is the single source of truth for the site's nav. Header
and sidebar both read it, so the navigation panel scales automatically
with whatever you put here.

MAX_BLOGS is the upper bound for blog IDs. Users can access any blog
from 1 to MAX_BLOGS. Blogs are created lazily: empty blogs don't exist
in the DB until the first post is created.
"""

import os
from pathlib import Path

# Project root - used to locate the SQLite file in instance/.
_PROJECT_DIR = Path(__file__).resolve().parent
_INSTANCE_DIR = _PROJECT_DIR / "instance"


class Config:
    """Base config. Subclass for ProductionConfig / TestConfig as needed."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # ------------------------------------------------------------------
    # Database.
    # Default: SQLite file at instance/creepydocs.db (Flask creates the
    # instance/ folder for us). Override with the DATABASE_URL env var
    # for Postgres / MySQL / etc.
    # ------------------------------------------------------------------
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{_INSTANCE_DIR / 'creepydocs.db'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Echoes SQL to stdout when True - useful in dev, noisy in prod.
    SQLALCHEMY_ECHO = bool(int(os.environ.get("SQLALCHEMY_ECHO", "0")))

    # ------------------------------------------------------------------
    # SQLite connection pool & engine options.
    #
    # NullPool closes every connection immediately after use instead of
    # keeping idle connections alive.  This is the recommended setting
    # for SQLite file databases because:
    #   • SQLite is not designed for connection pooling (it is a single
    #     process / single writer model).
    #   • On Windows, idle pooled connections hold a Windows file-level
    #     lock that prevents DB Browser (and other tools) from opening
    #     or reading the database file while Flask is running.
    #   • Even on Linux the pooled idle connection keeps a BEGIN-level
    #     read snapshot, so WAL-mode changes written by the CLI command
    #     (import_prefabs.bat → flask import-prefabs) are invisible to
    #     that connection until its transaction ends.
    # ------------------------------------------------------------------
    SQLALCHEMY_ENGINE_OPTIONS = {
        "poolclass": __import__("sqlalchemy.pool", fromlist=["NullPool"]).NullPool,
    }

    # ------------------------------------------------------------------
    # Site sections - drives both header nav and sidebar nav.
    # `slug` is used in URLs; `label` is displayed; `href` overrides the
    # default /section/<slug> URL when present.
    # ------------------------------------------------------------------
    NAV_SECTIONS = [
        {"slug": "stories",   "label": "ИСТОРИИ"},
        {"slug": "gallery",   "label": "ГАЛЕРЕЯ", "href": "/gallery"},
        {"slug": "blog",      "label": "БЛОГ",    "href": "/blog/random"},
    ]

    # ------------------------------------------------------------------
    # Blog configuration
    # ------------------------------------------------------------------
    # Maximum number of blogs. Each blog is identified by a number from
    # 1 to MAX_BLOGS. Blogs are created lazily - they don't need to
    # exist in DB until the first post. The "random blog" button picks
    # a random number between 1 and MAX_BLOGS.
    MAX_BLOGS = 100

    # ------------------------------------------------------------------
    # Comments configuration
    # ------------------------------------------------------------------
    # Application-level cap on a comment body length. The schema column
    # itself is TEXT (unlimited) - this cap is enforced in
    # CommentRepository.create and the JSON route.
    COMMENT_MAX_LENGTH = 4000

    # Cap on the optional author display name. Over-long names are trimmed
    # by the repository so the field degrades gracefully.
    COMMENT_AUTHOR_MAX_LENGTH = 80

    @classmethod
    def valid_section_slugs(cls) -> set[str]:
        """Helper for repository write-side validation."""
        return {s["slug"] for s in cls.NAV_SECTIONS}
