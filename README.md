# CreepyDocs

Flask + SQLAlchemy archive of creepypastas with a public image gallery,
a multi-blog area, and story comments. Black-grey-red palette, modular codebase intended
for parallel development.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Database (one-time, then re-run seed-db whenever fixtures change):
export FLASK_APP=app:create_app    # Windows: set FLASK_APP=app:create_app
flask init-db                      # create tables
flask seed-db                      # stories + ingest static gallery + sample posts

python app.py                      # http://127.0.0.1:5000
```

The default DB is SQLite at `instance/creepydocs.db`. Override with the
`DATABASE_URL` env var to point at Postgres / MySQL / etc.

## CLI

| Command                       | Effect                                                     |
|-------------------------------|------------------------------------------------------------|
| `flask init-db`               | Create tables (idempotent).                                |
| `flask seed-db`               | Insert fixtures + ingest gallery folder (idempotent).      |
| `flask seed-db --force`       | Replace fixture rows whose titles match (destructive).     |
| `flask seed-db --skip-gallery`| Skip ingest of `static/images/gallery/`.                   |
| `flask seed-db --skip-posts`  | Skip blog post fixtures.                                   |
| `flask reset-db`              | Drop everything, recreate, re-seed (destructive).          |
| `flask add-comment <story_id>` | Add a plain-text story comment.                            |
| `flask list-comments <story_id>`| List comments for a story.                                |
| `flask delete-comment <id>`    | Delete one comment.                                        |

## Project layout

```
app.py                   Flask factory + entry point
config.py                Config: DB URI, NAV_SECTIONS, MAX_BLOGS
cli.py                   Click commands

models/
  database.py            SQLAlchemy `db` instance + DeclarativeBase
  story.py               Story ORM model (+ cover_image / gallery_images)
  post.py                Post ORM model (blog posts)
  image.py               Image ORM model (binary blobs, multi-owner)
  comment.py             Comment ORM model (plain-text story comments)

repositories/
  story_repository.py    Story DB access
  post_repository.py     Post DB access (creates Post + Image atomically)
  image_repository.py    Image DB access (per-owner helper methods)
  comment_repository.py  Comment DB access + validation

services/
  stub_data.py           STORY_FIXTURES + BLOG_POST_FIXTURES
  seeder.py              Inserts fixtures + ingests gallery folder

routes/
  main.py                /  and  /section/<slug>            (story feed)
  gallery.py             /gallery                            (masonry)
  blog.py                /blog/random, /blog/<id>, POST API  (multi-blog)
  images.py              /image/<id>                         (binary serve)
  comments.py            /api/stories/<id>/comments           (JSON API)

templates/               base.html + components/ + per-page templates
static/                  css/, js/, fonts/, images/ (seed source)
```

## Data model

```
stories                                 posts
  id                                      id
  title                                   blog_id (indexed)
  body                                    text (nullable)
  author                                  created_at
  section_slug (indexed)                 └──> images (cascade)
  created_at (indexed)
  └──> images (cascade)
  └──> comments (cascade)

comments
  id
  story_id (FK->stories, ON DELETE CASCADE)
  body
  author
  created_at (indexed)

images
  id
  story_id  (FK->stories, ON DELETE CASCADE, nullable)
  post_id   (FK->posts,   ON DELETE CASCADE, nullable)
  is_gallery (bool, indexed)   show in /gallery feed
  is_cover   (bool)            mark as story cover
  filename, mime_type, title, alt_text, width, height, position
  data (BLOB)
  created_at (indexed)
```

The same `images` table serves four roles, distinguished by which FK /
flag is set:

| Role             | Condition                                    |
|------------------|----------------------------------------------|
| Story image      | `story_id IS NOT NULL`                       |
| Story cover      | `story_id IS NOT NULL AND is_cover = TRUE`   |
| Blog post image  | `post_id IS NOT NULL`                        |
| Public gallery   | `is_gallery = TRUE` (FKs may be null)        |
| Standalone asset | all FKs null and `is_gallery = FALSE`        |

`Image.url` returns `url_for('images.serve', image_id=self.id)` so
templates never construct asset paths themselves.

## How feature areas talk to the DB

- **Stories** (`/`, `/section/<slug>`):
  `StoryRepository.list_all` / `list_by_section`. Each Story exposes
  `.cover_image` and `.gallery_images` for the template.
- **Comments** (`GET/POST /api/stories/<id>/comments`):
  `CommentRepository` validates, stores, lists, counts, and deletes
  plain-text comments. Cyrillic JSON responses are emitted without
  `\uXXXX` escaping for easier debugging.
- **Gallery** (`/gallery`):
  `ImageRepository.list_gallery()` returns rows where `is_gallery=True`.
  Seeder ingests every supported file in `static/images/gallery/` on
  first run.
- **Blog** (`/blog/random`, `/blog/<id>`, `POST /api/blog/<id>/post`):
  `PostRepository.create()` writes the Post and its (optional) Image
  in one transaction; the upload's bytes are stored directly in the
  `images` table - no new files written to disk by the request handler.
  `post.image.url` points at the serve route.
- **Image bytes**: `routes/images.py` returns the blob with proper
  `Content-Type` and a year-long `Cache-Control: immutable` (image
  contents are immutable per id).

## Where to add things

- **New nav section** → add a dict to `Config.NAV_SECTIONS`. If it has
  a custom URL, set `"href": "/whatever"`; otherwise it routes through
  `main.section`.
- **New repository method** → add it next to existing ones; routes and
  templates depend only on public method names.
- **New columns on Story / Post / Image** → edit the ORM model, then
  either `flask reset-db` in dev or wire up Flask-Migrate / Alembic
  (commented stub in `requirements.txt`).
- **New page** → blueprint in `routes/`, template extending `base.html`,
  reuse `components/content_block.html` / `image_card.html` /
  `post_card.html` as appropriate.

## What this iteration does NOT do (intentionally)

- No reactions or ratings. Comments are available through the JSON API and CLI; a full inline thread UI can be added next.
- No auth / login / submissions form for stories.
- No admin UI (image / post management is via repositories).
- No pagination, search, infinite scroll.

Each has a marked extension point in the relevant file.
