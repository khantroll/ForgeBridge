# Project Status

**Lifecycle:** IMPORTABLE UVTT FILE  
**Implementation started:** Inventory CLI, plus one scene written as a UVTT file Arkenforge can import  
**General converter started:** No

The UVTT scene slice is the previous state. This slice is the current state. It writes scene `scene-crypt` as a bare UVTT JSON file and grades everything else in the synthetic module. It is not a general Foundry-to-Arkenforge converter.

## What this slice does

`PYTHONPATH=src python3 -m forgebridge fixtures/synthetic-module --uvtt-scene scene-crypt --uvtt-out scene-crypt.uvtt`

prints one JSON object with `uvtt` and `loss_report`, and writes only the `uvtt` object to the path given by `--uvtt-out`. That file is the Arkenforge import. The envelope on stdout is the graded report and is not itself an import file.

The UVTT object uses the core fields on [Arkenforge's UVTT page](https://arkenforge.com/universal-vtt-files/), read 2026-10-03 (`dateModified` 2026-08-22): map image, square resolution, line of sight, portals, and lights. Grades are `native`, `approximate`, `manual`, and `unsupported`, taken from that page and the public Toolkit notes in [docs/research/ARKENFORGE.md](docs/research/ARKENFORGE.md). Notes, citations, and the field list actually written are in [docs/compatibility/UVTT-SLICE.md](docs/compatibility/UVTT-SLICE.md).

No `.uvtt` file is stored as a hand-written artifact. Tests run the writer against `fixtures/synthetic-module`.

The inventory command from the earlier spike is unchanged:

`PYTHONPATH=src python3 -m forgebridge <module-folder-or-zip>`

## What the earlier spikes established

Public docs were re-read on 2026-10-03 and written up with citations:

- [docs/research/FOUNDRY.md](docs/research/FOUNDRY.md) — Version 14 document lists, module/world/system layout, NeDB versus LevelDB, and the places those pages disagree.
- [docs/research/ARKENFORGE.md](docs/research/ARKENFORGE.md) — import extensions, UVTT fields, v0.5.0.0 / v0.5.1 UI features, and the automation surface that was not found.
- [docs/compatibility/INVENTORY-SPIKE.md](docs/compatibility/INVENTORY-SPIKE.md) — what the synthetic fixtures inventory, and which Arkenforge surfaces are confirmed.
- [docs/compatibility/UVTT-SLICE.md](docs/compatibility/UVTT-SLICE.md) — the importable file and the four grades.

The inventory IR is `schema/inventory-0.1.schema.json`. On this branch, LevelDB directories are detected and not decoded. A separate draft decodes a synthetic LevelDB pack into the inventory and is not part of this branch. Unknown fields are retained. Imported JavaScript, macros, HTML, and YAML are not executed.

## Next step

**Apply this same importable UVTT file and graded loss report to one scene stored in a synthetic LevelDB pack. Not started.**

This branch still reads the scene from the text fixture. The following step points the same writer at one scene inside a synthetic LevelDB pack, once that pack can be inventoried. It does not add a campaign folder, a note file, a token file, a hotkey file, or a MyAssets layout.

## Still out of scope

No framework beyond the Python standard library used by this CLI and its tests. No CI, release workflow, UI, MCP server, LLM provider, or module/system-specific adapters. No invented Arkenforge API. No general converter.
