# Project Status

**Lifecycle:** LEVELDB INVENTORY  
**Implementation started:** Inventory CLI, one UVTT scene slice, and LevelDB compendium reading  
**General converter started:** No

The UVTT scene slice is the previous state. This decode is the current state. A synthetic LevelDB compendium is read into the same inventory as the NeDB packs. It is not a general Foundry-to-Arkenforge converter.

## What this decode does

`PYTHONPATH=src python3 -m forgebridge fixtures/synthetic-leveldb`

prints the inventory JSON. The pack `packs/actors` is `storage: "leveldb"`, `decoded: true`, with two Actor documents and one Folder document. The Actor `Level Mummy` includes its embedded effect. Unknown fields such as `homebrewRule` stay on the document. The dependency is `plyvel==1.5.1` in `requirements.txt`, a binding to LevelDB. Foundry's CLI writes this database shape with classic-level.

The key layout is the one in foundryvtt-cli 0.0.6 `lib/package.mjs`, retrieved 2026-10-03: UTF-8 keys, JSON values, primary keys `!<collection>!<id>`, embedded keys `!<collection>.<field>!<parentId>.<embeddedId>`. Values are parsed as JSON. They are not executed.

`fixtures/leveldb-pointer` is still not a LevelDB database. Opening it fails, the `.ldb` bytes are not read as text, and `should-not-import` stays out of the inventory. NeDB `.db` packs are unchanged.

The UVTT command from the previous slice is unchanged and still uses the text scene fixture:

`PYTHONPATH=src python3 -m forgebridge fixtures/synthetic-module --uvtt-scene scene-crypt`

## What the earlier work established

- [docs/research/FOUNDRY.md](docs/research/FOUNDRY.md) — Version 14 document lists, package layout, and the LevelDB key layout used here.
- [docs/research/ARKENFORGE.md](docs/research/ARKENFORGE.md) — import extensions, UVTT fields, and the automation surface that was not found.
- [docs/compatibility/INVENTORY-SPIKE.md](docs/compatibility/INVENTORY-SPIKE.md) — synthetic inventory results, including this LevelDB pack.
- [docs/compatibility/UVTT-SLICE.md](docs/compatibility/UVTT-SLICE.md) — one text scene written as UVTT, plus the loss report.

## Next step

**Point the existing UVTT slice at one scene stored in a synthetic LevelDB pack. Not started.**

The UVTT writer still reads `scene-crypt` from the NeDB text fixture. The next step is one scene document inside a synthetic LevelDB pack, passed through the existing `--uvtt-scene` command and its loss report.

That is still one scene. It does not write Arkenforge notes, tokens, campaign files, a MyAssets folder, a hotkey file, or a Foundry module. It is not a general converter.

## Still out of scope

No framework beyond the standard library and the pinned LevelDB binding. No CI, release workflow, UI, MCP server, LLM provider, or module/system-specific adapters. No Arkenforge campaign output. No general converter.
