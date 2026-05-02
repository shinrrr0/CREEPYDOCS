"""
Repositories package.

Each repository is a thin wrapper around the data source (DB or stub).
Routes/services depend on this layer, NOT on raw SQLAlchemy queries
or stub functions. That way, swapping the backend (stub -> real DB)
only touches files in this folder.
"""
