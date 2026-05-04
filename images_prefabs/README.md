# images_prefabs/

Drop image files here. On the next dev-server restart (or any time
you run `flask import-prefabs` or `import_prefabs.bat`), each file
is loaded into the DB and added to the public `/gallery` feed.

## Layout

Just files. Subfolders are ignored.

```
images_prefabs/
    creepy_face.jpg
    abandoned_room.png
    static.gif
    ...
```

Display title is auto-generated from the filename:
`creepy_face.jpg` -> `CREEPY FACE`. To override the title, use the
one-off CLI command instead:

```
flask add-gallery-image path/to/file.jpg --title "CUSTOM TITLE"
```

## Supported extensions

`.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`

## Idempotency

Gallery images are matched by `filename` - re-importing the same file
skips it. Pass `--force` to replace.

## See also

- `story_prefabs/` for stories (text + optional images).
- `flask add-gallery-image PATH` for adding one image with custom metadata.
