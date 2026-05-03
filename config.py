"""
Application configuration.

NAV_SECTIONS is the single source of truth for the site's nav. Header
and sidebar both read it, so the navigation panel scales automatically
with whatever you put here.
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
    # Site sections - drives both header nav and sidebar nav.
    # `slug` is used in URLs and as Story.section_slug; `label` is shown.
    # ------------------------------------------------------------------
    NAV_SECTIONS = [
        {"slug": "stories",   "label": "STORIES"},
        {"slug": "archive",   "label": "ARCHIVE"},
        {"slug": "rituals",   "label": "RITUALS"},
        {"slug": "lost",      "label": "LOST FILES"},
        {"slug": "submit",    "label": "SUBMIT"},
        {"slug": "about",     "label": "ABOUT"},
    ]

    @classmethod
    def valid_section_slugs(cls) -> set[str]:
        """Helper for repository write-side validation."""
        return {s["slug"] for s in cls.NAV_SECTIONS}
