"""
Database setup.

Currently inactive - we use an in-memory stub via services/stub_data.py.
When ready, uncomment the SQLAlchemy lines below and call db.init_app(app)
from create_app() in app.py.
"""

# FUTURE: replace this stub with a real SQLAlchemy instance.
#
# from flask_sqlalchemy import SQLAlchemy
# db = SQLAlchemy()
#
# Then in app.py:
#     from models.database import db
#     db.init_app(app)
#
# And run migrations or db.create_all() inside an app context.

db = None  # placeholder so imports do not fail elsewhere
