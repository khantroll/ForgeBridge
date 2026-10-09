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

## Crypt native notes verified; calibrated map markers (2026-10-09)

The user opened a real Crypt room, followed room/note and rules links, and rolled the tables successfully. Handout links have no files to open; media packaging remains a gap. A manually saved native export contains the image and three calibration markers. Its background is 4000×4200 pixels (40×42 source grid squares), centred at native (51.2, -53.76), with scale 2.56. The three approximate hand placements confirm right-positive/up-positive axes and image origin (0, 0); hand-placement jitter is not used to skew the transform.

Added a separate native-map experiment that appends marker graphs cloned from the supplied native template and patches only name, tile list and UID counter. Existing source objects outside those three records are compared unchanged after reparsing. The new private map has 19 matched room markers, excludes the three calibration markers from the active tile list, and retains the image, barriers, doors, lights and media. The source export is untouched. This is not native-map construction from Foundry or general coordinate inference.

Validation: 97 local tests pass, including marker identities/UIDs, a full-array expansion, preservation of existing wall data, shared-name metadata, invalid transforms/targets, ZIP paths, package target closure and no overwrite. The user subsequently verified marker click-through and persistence after saving, switching to a blank map and reopening the saved copy. All 19 coordinates retain the source placement; the screenshots confirm working room targets. Native player visibility remains unverified.

## Marker label research (2026-10-09)

Foundry core shows Text Labels on hover; permanent labels are an optional enhancement (for example Pin Cushion), not its default. Arkenforge uses native content-link icons, with overlay visibility/size settings; its v0.5 release removed Hover Text and Alias note fields and added native map text. Older hover-field release notes do not establish current behavior. The user reports no room-name tooltip when hovering the converted marker. Exported marker names and note/metadata names are already populated correctly; a conversion defect has not been proven.

Decision: persistent room labels should be optional and off by default. Preserve source positions and room names. Native text serialization is not present in the supplied samples, so implementing editable native labels requires one current native text object exported with its map. Compare a newly placed native note marker against the imported one before claiming a hover fix. No label switch or hover fix is implemented yet.

Sources: https://foundryvtt.com/article/map-notes/ ; https://foundryvtt.com/packages/pin-cushion ; https://arkenforge.com/v0-5release/ ; Arkenforge maintainer explanation at https://www.reddit.com/r/Arkenforge/comments/1g8ezwa/can_i_make_an_overworld_style_map_with_pins/ .

## Optional native room labels implemented (2026-10-09)

The new private saved-map export supplies one `ArkenTilePresetText` object. Text is a string; its font is null (native default), font size 10, white tint, scale 1, and Hidden from players is enabled. Implemented `--marker-labels off|on`, default off, using a cloned native text template. Labels are separate editable text objects with unique UIDs; they inherit the native style, use a configurable grid offset, enable the hidden flag, ignore time-of-day tinting and neither illuminate nor block the map. Toolkit display controls are not modified.

Existing exact-target room markers now retain their native positions, UIDs and objects instead of being duplicated. Re-exporting replaces/removes only generated labels, preserving unrelated manual text. Exported note files are preserved, including edits, while missing companion notes are supplied. A separately named private Crypt map contains 19 original room markers and 19 generated labels. All original source objects outside map name, tile list and UID counter compare unchanged; original notes/media are byte-identical and target closure/ZIP CRC/native reparsing checks pass.

Validation: 102 local tests pass, including default-off behavior, native-template requirement, label hidden/nonblocking settings, inherited shared positions, existing marker preservation, label on/off re-export and edited-note preservation. Generated label appearance, editing/save/reload and Player View still need Toolkit testing. The previously tested unlabelled map remains untouched.

## Labels deferred; journal media collection (2026-10-09)

The label map loads and displays its native text. The user finds its appearance unsuitable and asks to leave labels off for all further testing. Simulate player view left labels visible even after deselection, while the map image disappeared. Actual player output is unavailable at present; hidden flags alone are not proof of player visibility. Label editing/save/reload is not verified. Return to the tested unlabelled map; the default remains off.

The next gap is missing handout media. Added `forgebridge.handouts`, which reads the existing retained journal/table graph and collects local image/PDF/audio/video files from the original Foundry ZIP or directory into a separate inspection bundle. Source bytes are unchanged, paths are mapped with origins/hashes, repeated references share files, and matching basenames do not collide. Missing, external, foreign-package, unsafe, oversized and unsupported references are explicit. No remote fetching, native media writing or note-link rewriting is claimed.

Validation: 109 local tests pass, covering nested ZIP package roots, namespace matching, encoded local paths, collisions, HTML media discovery, suppression of active markup, traversal/symlink rejection, bounds, duplicates, no overwrite and CLI outcomes. The private Crypt companion has 65 unique media references across 91 occurrences (49 WebP, five PNG, ten PDF and one unsupported SVG). These are reference counts, not verified source files. The original package remains on the user's machine; next run the collection there, inspect a handout, then supply one controlled native note/media export to establish actual handout serialization.

## Media collection verified; native image-field test (2026-10-09)

The user's collection report confirms 58 copied files: five PNG, 43 WebP and ten PDF, totalling 5,496,278 bytes. Six references point to other modules and one SVG is unsupported; there are no `missing` entries. Images opened successfully; PDF opening has not been confirmed. No native media links were rewritten by collection.

The supplied small native image-note export contains a Media field targeting its accompanying media metadata, plus an embedded 500×500 RGBA PNG and 128×128 PNG thumbnail. Added the observed field schema without private text or user identity. `forgebridge.native_media` generates a fresh note with that field, a separately named/relocated native asset pair and installation/test instructions. It preserves image/thumbnail byte arrays and uses bounded inert parsing. This deliberately tests generated attachment linkage before arbitrary source-image construction or PDF conversion.

Validation: 114 tests pass. New cases verify target closure, inherited field identities, byte preservation, asset names/provenance, ZIP integrity, no overwrite, mismatched targets, multiple fields, rejected paths and invalid images. The private generated four-native-file package reparses, has no reference to the original image metadata path, and preserves both supplied image arrays. Toolkit display and note/restart persistence are the next gate. Labels remain off; actual player visibility remains unverified.
