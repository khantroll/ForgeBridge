# Project Status

**Lifecycle:** RESEARCH SPIKE / INVENTORY ONLY  
**Implementation started:** Inventory CLI and IR schema only  
**Conversion started:** No

The previous lifecycle was PARKED, waiting on other work. This spike is now the current state. It does not start Foundry-to-Arkenforge conversion.

## What this spike established

Public docs were re-read on 2026-10-03 and written up with citations:

- [docs/research/FOUNDRY.md](docs/research/FOUNDRY.md) — Version 14 document lists, module/world/system layout, NeDB versus LevelDB, and the places those pages disagree.
- [docs/research/ARKENFORGE.md](docs/research/ARKENFORGE.md) — import extensions, UVTT fields, v0.5.0.0 / v0.5.1 UI features, and the automation surface that was not found.
- [docs/compatibility/INVENTORY-SPIKE.md](docs/compatibility/INVENTORY-SPIKE.md) — what the synthetic fixtures actually inventory, and the boundary between confirmed Arkenforge imports and unknown file formats.

The inventory IR is `schema/inventory-0.1.schema.json`. It covers the domains in `docs/ARCHITECTURE.md` for counting and provenance only: assets, maps, geometry, presentation, entities, knowledge, audio, tables, behaviors, provenance, and diagnostics. It is not a conversion schema.

The CLI is `PYTHONPATH=src python3 -m forgebridge <module-folder-or-zip>`. It reads the synthetic fixtures under `fixtures/`. It does not execute imported JavaScript, macros, HTML, or YAML. LevelDB directories are detected and not decoded. Unknown fields are retained. Tests cover the schema and the hostile cases.

Arkenforge's only documented structured import/export that this spike can name field-by-field is UVTT. Notes, tokens, rollable tables, playlists, and hotkeys exist in the Toolkit UI as of v0.5.1 (2026-05-14). No public API or file schema for them was found. No Arkenforge output is produced here.

## Next step

**One synthetic scene to a UVTT JSON document, plus a loss report. Not started.**

Use scene `scene-crypt` in `fixtures/synthetic-module`. Write only the fields on Arkenforge's UVTT page, and report everything that file cannot carry (tokens, journals, actors, items, tables, playlists, macros, region behaviors, active effects).

Real Foundry 11+ compendia are LevelDB. This spike does not decode them, so that UVTT candidate stays on a text fixture unless a decoder is added first. A decoder would still be inventory work. It is not this next step, and it is not conversion.

Do not write a MyAssets folder, a hotkey file, an encyclopedia note, or a Foundry module in that milestone.

## Still out of scope

No framework beyond the Python standard library used by the inventory CLI and its tests. No CI, release workflow, UI, MCP server, LLM provider, or module/system-specific adapters. No Foundry-to-Arkenforge conversion.
