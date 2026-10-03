# UVTT scene slice

This slice writes one synthetic scene as UVTT JSON and a loss report. It is not a general converter. It does not write a campaign, a note, a token file, a hotkey file, a MyAssets folder, or a Foundry module.

```bash
PYTHONPATH=src python3 -m forgebridge fixtures/synthetic-module --uvtt-scene scene-crypt
PYTHONPATH=src python3 -m unittest discover -s tests
```

The command prints one JSON object, `{"uvtt", "loss_report"}`, and exits 0 when `uvtt` matches `schema/uvtt-core.schema.json` and `loss_report` matches `schema/uvtt-loss-report.schema.json`. It exits 1 when the scene is missing, the pack is not text, or the grid is not square. No `.uvtt` file is checked in. The tests generate the object.

Inventory without `--uvtt-scene` is unchanged. See [INVENTORY-SPIKE.md](INVENTORY-SPIKE.md).

## Field list actually used

[Universal VTT files](https://arkenforge.com/universal-vtt-files/), read 2026-10-03. The page `datePublished` is 2022-03-05 and `dateModified` is 2026-08-22. The sample map linked from that page was not downloaded.

The page's core tags, in its own outline, are:

- `format`: a decimal version. The page does not give the number. This slice writes `0.0` and records that as a gap.
- `resolution.map_origin` `{x, y}`
- `resolution.map_size` `{x, y}` in squares
- `resolution.pixels_per_grid`
- `line_of_sight`: an array of `[x][y]` values per object
- `objects_line_of_sight`: the same shape. Tokens and tiles are not placed here.
- `portals`: `position` `{x, y}`, `bounds` (an array of x,y values; the page has no example, so this slice uses `[x, y]` pairs relative to `position` and records that as a gap), `rotation` in radians, `closed`, `freestanding` (the page does not define it; wall segments are written `false`)
- `environment.baked_lighting`
- `environment.ambient_light` (omitted when the scene has no hex ambient color)
- `environment.lights`: `position`, `range`, `intensity`, `color`, `shadows`. This slice writes `position` and `color` only.
- `image`: base64 PNG or WEBP

The same page says Arkenforge adds `software` and `creator` for its own use. Those are not core tags. This slice omits them.

Positions in the file are squares. For `scene-crypt`, Foundry `grid.type` is `1` (`GRID_TYPES.SQUARE` on the Version 14 API, retrieved 2026-10-03) and `grid.size` is 100 pixels, so a 200 by 200 scene is `map_size` 2 by 2. A grid type other than square does not produce a file. The slice refuses to call a hex grid a field of squares.

Door codes `1` and `2` become portals and are not also copied into `line_of_sight`. `ds` `0` is `WALL_DOOR_STATES.CLOSED` and `ds` `1` is `OPEN` (Version 14, retrieved 2026-10-03), which sets `closed`. `LOCKED` (`2`) has no UVTT value, so a locked door would be `closed` true and listed in the loss report. The crypt wall is `door` 1 and `ds` 0. The door code itself is dropped because a portal has no type field.

`LightData.dim`, `bright`, and `shadows` are numbers on the Version 14 class page (retrieved 2026-10-03). That page does not state whether dim and bright are pixels or squares. UVTT `shadows` is a bool. Range, intensity, and shadows are left out.

The image is the level background `assets/crypt.png`, read from inside the package. Paths that leave the package, external URLs, and symlinks are not opened. The thumbnail is not a second image.

## Loss report

The same function builds the report from the inventory of the folder plus the scene document. The headline starts with `Dropped` and counts more dropped lines than carried lines. Dropped lines name the actor, item, journal, roll table, playlist, macros, active effect, token, tiles, sounds, notes, region, flags, unknown scene fields, assets that are not the one image, the YAML pack, package scripts, and manifest fields outside Foundry's set. Script bodies are not copied into the UVTT object or the report, and they are not executed.

## Following step

Point the existing UVTT slice at one scene stored in a synthetic LevelDB pack. That step is named in [STATUS.md](../../STATUS.md) and is not done here. This slice still reads `scene-crypt` from the NeDB text fixture. `fixtures/leveldb-pointer` stays an unreadable trap directory.
