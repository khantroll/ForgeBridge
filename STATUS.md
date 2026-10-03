# Project Status

**Lifecycle:** UVTT FROM A ZIPPED LEVELDB SCENE  
**Implementation started:** Inventory CLI, an importable UVTT file, LevelDB compendium reading, and that file from a zipped LevelDB scene  
**General converter started:** No

The unpacked LevelDB scene is the previous state. This slice is the current state. It writes scene `scene-vault` from `fixtures/synthetic-leveldb-scene.zip` as a UVTT file Arkenforge can import, and grades everything else in that package. The unpacked LevelDB scene and the text scene `scene-crypt` still work. It is not a general Foundry-to-Arkenforge converter.

## What this slice does

`PYTHONPATH=src python3 -m forgebridge fixtures/synthetic-leveldb-scene.zip --uvtt-scene scene-vault --uvtt-out scene-vault.uvtt`

reads the LevelDB pack inside the zip, prints one JSON object with `uvtt` and `loss_report`, and writes only the `uvtt` object to the path given by `--uvtt-out`. That file is the Arkenforge import. The envelope on stdout is the graded report and is not itself an import file.

Zip entries whose names leave the archive are not extracted and are not executed. They are graded unsupported.

The UVTT object uses the same core fields as the folder fixtures, from [Arkenforge's UVTT page](https://arkenforge.com/universal-vtt-files/), read 2026-10-03 (`dateModified` 2026-08-22): map image, square resolution, line of sight, portals, and lights. Grades are `native`, `approximate`, `manual`, and `unsupported`. Notes are in [docs/compatibility/UVTT-SLICE.md](docs/compatibility/UVTT-SLICE.md).

These commands are unchanged:

`PYTHONPATH=src python3 -m forgebridge fixtures/synthetic-leveldb-scene --uvtt-scene scene-vault --uvtt-out scene-vault.uvtt`

`PYTHONPATH=src python3 -m forgebridge fixtures/synthetic-module --uvtt-scene scene-crypt --uvtt-out scene-crypt.uvtt`

No `.uvtt` file is stored as a hand-written artifact. Tests run the writer against the zip, the unpacked LevelDB scene, and the text fixture. LevelDB values are parsed as JSON and are not executed.

## What the earlier work established

Public docs were re-read on 2026-10-03 and written up with citations:

- [docs/research/FOUNDRY.md](docs/research/FOUNDRY.md) — Version 14 document lists, package layout, and the LevelDB key layout used here.
- [docs/research/ARKENFORGE.md](docs/research/ARKENFORGE.md) — import extensions, UVTT fields, v0.5.0.0 / v0.5.1 UI features, and the automation surface that was not found.
- [docs/compatibility/INVENTORY-SPIKE.md](docs/compatibility/INVENTORY-SPIKE.md) — synthetic inventory results, including the LevelDB actor pack.
- [docs/compatibility/UVTT-SLICE.md](docs/compatibility/UVTT-SLICE.md) — the importable UVTT file, the four grades, and the LevelDB scene.

The inventory IR is `schema/inventory-0.1.schema.json`. `fixtures/synthetic-leveldb` is still decoded into the inventory. `fixtures/leveldb-pointer` still fails closed. Unknown fields are retained. Imported JavaScript, macros, HTML, and YAML are not executed.

## Next step

**Beside the UVTT file, also copy out the scene's image and audio assets that Arkenforge's documented import list can take. Not started.**

Those types are already recorded in [docs/research/ARKENFORGE.md](docs/research/ARKENFORGE.md): JPG, PNG, WEBP, GIF, MP4, M4V, WEBM, MP3, OGG, and WAV. The map image is already inside the UVTT file as base64. This step would also write the scene's matching image and audio files next to that UVTT file. It does not invent a note file, a token file, or a campaign format.

## Still out of scope

No framework beyond the standard library and the pinned LevelDB binding. No CI, release workflow, UI, MCP server, LLM provider, or module/system-specific adapters. No invented Arkenforge API. No general converter.
