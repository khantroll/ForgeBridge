# Foundry VTT package and document notes

Retrieved 2026-10-03 from public Foundry pages. This spike did not install Foundry and did not open a commercial module. Where two public pages disagree, both are quoted and the inventory code follows the narrower, safer reading.

## Sources

| Source | What was used | Date |
|---|---|---|
| [API documentation, Version 14](https://foundryvtt.com/api/) | Primary, world, and embedded document lists; scene, wall, macro, journal-page, and level fields | Retrieved 2026-10-03. The pages identify themselves as Version 14 and do not show a separate last-updated date. |
| [`CONST.PRIMARY_DOCUMENT_TYPES`](https://foundryvtt.com/api/variables/CONST.PRIMARY_DOCUMENT_TYPES.html) | Primary document list | Version 14, retrieved 2026-10-03 |
| [`CONST.WORLD_DOCUMENT_TYPES`](https://foundryvtt.com/api/variables/CONST.WORLD_DOCUMENT_TYPES.html) | Documents that may exist in a world | Version 14, retrieved 2026-10-03 |
| [`CONST.COMPENDIUM_DOCUMENT_TYPES`](https://foundryvtt.com/api/variables/CONST.COMPENDIUM_DOCUMENT_TYPES.html) | Documents that may exist in a compendium | Version 14, retrieved 2026-10-03 |
| [`CONST.EMBEDDED_DOCUMENT_TYPES`](https://foundryvtt.com/api/variables/CONST.EMBEDDED_DOCUMENT_TYPES.html) | Embedded document list, including `Item` and `Level` | Version 14, retrieved 2026-10-03 |
| [`CONST.PACKAGE_TYPES`](https://foundryvtt.com/api/variables/CONST.PACKAGE_TYPES.html) | `world`, `system`, `module` | Version 14, retrieved 2026-10-03 |
| [`CONST.MACRO_TYPES`](https://foundryvtt.com/api/variables/CONST.MACRO_TYPES.html) and [`MacroData`](https://foundryvtt.com/api/interfaces/foundry.documents.types.MacroData.html) | `script` and `chat`; `command` is a string | Version 14, retrieved 2026-10-03 |
| [`CONST.WALL_DOOR_TYPES`](https://foundryvtt.com/api/variables/CONST.WALL_DOOR_TYPES.html) and [`WallData`](https://foundryvtt.com/api/interfaces/foundry.documents.types.WallData.html) | Door codes and wall fields | Version 14, retrieved 2026-10-03 |
| [`SceneData`](https://foundryvtt.com/api/interfaces/foundry.documents.types.SceneData.html), [`LevelData`](https://foundryvtt.com/api/interfaces/foundry.documents.types.LevelData.html), [`SceneEnvironmentData`](https://foundryvtt.com/api/interfaces/foundry.documents.types.SceneEnvironmentData.html) | Where a scene stores grid, walls, lights, and the background texture | Version 14, retrieved 2026-10-03 |
| [`JournalEntryPageData`](https://foundryvtt.com/api/interfaces/foundry.documents.types.JournalEntryPageData.html) | Page `text`, `image`, `video`, and `src` | Version 14, retrieved 2026-10-03 |
| [`PackageCompendiumData`](https://foundryvtt.com/api/interfaces/foundry.packages.types.PackageCompendiumData.html) | Pack `name`, `label`, `path`, `type`, optional `system` | Version 14, retrieved 2026-10-03 |
| [Introduction to Module Development](https://foundryvtt.com/article/module-development/) | `module.json`, folder layout, scripts, packs | Retrieved 2026-10-03. No last-updated field was found. |
| [Introduction to System Development](https://foundryvtt.com/article/system-development/) | `system.json` | Retrieved 2026-10-03. No last-updated field was found. |
| [Managing User Data](https://foundryvtt.com/article/user-data/) and [Game Worlds](https://foundryvtt.com/article/game-worlds/) | User-data tree and world folder | Retrieved 2026-10-03. No last-updated field was found. |
| [Content Packaging Guide](https://foundryvtt.com/article/packaging-guide/) | Module distribution, compendium export, NeDB versus V11 folders | Retrieved 2026-10-03. A screenshot filename on the page contains `2021-12-17`. That is not an article date. |
| [Compendium Packs](https://foundryvtt.com/article/compendium/) | One document type per pack, except adventures; JSON import | Retrieved 2026-10-03. A screenshot filename on the page contains `2023-06-06`. That is not an article date. |
| [Version 11 Content Packaging Changes](https://foundryvtt.com/article/v11-leveldb-packs/) | NeDB `.db` files versus LevelDB directories; official unpack to JSON or YAML | Retrieved 2026-10-03. No last-updated field was found. |
| [Adventure Documents](https://foundryvtt.com/article/adventure/) | Adventure compendia and V14 quick start | The page says "Updated October 20, 2025 (Version 13.350)". Retrieved 2026-10-03. |

## Package types and layout

Version 14 allows three package types: `world`, `system`, and `module`.

User data is split into `Config/`, `Data/`, and `Logs/`. Under `Data/` the documented directories are `systems/`, `modules/`, and `worlds/`. Anything inside `Data/` can be served as a URL relative to that folder. The user-data article does not list the database filenames inside a world.

A module is a folder `Data/modules/<id>/` with `module.json` at its root. The manifest `id` must match the folder name. Foundry recommends `templates/`, `scripts/`, `styles/`, `packs/`, and `lang/`, and says any other layout is legal as long as `module.json` is present. `scripts` and `esmodules` are JavaScript that Foundry would load in a game session. This inventory records those paths and does not load them.

A system is `Data/systems/<id>/system.json`. The same article's example also shows `documentTypes`, `packs`, and script files. This spike does not implement a system adapter.

A world is a folder under `Data/worlds/` whose manifest is `world.json`. The Version 14 `WorldManifestData` interface requires `id`, `title`, `type: "world"`, `version`, `system`, `systemVersion`, and `coreVersion`. The game-worlds article says the data-path folder name cannot be changed after creation and the system cannot be changed after creation.

The module-development article's minimal example omits `"type": "module"`. The Version 14 `ModuleManifestData` interface requires `type: "module"`. The inventory trusts the manifest filename (`module.json`, `world.json`, or `system.json`) and warns if `type` disagrees.

## Compendium packs and on-disk formats

A pack declaration has a canonical `name`, a human `label`, a document `type`, and a relative `path`. `system` is optional in the type interface. The module article says that since Version 10, Actor, Item, and Adventure packs must set `system`. The inventory warns when those three types omit it.

Two storage formats are documented:

- Through Version 10, a pack was one NeDB file, usually `packs/<name>.db`: plain text, one JSON document per line.
- Since Version 11, a pack is a LevelDB directory. The manifest path drops the `.db` suffix (`packs/monsters` instead of `packs/monsters.db`). The directory contains binary files. Foundry migrates a leftover `.db` file into that directory on first load. The packaging guide still shows a `.db` path in its example and, later, tells V11+ authors to delete the database folder. Both statements are in the same guide.

The Version 11 article also says Foundry ships a command-line tool that unpacks LevelDB to JSON or YAML and packs it back. The [foundryvtt-cli](https://github.com/foundryvtt/foundryvtt-cli) README and `lib/package.mjs` were retrieved on 2026-10-03 (package version 0.0.6). The README describes `fvtt package unpack` and `fvtt package pack`. The pack source shows the classic-level options and the `!<collection>!<id>` keys quoted above. This inventory reads that LevelDB shape. It still does not load the YAML files the same tool can emit.

What the inventory reads:

- NeDB `.db` files as UTF-8 JSON lines.
- A `.json` pack file that is one object or an array of objects.
- A directory of `.json` files, one object or array per file.
- A LevelDB directory, using the key layout in [foundryvtt-cli 0.0.6 `lib/package.mjs`](https://github.com/foundryvtt/foundryvtt-cli/blob/main/lib/package.mjs), retrieved 2026-10-03. That file opens the directory with classic-level, `keyEncoding: "utf8"` and `valueEncoding: "json"`. Primary keys are `!<collection>!<id>`. Embedded documents are separate keys, `!<collection>.<field>!<parentId>.<embeddedId>`, and the parent value stores the ids. This inventory puts those objects back on the parent. A JSON object under any other text key is still inventoried, and the key is recorded as a diagnostic. Values are parsed with the JSON decoder only.

What it refuses to decode:

- `fixtures/leveldb-pointer`, which only looks like LevelDB (`CURRENT` plus a `.ldb` file that is not a database). Opening it fails. The bytes are not read as text and are not executed.
- `.yaml` / `.yml`. The Version 11 article says the official tool can emit YAML. This spike does not load YAML, because a YAML loader can be asked to construct objects.

Foundry's compendium UI can also import a JSON file into an unlocked pack ("Import Data" in the compendium article). That confirms JSON as an interchange Foundry itself accepts. It does not document the file's envelope beyond "a JSON file".

## Document types

### Primary documents (Version 14)

`ActiveEffect`, `Actor`, `Adventure`, `Cards`, `ChatMessage`, `Combat`, `FogExploration`, `Folder`, `Item`, `JournalEntry`, `Macro`, `Playlist`, `RollTable`, `Scene`, `Setting`, `User`.

Each primary type is described as having its own database table in the active world, except Adventure. The API overview says Adventures have no world collection and can only be stored in an Adventure compendium.

### World documents

The world list is the primary list without `ActiveEffect` and without `Adventure`.

### Compendium documents

`ActiveEffect`, `Actor`, `Adventure`, `Cards`, `Item`, `JournalEntry`, `Macro`, `Playlist`, `RollTable`, `Scene`.

The Compendium Packs article instead says that, aside from adventures, a pack holds one of: Actors, Items, Journal Entries, Macro Commands, Playlists, Rollable Tables, or Scenes. That user-facing list omits `Cards` and `ActiveEffect`, which the Version 14 constant includes. The constant is the newer, explicit list. The article is still published and was not updated in any date field this session could find. The inventory does not reject a pack whose type is only in one of the two lists; it records the declared type.

### Embedded documents

Version 14's embedded constant is:

`ActiveEffect`, `ActorDelta`, `AmbientLight`, `AmbientSound`, `Card`, `Combatant`, `CombatantGroup`, `Drawing`, `Item`, `JournalEntryCategory`, `JournalEntryPage`, `Note`, `PlaylistSound`, `Region`, `RegionBehavior`, `Level`, `TableResult`, `Tile`, `Token`, `Wall`.

The API overview table of contents retrieved the same day does not head a section for `Item` or `Level`, but the same overview says items can be embedded in actors, `actor.effects` is the documented ActiveEffect collection, and `SceneData.levels` is a collection of `LevelData`. The constant and `SceneData` are what this spike treats as authoritative.

`SceneData` names these embedded arrays: `drawings`, `lights`, `notes`, `regions`, `sounds`, `tiles`, `tokens`, `walls`, `levels`. `sounds` on a scene are ambient sounds. Playlist sounds are a different embedded type, `PlaylistSound`. The inventory counts a `sounds` array as `PlaylistSound` only when the parent pack type is `Playlist`. That parent-key choice for playlists was not re-fetched as a `PlaylistData` interface; scene `sounds` was. Playlist documents are otherwise retained whole because their schema is not pinned.

### Subtypes

The Version 14 documents page says these types can have package-defined subtypes: `ActiveEffect`, `Actor`, `Card`, `Cards`, `ChatMessage`, `Combat`, `Combatant`, `CombatantGroup`, `Item`, `JournalEntryPage`, `RegionBehavior`. A module-registered subtype id is prefixed with the module id.

The module-development article still says that, as of Version 11, only `Actor`, `Item`, `JournalEntryPage`, `Cards`, and `Card` can gain module subtypes. That is narrower than the Version 14 list. The inventory records `documentTypes` keys from the manifest and stores each document's `type` string as `subtype`. It does not interpret system or module data models.

### Adventure documents

An adventure is a compendium document that bundles other documents and keeps their ids and folder structure. The adventure article, updated 20 October 2025 with a Version 13.350 banner, names Actors, Items, Scenes, Roll Tables, Journal Entries, Cards, and Playlists. It does not name Macros in that sentence, even though Macro is a compendium type. The same page then describes Version 14 quick-start registration in `module.json`. The banner version and the V14 section were not reconciled on the page.

Media is not stored inside the adventure. The article says images, video, and audio stay as files in the module and the documents point at them.

This session did not retrieve an `AdventureData` field list. Nested adventure arrays are not expanded into separate inventory documents. On an unpinned document type the whole object is kept under `retained_fields`.

### Macros

`CONST.MACRO_TYPES` is `script` and `chat`. `MacroData.command` is "the string content of the macro command". `img` is a file path. Script macros are JavaScript. Chat macros are chat text. Both are data. The inventory copies `command` onto a behavior record with `executed: false` and `interpreted: false`. It does not parse the command for Foundry API calls. That parsing is a later milestone, and it is not required to refuse execution.

### Scenes, walls, and files

Version 14 `SceneData` holds `width`, `height`, `grid`, `environment`, `thumb`, and the embedded arrays above. `environment` is darkness and ambient light (`darknessLevel` from 0 to 1), not the map image. The background texture is `LevelData.background`. `thumb` is a thumbnail path.

A top-level `img` or `background` key is not in the Version 14 `SceneData` interface. If one appears, the inventory keeps it as an unmapped field and still picks up an asset reference when the key is `img`, `src`, `path`, `thumb`, or `video`. Asset discovery walks those keys anywhere except `command` and `script`, so a filename mentioned inside a macro is not treated as a resolved asset.

`WallData.c` is `[x0, y0, x1, y1]`. `door` is a number: `NONE` 0, `DOOR` 1, `SECRET` 2. `light`, `move`, `sight`, and `sound` are also numbers. This spike stores the raw `door` integers on the scene as `door_codes`. It does not turn them into barriers.

`JournalEntryPageData` has `type`, `text`, `image`, `video`, and optional `src`. Text that contains `<script`, `javascript:`, `onerror=`, or `onload=` produces a warning and is not rendered. The page object itself stays in the parent document when that parent type has no pinned field list.

## Export surfaces that matter here

Distribution of content is a module of compendium packs, or an adventure pack inside a module. The packaging guide says pre-packaged worlds are no longer the recommended way to ship adventures.

A world can still be backed up by copying or zipping the user-data folder. That zip is a package tree, not a new document type.

Folder export into a compendium can merge by name and can keep document ids. Individual drag-and-drop into a compendium does not keep ids. The compendium article also offers JSON import into an unlocked pack.

Version 14 quick start, from the adventure article, is a `quickstart` object on `module.json` that points at adventure uuids. The inventory retains that object as part of the manifest. It does not import an adventure.

## What this spike does not know

- A field-level schema for `Actor`, `Item`, `JournalEntry`, `Playlist`, `RollTable`, `Adventure`, `Token`, `AmbientLight`, or `Tile`. Those documents are retained whole, or, for scenes, only unmapped top-level keys are called out. Embedded counts use the `SceneData` array names plus `effects` (documented as `actor.effects`), `items` (items are documented as embeddable in actors; the key name is the usual one and was not re-read from an `ActorData` page), `pages`, `results`, `cards`, `combatants`, and `behaviors` on a `Region`.
- World database filenames. They are not in the user-data article. A Forge hosting staff reply on 7 September 2023 describes v11 worlds as LevelDB folders instead of `.db` files for actors ([World Size Check](https://forums.forge-vtt.com/t/world-size-check/12105?page=2)). This spike maps `data/actors` and `data/actors.db` from that description, and also maps the stems `items`, `scenes`, `journal`, `tables`, `playlists`, `macros`, `cards`, `folders`, `combats`, `messages`, `settings`, `users`, and `fog`. Those other stems are not each confirmed by an official filename table. An unrecognized `data/` entry is still read when it is text, with document type `Unknown`. A directory that actually opens as LevelDB is decoded with the same reader as a compendium pack.
- System-specific `system` payloads. They are retained and not interpreted. There is no dnd5e or pf2e adapter.
