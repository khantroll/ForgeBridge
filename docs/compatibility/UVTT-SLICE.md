# Importable UVTT file

This slice writes one synthetic scene as a UVTT file Arkenforge can import, plus a graded loss report. It is not a general converter. It does not write a campaign, a note file, a token file, a hotkey file, a MyAssets folder, or a Foundry module. It does not invent an Arkenforge API.

```bash
PYTHONPATH=src python3 -m forgebridge fixtures/synthetic-module --uvtt-scene scene-crypt --uvtt-out scene-crypt.uvtt
PYTHONPATH=src python3 -m unittest discover -s tests
```

Stdout is one JSON object, `{"uvtt", "loss_report"}`. `--uvtt-out` writes only the `uvtt` object. That file is the import. The envelope is not: it has `loss_report`, which is outside the UVTT core fields.

The command exits 0 when `uvtt` matches `schema/uvtt-core.schema.json` and `loss_report` matches `schema/uvtt-loss-report.schema.json`. It exits 1 when the scene is missing, the pack is not text, or the grid is not square. It exits 2 when a schema check fails, and it does not write the file in that case. No `.uvtt` file is checked in. The tests generate the object.

Inventory without `--uvtt-scene` is unchanged. See [INVENTORY-SPIKE.md](INVENTORY-SPIKE.md).

## Field list actually used

[Universal VTT files](https://arkenforge.com/universal-vtt-files/), read 2026-10-03. The page `datePublished` is 2022-03-05 and `dateModified` is 2026-08-22. The sample map linked from that page was not downloaded.

The page's core tags, in its own outline, are:

- `format`: a decimal version. The page does not give the number. This slice writes `0.0` and grades that approximate.
- `resolution.map_origin` `{x, y}`
- `resolution.map_size` `{x, y}` in squares
- `resolution.pixels_per_grid`
- `line_of_sight`: an array of `[x][y]` values per object
- `objects_line_of_sight`: the same shape. Tokens and tiles are not placed here.
- `portals`: `position` `{x, y}`, `bounds` (an array of x,y values; the page has no example, so this slice uses `[x, y]` pairs relative to `position` and grades that approximate), `rotation` in radians, `closed`, `freestanding` (the page does not define it; wall segments are written `false`)
- `environment.baked_lighting`
- `environment.ambient_light` (omitted when the scene has no hex ambient color)
- `environment.lights`: `position`, `range`, `intensity`, `color`, `shadows`. This slice writes `position` and `color` only.
- `image`: base64 PNG or WEBP

The same page says Arkenforge adds `software` and `creator` for its own use. Those are not core tags. This slice omits them.

Positions in the file are squares. For `scene-crypt`, Foundry `grid.type` is `1` (`GRID_TYPES.SQUARE` on the Version 14 API, retrieved 2026-10-03) and `grid.size` is 100 pixels, so a 200 by 200 scene is `map_size` 2 by 2. A grid type other than square does not produce a file. The slice refuses to call a hex grid a field of squares.

Door codes `1` and `2` become portals and are not also copied into `line_of_sight`. `ds` `0` is `WALL_DOOR_STATES.CLOSED` and `ds` `1` is `OPEN` (Version 14, retrieved 2026-10-03), which sets `closed`. `LOCKED` (`2`) has no UVTT value, so a locked door would be `closed` true and graded approximate. The crypt wall is `door` 1 and `ds` 0. The door code itself is approximate because a portal has no type field. The portal geometry is native.

`LightData.dim`, `bright`, and `shadows` are numbers on the Version 14 class page (retrieved 2026-10-03). That page does not state whether dim and bright are pixels or squares. UVTT `shadows` is a bool. Range, intensity, and shadows are left out and graded approximate. Position and hex color are native.

The image is the level background `assets/crypt.png`, read from inside the package. Paths that leave the package, external URLs, and symlinks are not opened. The thumbnail is not a second image.

Confirmed loose imports, from the animated-map FAQ (`dateModified` 2025-12-10) and the v0.5.0.0 notes (2026-01-13), are JPG, PNG, WEBP, GIF, MP4, M4V, WEBM, MP3, OGG, and WAV. Those files are not bundled beside the UVTT image. No package layout for that was published, so they stay in the Foundry package and are graded manual.

## Grades

The same function builds the report from the inventory of the folder plus the scene document. The headline starts with `Unsupported` and counts unsupported, manual, approximate, and native lines. Each summary starts with `Native:`, `Approximate:`, `Manual:`, or `Unsupported:`.

The grades use [docs/research/ARKENFORGE.md](../research/ARKENFORGE.md), retrieved 2026-10-03. They are the best grade those public pages support.

| Grade | Meaning on this slice |
|---|---|
| native | A documented UVTT field filled in the file: the map image, square resolution, `baked_lighting`, a portal's position and closed flag, a line-of-sight segment, and a light's position and color. |
| approximate | Written or deliberately omitted with a documented mismatch: `format` 0.0, portal bounds, `freestanding`, omitted `software` and `creator`, door type, locked or unknown door state, light dim/bright/shadows, grid distance and units, thumbnail, and a scene image that is not the chosen background. |
| manual | A Toolkit UI feature with no file this slice can write. Scene and level names. Tokens (UVTT cannot carry selectable tokens; tokens exist in the UI). In-package tiles. Notes. Ambient audio. Actors, journals, items (5e note fields, not a general item system), rollable tables, playlists, and macros (hotkeys; the macro is not executed). Loose image and audio files that are not the one map image. |
| unsupported | No documented equivalent, or the data cannot be used. Regions and their scripts. Active effects. Flags, unknown scene fields, and other retained fields such as `homebrewRule`. Hostile, missing, and external assets. Package scripts (not executed), styles, the YAML pack, and extra manifest keys. A wall with no geometry, or a light with no position and hex color. |

Script bodies are not copied into the UVTT object or the report, and they are not executed.

## Following step

Apply this same importable UVTT file and graded loss report to one scene stored in a synthetic LevelDB pack. Not this slice. The inventory reads `fixtures/synthetic-leveldb`. This writer still reads `scene-crypt` from the NeDB text fixture. `fixtures/leveldb-pointer` stays an unreadable trap directory.
