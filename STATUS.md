# Project Status

**Lifecycle:** UVTT SCENE SLICE  
**Implementation started:** Inventory CLI, plus one scene written as UVTT JSON  
**General converter started:** No

The inventory spike is the previous state. This slice is the current state. It writes scene `scene-crypt` as UVTT and lists what that file cannot carry. It is not a general Foundry-to-Arkenforge converter.

## What this slice does

`PYTHONPATH=src python3 -m forgebridge fixtures/synthetic-module --uvtt-scene scene-crypt`

prints one JSON object with `uvtt` and `loss_report`. The UVTT object uses only the core fields on [Arkenforge's UVTT page](https://arkenforge.com/universal-vtt-files/), read 2026-10-03 (`dateModified` 2026-08-22). The loss report is produced by that same command. Notes, citations, and the field list actually written are in [docs/compatibility/UVTT-SLICE.md](docs/compatibility/UVTT-SLICE.md).

No `.uvtt` file is stored as a hand-written artifact. Tests run the writer against `fixtures/synthetic-module`.

The inventory command from the previous spike is unchanged:

`PYTHONPATH=src python3 -m forgebridge <module-folder-or-zip>`

## What the inventory spike established

Public docs were re-read on 2026-10-03 and written up with citations:

- [docs/research/FOUNDRY.md](docs/research/FOUNDRY.md) — Version 14 document lists, module/world/system layout, NeDB versus LevelDB, and the places those pages disagree.
- [docs/research/ARKENFORGE.md](docs/research/ARKENFORGE.md) — import extensions, UVTT fields, v0.5.0.0 / v0.5.1 UI features, and the automation surface that was not found.
- [docs/compatibility/INVENTORY-SPIKE.md](docs/compatibility/INVENTORY-SPIKE.md) — what the synthetic fixtures inventory, and which Arkenforge surfaces are confirmed.

The inventory IR is `schema/inventory-0.1.schema.json`. LevelDB directories are detected and not decoded. Unknown fields are retained. Imported JavaScript, macros, HTML, and YAML are not executed.

## Next step

**Decode a synthetic LevelDB compendium into the inventory. Not started.**

Real Foundry 11+ compendia are LevelDB. This slice still does not decode them, so the UVTT writer stays on the text fixture. The next step is a decoder for a LevelDB database generated as a synthetic fixture in this repo, adding those documents to the inventory.

`fixtures/leveldb-pointer` is not that database. Its bytes are a trap for a decoder that treats the directory as text or as code, and they stay undecoded.

That decoder is still inventory work. It does not write Arkenforge notes, tokens, campaign files, a MyAssets folder, a hotkey file, or a Foundry module. It is not a general converter.

## Still out of scope

No framework beyond the Python standard library used by this CLI and its tests. No CI, release workflow, UI, MCP server, LLM provider, or module/system-specific adapters. No Arkenforge campaign output. No general converter.
