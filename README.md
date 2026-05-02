# CreepyDocs

Flask-based archive of creepypastas. Black-grey-red palette, modular
codebase intended for parallel development.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000`.

## Project layout

```
app.py                   # Flask factory + entry point
config.py                # Config; NAV_SECTIONS drives header & sidebar
models/                  # Domain types (Story dataclass; later SQLAlchemy)
repositories/            # DB access wrappers - swap stub for real DB here
services/                # Non-DB business logic + the current stub data
routes/                  # Flask blueprints (one per feature area)
templates/
  base.html              # Page shell
  components/            # header, sidebar, sidebar_trigger, content_block
  index.html             # Feed page
static/
  css/                   # base, fonts, header, sidebar, content, animations
  js/                    # main, header_scroll, sidebar, content_expand
  fonts/                 # Drop "another danger" font file here
```

## Where to add things

- **New section in nav** → add a dict to `Config.NAV_SECTIONS`. Header +
  sidebar both update; a `/section/<slug>` route exists already.
- **Real DB** → uncomment Flask-SQLAlchemy in `requirements.txt` +
  `models/database.py`, replace stub calls in
  `repositories/story_repository.py`. Public method signatures stay
  the same so routes/templates don't need to change.
- **New page** → add a route in `routes/`, a template extending
  `base.html`. Reuse `components/content_block.html`.
- **Comments / reactions on a story** → extend
  `templates/components/content_block.html` below the marked
  "FUTURE" comment. The card grows down naturally.

## What this iteration does NOT do (intentionally, per spec)

- No comments, reactions, ratings on stories.
- No real database — `repositories/story_repository.py` reads from
  `services/stub_data.py`.
- No settings UI — sidebar reserves space for them only.
- No auth, submissions, search.

Each of those has a marked extension point in the relevant file.
