# Project Status

**Lifecycle:** LEVELDB INVENTORY  
**Implementation started:** Inventory CLI, an importable UVTT file, and LevelDB compendium reading  
**General converter started:** No

The importable UVTT file is on main. This branch keeps that file and reads a synthetic LevelDB compendium into the same inventory as the NeDB packs. It is not a general Foundry-to-Arkenforge converter.

## What this decode does

`PYTHONPATH=src python3 -m forgebridge fixtures/synthetic-leveldb`

prints the inventory JSON. The pack `packs/actors` is `storage: "leveldb"`, `decoded: true`, with two Actor documents and one Folder document. The Actor `Level Mummy` includes its embedded effect. Unknown fields such as `homebrewRule` stay on the document. The dependency is `plyvel==1.5.1` in `requirements.txt`, a binding to LevelDB. Foundry's CLI writes this database shape with classic-level.

The key layout is the one in foundryvtt-cli 0.0.6 `lib/package.mjs`, retrieved 2026-10-03: UTF-8 keys, JSON values, primary keys `!<collection>!<id>`, embedded keys `!<collection>.<field>!<parentId>.<embeddedId>`. Values are parsed as JSON. They are not executed.

`fixtures/leveldb-pointer` is still not a LevelDB database. Opening it fails, the `.ldb` bytes are not read as text, and `should-not-import` stays out of the inventory. NeDB `.db` packs are unchanged.

The UVTT command from main is unchanged and still uses the text scene fixture:

`PYTHONPATH=src python3 -m forgebridge fixtures/synthetic-module --uvtt-scene scene-crypt --uvtt-out scene-crypt.uvtt`

That command prints one JSON object with `uvtt` and `loss_report`, and writes only the `uvtt` object to the path given by `--uvtt-out`. That file is the Arkenforge import. The envelope on stdout is the graded report and is not itself an import file.

The UVTT object uses the core fields on [Arkenforge's UVTT page](https://arkenforge.com/universal-vtt-files/), read 2026-10-03 (`dateModified` 2026-08-22): map image, square resolution, line of sight, portals, and lights. Grades are `native`, `approximate`, `manual`, and `unsupported`, taken from that page and the public Toolkit notes in [docs/research/ARKENFORGE.md](docs/research/ARKENFORGE.md). Notes, citations, and the field list actually written are in [docs/compatibility/UVTT-SLICE.md](docs/compatibility/UVTT-SLICE.md).

No `.uvtt` file is stored as a hand-written artifact. Tests run the writer against `fixtures/synthetic-module`.

## What the earlier work established

Public docs were re-read on 2026-10-03 and written up with citations:

- [docs/research/FOUNDRY.md](docs/research/FOUNDRY.md) — Version 14 document lists, package layout, and the LevelDB key layout used here.
- [docs/research/ARKENFORGE.md](docs/research/ARKENFORGE.md) — import extensions, UVTT fields, v0.5.0.0 / v0.5.1 UI features, and the automation surface that was not found.
- [docs/compatibility/INVENTORY-SPIKE.md](docs/compatibility/INVENTORY-SPIKE.md) — synthetic inventory results, including this LevelDB pack.
- [docs/compatibility/UVTT-SLICE.md](docs/compatibility/UVTT-SLICE.md) — the importable UVTT file and the four grades.

The inventory IR is `schema/inventory-0.1.schema.json`. Unknown fields are retained. Imported JavaScript, macros, HTML, and YAML are not executed.

## Next step

**Apply the importable UVTT file and graded loss report to one scene stored in a synthetic LevelDB pack. Not started.**

The UVTT writer still reads `scene-crypt` from the NeDB text fixture. The inventory can already read `fixtures/synthetic-leveldb`. The next step passes one scene document from a synthetic LevelDB pack through the existing `--uvtt-scene` command. It does not add a campaign folder, a note file, a token file, a hotkey file, or a MyAssets layout.

## Still out of scope

No framework beyond the standard library and the pinned LevelDB binding. No CI, release workflow, UI, MCP server, LLM provider, or module/system-specific adapters. No invented Arkenforge API. No general converter.
