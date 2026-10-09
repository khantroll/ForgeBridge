# Project Status

**Lifecycle:** UVTT DYNAMIC LIGHTING SLICE  
**Implementation started:** Inventory CLI, importable UVTT, loose scene assets, embedded Adventure scene discovery, ambient color, and deterministic AmbientLight range conversion  
**General converter started:** No

The zipped LevelDB scene is the previous state. This slice is the current state. One command writes scene `scene-vault` from `fixtures/synthetic-leveldb-scene.zip` as a UVTT file and copies that scene's PNG and WAV beside it. The unpacked LevelDB scene and the text scene `scene-crypt` still produce the same UVTT object. It is not a general Foundry-to-Arkenforge converter.

## What this slice does

`PYTHONPATH=src python3 -m forgebridge fixtures/synthetic-leveldb-scene.zip --uvtt-scene scene-vault --uvtt-out scene-vault.uvtt`

reads the LevelDB pack inside the zip, prints one JSON object with `uvtt` and `loss_report`, writes only the `uvtt` object to `--uvtt-out`, and writes `crypt.png` and `drip.wav` in the same directory. The UVTT file is the Arkenforge map import. The PNG and WAV are loose files from the import list in [docs/research/ARKENFORGE.md](docs/research/ARKENFORGE.md): JPG, PNG, WEBP, GIF, MP4, M4V, WEBM, MP3, OGG, and WAV. The envelope on stdout is the graded report and is not itself an import file.

Asset types that are not on that list are skipped and graded unsupported. Zip entries whose names leave the archive are not extracted and are not executed.

The current UVTT object follows the compatibility fixes below, based on the core fields on [Arkenforge's UVTT page](https://arkenforge.com/universal-vtt-files/), read 2026-10-03 (`dateModified` 2026-08-22). Notes are in [docs/compatibility/UVTT-SLICE.md](docs/compatibility/UVTT-SLICE.md).

These commands still write a UVTT file. They also write loose image and audio files for the scene they read:

`PYTHONPATH=src python3 -m forgebridge fixtures/synthetic-leveldb-scene --uvtt-scene scene-vault --uvtt-out scene-vault.uvtt`

`PYTHONPATH=src python3 -m forgebridge fixtures/synthetic-module --uvtt-scene scene-crypt --uvtt-out scene-crypt.uvtt`

No `.uvtt` file is stored as a hand-written artifact. Tests run the writer. LevelDB values and scripts are not executed.

## What the earlier work established

Public docs were re-read on 2026-10-03 and written up with citations:

- [docs/research/FOUNDRY.md](docs/research/FOUNDRY.md) — Version 14 document lists, package layout, and the LevelDB key layout used here.
- [docs/research/ARKENFORGE.md](docs/research/ARKENFORGE.md) — import extensions, UVTT fields, v0.5.0.0 / v0.5.1 UI features, and the automation surface that was not found.
- [docs/compatibility/INVENTORY-SPIKE.md](docs/compatibility/INVENTORY-SPIKE.md) — synthetic inventory results, including the LevelDB actor pack.
- [docs/compatibility/UVTT-SLICE.md](docs/compatibility/UVTT-SLICE.md) — the importable UVTT file, the four grades, the LevelDB scene, and the loose image and audio files.

The inventory IR is `schema/inventory-0.1.schema.json`. `fixtures/synthetic-leveldb` is still decoded into the inventory. `fixtures/leveldb-pointer` still fails closed. Unknown fields are retained. Imported JavaScript, macros, HTML, and YAML are not executed.

## Real Foundry Adventure scene support

A real Foundry v13 Adventure pack exposed a storage shape the synthetic scene pack did not cover: the pack can contain one top-level `Adventure` document whose `scenes` array contains the actual Scene documents.

The inventory now keeps the parent Adventure and also promotes each embedded Scene into the normal scene inventory. Promoted scenes retain their containing Adventure id/name/source index under `retained_fields._forgebridge_parent_adventure`. `--uvtt-scene SCENE_ID` uses that provenance to reopen the parent Adventure and select the embedded Scene, then sends it through the same Scene -> UVTT path as ordinary scene packs.

Foundry virtual asset paths of the form `modules/<this-package>/...`, `worlds/<this-package>/...`, or `systems/<this-package>/...` may resolve to the corresponding package-local path when the virtual package name matches the package directory. Traversal and symlink protections remain in force.

A synthetic regression covers a two-scene Adventure, parent preservation, scene discovery, provenance, scene selection, wall/light conversion, and package-local virtual background resolution.

## Dynamic lighting slice

The current branch translates the deterministic UVTT lighting subset:

- scene ambient hex color -> `environment.ambient_light` when the source stores a hex value directly;
- AmbientLight x/y -> UVTT position in squares;
- AmbientLight color -> UVTT color;
- outer Foundry dim/bright radius -> UVTT range in squares using `grid.distance`;
- separate Foundry bright/dim radii are explicitly graded approximate because UVTT has one range;
- negative Foundry radii (darkness/blackness sources) are reported unsupported and do not receive a fabricated positive range;
- Foundry animation, attenuation, coloration, contrast, luminosity, saturation, and numeric shadow controls remain in the loss report rather than being guessed into UVTT intensity/shadows.

Walls and portals remain the collision/line-of-sight geometry consumed by the target lighting engine.

## Real Arkenforge compatibility validation (2026-10-08)

The user-supplied native UVTT reference and Count's Manor import exposed wire-shape errors. The exporter now writes format 1.0, named point objects, absolute door bounds, top-level lights, native-compatible colors/defaults, and embedded compatible PNGs. Canvas origins derive from scene padding or stored dimensions and apply consistently to walls, doors, and lights. Source-specific constants are not used.

The working test confirmed image compatibility, geometry alignment, editable lights, dynamic illumination, and door switches. The entrance portal light-blocking test initially suggested a missing setting; the full source report later showed light=0 and sight=0 on both tested entrance segments, making their transparency intentional. Per-portal manual warnings now distinguish those settings from opaque doors. The fresh-export manual test confirmed light movement. Defaults for light intensity/shadows are explicitly approximate.

The full selected scene is now saved in a `.forgebridge.json` companion and included in stdout, preserving skipped lights, restriction settings, and unknown data for future correlation. UVTT does not define the destination's capabilities. The supplied native package demonstrated notes, audio, ambience, and map metadata beyond this interchange subset.

The full Count's Manor source report confirms padding 0.25 and valid positions/ranges for all 16 skipped lights, whose tint is null. Unset tint now exports as neutral white with an approximation warning, bringing this scene to 24 lights. Next: verify the expanded real import, test an opaque source door rather than a transparent entrance segment, and compare native map fields for independent blocking/toggle semantics and light positioning. Do not claim those unresolved parts are automatic or verified.


## Journal correlation milestone (2026-10-08)

Two real scene imports now pass alignment, lighting, and door checks: Manor first floor and Count's Crypt. Fireplace light trapping is corrected by omitting explicit light=0/sight=0 non-door barriers; manual warnings identify remaining mixed blocking modes. The user confirms illumination follows the moved light source. Ungrouping remains a manual import step.

Exports now include full linked JournalEntry data under `scene_notes` in the preservation companion and a readable `.notes.txt` GM reference. Map notes resolve within their selected parent Adventure first, then standalone packs, with exact page matching and explicit missing/ambiguous statuses. Duplicate Adventure variants are not mixed. Full source HTML is inert JSON; readable text excludes active HTML. Native `.rwnote` writing is not implemented. Existing native references establish that notes exist, but not a validated writer schema. Next: verify the real Crypt's 19 note links using a fresh companion export, then investigate native note representation and actor/token correlation.


## Linked dependency milestone (2026-10-08)

The real Crypt note export now verifies all 19 exact journal/page matches, no read errors, and complete retention of its 21-page journal. The dependency resolver follows recognized journal/page and roll-table UUID links recursively while preserving original references and full objects. Exact compendium namespaces, relative-page links, source scope, cycle detection, explicit failure statuses, and traversal bounds prevent silent guesses. The readable GM reference includes linked rules and table outcomes; no native destination objects or dice execution are introduced. All 11 relative links in the uploaded Crypt journal resolve. Next: run a new export against the original package to verify external rules pages and tables, then investigate native note representation.

### Native note research — 2026-10-08

Added a bounded inert MS-NRBF inspector (`src/forgebridge/nrbf.py`). Parsed all 30 native files in the user-supplied Town package and correlated its seven note marker targets with note metadata/content. See `docs/research/NATIVE-NOTES.md` for observed classes and the controlled sample needed next. The supplied token notes contain no prose/link/table fields. Native writing remains unimplemented; current UVTT output is unchanged. Verified the fresh Crypt companions: 19 placed notes and all 29 discovered dependency links resolved, two complete roll tables, no errors/truncation.

### Native note writer smoke test — 2026-10-08

The user supplied native test notes with bidirectional links and a rollable-table field, then an archive with their map markers in an autosave. Added an experimental generator (`python -m forgebridge.native --out NEW.zip`) for two synthetic linked notes and one three-result table. The fixed schema contains observed type/member metadata only, without private sample text or account names. Generated text, link targets, ranges, inherited fields, ZIP paths, and no-overwrite behavior are tested. It is separate from the existing Foundry exporter. No successful native Toolkit import is claimed; that manual test is next. The previously requested sample is now available; no further sample is required for this first note/table import experiment.

## Native note import verified; companion conversion (2026-10-09)

The user confirmed synthetic text, A/B links after correcting the installation path, and the three-outcome table. A failed startup log showed denied writes to ArkenforgeData temporary/hotkey files and Toolkit logging under Program Files; this log does not prove generated-note corruption. Source conversion is now available separately with `forgebridge.native --companion SOURCE.forgebridge.json --out NEW.zip`. It emits indexes, journal page notes, strictly supported rollable tables, exact native links, conversion/loss and placement reports, installation instructions and the unchanged source companion. Retained pages outside the initial traversal are resolved only against retained scoped documents. Unknown links/media/formatting/permissions are not silently reconstructed. The actual Crypt output requires a new manual import test; automatic map placement and native visibility remain unverified.

Validation: 89 local tests pass. The private Crypt package has 84 notes (76 pages, seven document notes and a scene index), both Despair/Nightmare tables, 54 converted UUID occurrences and one missing-document reference retained literally. All 168 native files reparse, all native targets exist, all 19 source placements map to native note metadata, ZIP CRC checks pass and the packaged source companion is unchanged. These checks do not replace Toolkit testing of the real source-content import.
