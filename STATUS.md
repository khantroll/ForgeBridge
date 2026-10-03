# Project Status

**Lifecycle:** UVTT FROM LEVELDB  
**Implementation started:** Inventory CLI, an importable UVTT file, LevelDB compendium reading, and one LevelDB scene written as that file  
**General converter started:** No

The LevelDB inventory decode is the previous state. This slice is the current state. It writes scene `scene-vault` from a synthetic LevelDB pack as a UVTT file Arkenforge can import, and grades everything else in that package. The text scene `scene-crypt` still works. It is not a general Foundry-to-Arkenforge converter.

## What this slice does

`PYTHONPATH=src python3 -m forgebridge fixtures/synthetic-leveldb-scene --uvtt-scene scene-vault --uvtt-out scene-vault.uvtt`

reads the LevelDB pack `packs/scenes`, prints one JSON object with `uvtt` and `loss_report`, and writes only the `uvtt` object to the path given by `--uvtt-out`. That file is the Arkenforge import. The envelope on stdout is the graded report and is not itself an import file.

The UVTT object uses the same core fields as the text fixture, from [Arkenforge's UVTT page](https://arkenforge.com/universal-vtt-files/), read 2026-10-03 (`dateModified` 2026-08-22): map image, square resolution, line of sight, portals, and lights. Grades are `native`, `approximate`, `manual`, and `unsupported`. Notes are in [docs/compatibility/UVTT-SLICE.md](docs/compatibility/UVTT-SLICE.md).

The text command is unchanged:

`PYTHONPATH=src python3 -m forgebridge fixtures/synthetic-module --uvtt-scene scene-crypt --uvtt-out scene-crypt.uvtt`

No `.uvtt` file is stored as a hand-written artifact. Tests run the writer against both fixtures. LevelDB values are parsed as JSON and are not executed.

## What the earlier work established

Public docs were re-read on 2026-10-03 and written up with citations:

- [docs/research/FOUNDRY.md](docs/research/FOUNDRY.md) — Version 14 document lists, package layout, and the LevelDB key layout used here.
- [docs/research/ARKENFORGE.md](docs/research/ARKENFORGE.md) — import extensions, UVTT fields, v0.5.0.0 / v0.5.1 UI features, and the automation surface that was not found.
- [docs/compatibility/INVENTORY-SPIKE.md](docs/compatibility/INVENTORY-SPIKE.md) — synthetic inventory results, including the LevelDB actor pack.
- [docs/compatibility/UVTT-SLICE.md](docs/compatibility/UVTT-SLICE.md) — the importable UVTT file, the four grades, and the LevelDB scene.

The inventory IR is `schema/inventory-0.1.schema.json`. `fixtures/synthetic-leveldb` is still decoded into the inventory. `fixtures/leveldb-pointer` still fails closed. Unknown fields are retained. Imported JavaScript, macros, HTML, and YAML are not executed.

## Next step

**Write this same UVTT file from a scene inside a zipped module whose scene pack is LevelDB. Not started.**

The writer still reads a module folder and refuses a zip archive. Inventory can already read a zipped LevelDB pack. The next step is that zip path for one scene, with the same fields and grades. It does not add a note file, a token file, an audio package, or a campaign folder.

## Still out of scope

No framework beyond the standard library and the pinned LevelDB binding. No CI, release workflow, UI, MCP server, LLM provider, or module/system-specific adapters. No invented Arkenforge API. No general converter.
