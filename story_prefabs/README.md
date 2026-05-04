# story_prefabs/

Drop story folders here. On the next dev-server restart (or any time
you run `flask import-prefabs` or `import_prefabs.bat`), the importer
walks every subfolder and inserts what it finds.

## Folder layout

```
story_prefabs/
  my_story_slug/                # any folder name; the title comes from meta.json
    meta.json                   # required - see schema below
    body.txt                    # required - story body, UTF-8
    cover.jpg                   # optional - cover image (jpg/png/webp/gif)
    gallery/                    # optional - extra images attached to the story
        photo1.jpg
        photo2.png
        ...
```

## meta.json schema

```json
{
  "title": "MANDATORY UNIQUE TITLE",
  "author": "optional",
  "section_slug": "stories",
  "cover_alt": "optional alt text for the cover image"
}
```

Only `title` is required. `section_slug` should match an entry in
`Config.NAV_SECTIONS` (currently the only story section is `"stories"`).

## Idempotency

Stories are matched by `title` - if a story with the same title already
exists in the DB, the importer skips it. Pass `--force` to replace it
(the old story is cascade-deleted, including its images, and re-inserted).

## See also

- `images_prefabs/` for plain gallery image dumps (no metadata, just files).
- `import_prefabs.bat` (Windows) or `flask import-prefabs` to trigger
  the import manually.
