# CreepyDocs

Flask + SQLAlchemy archive of creepypastas. Black-grey-red palette,
modular codebase intended for parallel development.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Database (one-time, then re-run seed-db whenever fixtures change):
export FLASK_APP=app:create_app    # Windows: set FLASK_APP=app:create_app
flask init-db                      # create tables
flask seed-db                      # insert sample stories + placeholder covers

python app.py                      # http://127.0.0.1:5000
```

The default DB is SQLite at `instance/creepydocs.db`. Override with the
`DATABASE_URL` env var to point at Postgres / MySQL / etc.

CLI:

| Command              | Effect                                                   |
|----------------------|----------------------------------------------------------|
| `flask init-db`      | Create tables (idempotent, no-op if they exist).         |
| `flask seed-db`      | Insert fixture stories + covers (idempotent).            |
| `flask seed-db --force` | Replace fixtures whose titles match (destructive).    |
| `flask reset-db`     | Drop everything, recreate, re-seed (destructive).        |

## Project layout

```
app.py                   Flask factory + entry point
config.py                Config; NAV_SECTIONS drives header & sidebar
cli.py                   Click commands (init-db, seed-db, reset-db)

models/
  database.py            SQLAlchemy `db` instance + DeclarativeBase
  story.py               Story ORM model
  image.py               Image ORM model (binary blob in DB)

repositories/
  story_repository.py    All Story DB access
  image_repository.py    All Image DB access (CRUD, cover swap, reorder)

services/
  stub_data.py           STORY_FIXTURES (dev seed data)
  seeder.py              Inserts fixtures + generates placeholder SVG covers

routes/
  main.py                / and /section/<slug>
  images.py              /image/<id>  (serves binary blob with mime + cache)

templates/               base.html + components/ + index.html
static/                  css/, js/, fonts/
```

## Data model

```
stories
  id, title, body, author, section_slug, created_at
  └─ images (1..N, ON DELETE CASCADE)

images
  id, story_id (nullable), filename, mime_type, alt_text,
  width, height, position, is_cover, data (BLOB), created_at
```

- `Image.story_id` is nullable so the table can also hold standalone
  site assets (banners, decorative art).
- `Image.data` is a `LargeBinary` — image bytes live in the DB. Backups
  and replication cover everything in one shot. To migrate to filesystem
  / object storage later, swap `data` for a `storage_key` column and
  update the two methods in `ImageRepository.create*` plus the route in
  `routes/images.py`. Templates use `image.url` (a model property) so
  they don't need to change.
- `Image.is_cover` is a soft single-cover-per-story flag. The repository
  enforces it via `set_as_cover()` / `_clear_existing_cover()`; the schema
  doesn't, so bulk inserts stay simple.

## How images get displayed

Templates only call `image.url`, which returns `url_for('images.serve',
image_id=image.id)`. The image-serving route reads the bytes and returns
them with the correct `Content-Type` and aggressive `Cache-Control`.

## Where to add things

- **New section in nav** → add a dict to `Config.NAV_SECTIONS`.
- **New repository method** → add it next to existing ones; keep the
  routes/templates depending only on the public method names.
- **New columns on Story / Image** → edit the ORM model, then either:
  - run `flask reset-db` in dev, or
  - add Flask-Migrate / Alembic for real migrations
    (`requirements.txt` has it commented in).
- **New page** → add a route in `routes/`, a template extending
  `base.html`. Reuse `components/content_block.html`.
- **Comments / reactions on a story** → extend
  `templates/components/content_block.html` below the marked
  "FUTURE" comment, then add `models/comment.py`,
  `repositories/comment_repository.py`, and a relationship on Story.
  Not in scope for this iteration.

## What this iteration does NOT do (intentionally)

- No comments, reactions, ratings.
- No upload UI for images — programmatic ingest only via
  `ImageRepository.create()` / `.create_from_path()`.
- No auth, search, pagination.

Each of those has a marked extension point in the relevant file.
