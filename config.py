"""
Application configuration.

NAV_SECTIONS is the single source of truth for the site's sections.
The header and the sidebar both read it, so the navigation panel scales
automatically with whatever you put here.
"""

import os


class Config:
    """Base config. Subclass for ProductionConfig / TestConfig as needed."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # FUTURE: SQLAlchemy DB URI lives here once we wire it up.
    # SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///creepydocs.db")
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ------------------------------------------------------------------
    # Site sections - drives both header nav and sidebar nav.
    # Add/remove items freely; the UI scales to match.
    # `slug` is used in URLs; `label` is displayed.
    # `href` is optional – omit to use the default /section/<slug> URL.
    # ------------------------------------------------------------------
    NAV_SECTIONS = [
        {"slug": "stories",   "label": "ИСТОРИИ"},
        {"slug": "gallery",   "label": "ГАЛЕРЕЯ",   "href": "/gallery"},
        {"slug": "blog",      "label": "БЛОГ",      "href": "/blog"},
    ]
