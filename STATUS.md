# Project Status

**Lifecycle:** CALIBRATED SCENE PROFILES
**Implementation started:** Inventory CLI, importable UVTT, loose scene assets, embedded Adventure scene discovery, ambient color, and deterministic AmbientLight range conversion  
**General converter:** Bounded scene/content/token slices implemented; complete actor and behavior conversion pending.

Portable capture milestone (2026-10-18): `forgebridge.native_capture` captures
dependency-closed native ZIPs with original member bytes and a provenance manifest.
Pinned profiles can be copied with all inputs and rebased for relocation; reusable
control exports remain separate from scene geometry and calibration. Saved-asset
reads require a closed-Toolkit snapshot; no capture installs or edits campaigns.
See [portable capture](docs/NATIVE-CAPTURE.md) and
[execution evidence](validation/2026-10-18/PORTABLE-CAPTURE.md).
Pending Crypt actual-player visibility, profile player restart and bounded fog
do not block development. Next independent task: investigate intermittent read-only LevelDB snapshots
with retained diagnostics and controlled fixtures, then extend native-reference audits.

Independent reader hardening (2026-10-24): in-memory LevelDB snapshots now reject
Windows separators, drive-qualified names, alternate data streams and NUL names
before writing. A cross-platform regression checks rejected entries cannot write
outside the snapshot and that accepted CURRENT bytes remain unchanged. No retry,
conversion-semantic or runtime-validation change. See
[reader evidence](validation/2026-10-24-READER-HARDENING.md).
Latest full suite: **150 run, 146 passed, four Windows symlink skips**, 31.173s.

Dependency isolation hardening (2026-10-24): capture and production assembly now
share portable native-path checks. Case aliases and ZIP symlinks fail; dependency
merges validate every entry before mutation. Exact identical dependencies still
deduplicate. Final package audits reject ambiguous paths even without tokens.
Latest full suite: **156 run, 152 passed, four Windows symlink skips**, 37.037s.
See [dependency evidence](validation/2026-10-24-DEPENDENCIES.md).

Historical CPU-contention investigation (2026-10-18; superseded by October 19 recovery below): desktop testing now runs separately
from tests/builds/PDF/compression/dependency scans. New read-only sampler and
[desktop runbook](docs/DESKTOP-VALIDATION.md) record process CPU and distinct helper/
capture outcomes. Baseline Toolkit70.8–76.5% of two-thread capacity; recovery
Toolkit72.3–75.8%, browsers4.1–7.6%, measured helper0%, no named compute workers.
One helper setup/enumeration attempt timed out at30s; no screenshot/input followed.
Native30-FPS cap and720p/15-FPS stream controls remain uninspected/unapplied because
native control is unavailable. The in-app player tab is confirmed stopped.
No after-reduction result or causal claim; prior97% load and current failures at
lower load suggest contention alone may not explain the helper failure. Desktop
checks remain pending; independent tooling work continued without another human
recovery request. No process priorities, power/security or original content changed.

Latest milestone (2026-10-17): version 1 scene profiles bind the original package,
exact Adventure/scene identity, companion, calibrated primary geometry and reusable
native controls. Relative paths resolve against the profile. Read-only preflight
checks identity, hashes, dependencies and token support; explicit CLI builds remain
available. Calibration cannot silently follow another scene or changed input.

Synthetic isolation tests cover repeated token identities/textures, different grids,
padding/calibration, rejected and zero tokens, dependency closure, deterministic
rebuilds and preservation of another scene/user edits. Two real profiles build Manor
and Crypt packages; file audit passes with 529 closed metadata references, isolated
token/note/media scopes and no installation conflicts. Separate reviewed installation
added 438 absent files without overwrites. October 18 runtime samples now PASS:
both real profile maps load/save/switch/reopen through Toolkit0.5.1.18 restart;
Manor Stoker/Upper Hall and Crypt Swarm/Wight/Storage Area retain their positions
and correct note targets. Saved-file audit confirms all token positions/hidden
flags and room targets match generated baselines. Input control recovered after
normal non-elevated relaunch; prior Toolkit/launcher elevation blocked the standard
helper. October 18 controlled player comparison displays a new native control,
Multi Scene and Manor through the same browser output. Crypt remains black after
fog-off and camera-follow comparisons; cause remains unconfirmed. New profile
generated-token player visibility/restart checks remain BLOCKED. The Manor token
visibility experiment selected the preserved manual Stoker, so it is excluded
from generated-token validation. Its original visibility was restored and saved.
Prior accepted player evidence remains separate. No converter change was made.
Latest suite: 144 run, 140 passed, four Windows symlink tests skipped (not safety PASS).

Resume verification (2026-10-18, after 982f23d): full suite rerun passes in66.104s
(144 run/140 passed/four symlink skips). Both real profile read-only preflights pass.
Toolkit0.5.1.18 capture/input work; explicitly selected generated Manor Stoker
inside the map, distinct from outside manual Stoker_token_1. UI Size1,
X12.500/Y-18.500, rotation0 and scales.512/.512 agree with the generated baseline.
No fields changed. Saved-map audit still matches all ten generated token states
and24 room targets, with unchanged saved-map hashes. New evidence does not pass
player visibility. The prior bounded diagnostic/human handoff remains pending;
no repeat of Crypt/fog gestures, rebuild, install or production change justified.

Manual steps remain native UVTT import/export/calibration, reviewed installation,
GIF setup and the documented bounded fog gesture. Labels off; Foundry fog/vision,
procedural light animation and actor/stat behavior stay explicit gaps. See
[scene profiles](docs/SCENE-PROFILES.md) and the validation log. Next validation step:
establish a visible actual player viewport for representative visible/hidden tokens
on both profile maps, then verify after restart. These pending runtime checks do
not block independent portable capture/export development. Exact diagnostic and
runtime scopes are recorded in the validation log.

Player follow-up after human setup (2026-10-18): working Waterfox player stream
shows Profile Manor. The correctly selected generated Stoker inside the room is
visible, then disappears after explicit Toggle hidden; the outside manual control
stays visible. This passes only the initial visible→hidden observation. Toolkit
capture then times out twice, including one fresh-enumeration recovery. Input
stopped. Generated Stoker remains temporarily hidden in memory, **unsaved**, with
human restoration requested. Saved-map audit still matches both original generated
baselines. Visible restoration, Crypt and restart checks remain BLOCKED. Do not
assume live state was restored from the unchanged saved-file hash.

Subsequent recovery supersedes that temporary-state warning: actual Waterfox
output now shows generated inside-Manor Stoker restored visible, distinct from
outside manual control. Saved Manor normally. Crypt opened without rebuilding;
no Crypt token edits/save. Capture timeouts recur during projection framing, so
Crypt player and both-profile restart remain BLOCKED. See appended restoration
evidence; Stoker is no longer left hidden.

The sections below retain earlier milestone history.

### One scene package with generated tokens — 2026-10-16

The production package builder accepts calibrated token and optional separate
marker controls, composes them into the geometry map, closes native metadata
dependencies and rejects conflicts. Existing map objects and original map/metadata
backlinks are preserved. Generated token notes are isolated by output map name and
source identity. Missing textures are explicit per-token rejections while other
supported tokens migrate. Standalone token ZIPs use the same scene compiler.

The fresh manor test package contains Stoker and four asymmetric arrows sharing
one texture, Sizes .5/1/2, rotations 0/90/180/270 and mixed hidden states. Three
invalid entries are reported without duplicate output. Actual player rotation and
visibility pass through restart. Targeted wall/door blocking passes with one
temporarily white light; movement follows isolated numeric edits. Lighting
experiments were discarded. Package SHA256:
`9c9cc84a5a514065e8321a0dcc406dd5aa1fe8281c7abaa9f4ace0253ca5d5f8`.

Manual work remains: native import/export/calibration, conflict-aware installation,
ungrouping individual geometry objects, GIF import/FPS and bounded fog reveal/hide.
Foundry fog/vision, actor/stat blocks, combat behavior and procedural light
animations are retained but unmapped. Labels off; two missing source tables and
seven media gaps remain explicit. Next implementation: a reusable calibrated
scene profile/control dependency workflow with multi-scene token isolation tests.

The earlier UVTT milestone below remains supported. Native map/content packages
and the bounded token writer are later milestones, described at the end of this
file. Complete actor/stat/behavior conversion remains pending.

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

### Native image lookup failed; diagnostic v2

The user opened the generated note but Toolkit reported its `.rwfile` missing. The next screenshots confirm both `Image-Test.rwfile` and `Image-Test.rwmeta` exist under the installed Media test folder. Presence does not establish successful resolution. v1 renamed internal asset name/creator independently of its filename and moved it out of the source media-category hierarchy; neither change was runtime-validated.

The revised test preserves the complete exported asset pair byte-for-byte, including original filename, names, creator and presets. It retains the media-category parent layout and changes only the containing test folder. The freshly generated note and folder have distinct v2 names. Tests now assert whole-file equality as well as embedded image preservation. The lookup cause is unproven; actual v2 display/save/reopen testing is required before source media integration.

## Native reused-image test passed; source image attachments (2026-10-09)

The user confirmed v2 displays correctly and survives closing/reopening the note and restarting Arkenforge. This verifies generated Media fields and relocation with the original asset pair intact; it does not isolate which v1 change caused the failure.

Added an experimental source-image mode to `forgebridge.native_media` using `--companion` and `--media-bundle`. It validates collection scene/origins/hashes, normalizes static PNG/JPEG/WebP/GIF to RGBA PNG, derives aspect-preserving thumbnails and replaces encoded image arrays within the supplied native template. Original native asset filename/name/provenance and preset defaults remain intact; separate content-derived folders prevent collisions. Native image fields attach to their corresponding retained journal pages, journal images and table-reference notes. Repeated sources share assets and identical occurrences within a note share a field. Existing converted note paths and room-marker targets stay unchanged. No map/labels are emitted. PDFs/animations/gaps remain explicit references. Regenerated note files replace prior generated notes; user edits require retaining a backup.

Validation: 119 tests pass, adding page scoping, attachment closure, stable note/marker targets, retained source equality, WebP transparency, portrait/landscape sizes, deduplication, PDF/animation fallback, tampered hashes, mismatched origins, no overwrite and thumbnail sizing. Source asset construction/thumbnail scaling still need Toolkit testing; the original native-image test does not verify arbitrary source image conversion. The real collected asset bundle remains on the user's computer, so next run the new command there and verify real handouts plus reopening/restart. Labels remain off and player visibility remains unverified.

## Source image runtime test passed; attachment names/order (2026-10-09)

The user supplied a conversion report with 48 native image assets and 55 attachments across 84 notes, no source read errors, 10 PDF references and seven expected collection gaps (six other-pack images and one SVG). The user confirmed source image display/proportions, note reopening and Toolkit restart all pass. This verifies the tested Count's Crypt package; other packages and native map asset placement remain unverified.

Attachments now follow occurrence order within each individual note, including reused images appearing in different orders across pages. Readable filename-based Media field titles replace global attachment numbers. Deduplication, existing note paths and marker targets are retained. Attachments remain below the text; the library panel's generated document order is unchanged. Validation: 120 tests pass, including opposite image order across pages and decoded native field titles. Labels remain off; PDF support and player visibility are pending.

## Optional PDF page handouts (2026-10-09)

User confirmed attachment ordering passes in Toolkit. The uploaded collected
handout bundle contains ten PDFs, seventeen total pages. Added opt-in
`--pdf-pages` and optional pinned PDFium renderer dependency. PDF page images
use the verified native image encoding and category layout, attach to existing
notes in numbered page order, and preserve original PDFs outside MyAssets.
Existing note paths/marker targets remain stable; no labels/map are emitted.
PDF interactivity/searchable text is not reproduced. Invalid/encrypted PDFs
remain references. Bounds: 32 pages/document, 128 package pages, at most 2400
pixels per side, 64 MiB rendered PNGs per document and existing package limits.

Validation: 123 tests pass with the optional renderer installed, including
coloured page order, portrait/landscape dimensions, decoded native payloads,
original PDF bytes, default-off behavior, malformed PDF fallback and page/byte
limits. Actual PDF page display/readability/persistence requires the user's
Toolkit test. Labels remain off; player visibility remains deferred.

## Second-floor tests and readable naming (2026-10-14)

The user confirmed manual map opening, all five second-floor marker links and
marker persistence. Toolkit logs show automatic UVTT opening looks for map
metadata under Media/Cartographer/MapImport while the importer actually saves
it under Maps/MapImport; opening from the map browser worked. The exported
background image had a magenta light enabled, and all seven door barriers had
light-blocking flags set. Isolated door runtime behavior remains unconfirmed.
The user confirmed linked documents are present in the correct order and the
Upper Hall marker is present; second-floor handout image/PDF display and restart
persistence were not explicitly confirmed by that response.

Added optional readable `--note-folder` to native map and handout commands,
with portable-name validation. Internal note links and map marker paths derive
from the selected folder; default hashed paths are preserved for compatibility.
Navigation notes now read `<scene name> — Start Here`. Separate migration test
copies avoid overwriting tested maps. 125 tests pass, including renamed-folder
link closure, rewritten marker targets and unsafe/reserved filename rejection.
Labels remain off and native marker icons are retained at the user's request.

## Second-floor regression complete; combined package command (2026-10-14)

The user confirmed the second-floor handouts persist and door blocking works.
Five marker links and map/marker persistence previously passed. Readable names
are accepted. This completes the requested second-floor regression; player
visibility remains deferred and labels remain off. No claim is made that every
individual source asset or additional scene was exhaustively tested.

Added `python -m forgebridge.package` to collect source media (or use a matching
bundle), compile map markers and enriched native notes, and emit one combined
ZIP/report/INSTALL. It uses a calibrated native map export and the observed
native media template. Marker and attachment targets are checked before output;
media conflicts, mismatched bundles, unsafe folders and overwrite attempts fail.
Existing exported generated notes require explicit `--regenerate-notes`, retaining
backup guidance for manual edits. Native marker icons remain unchanged.

Validation: 129 tests pass. New integration tests cover collected media, map and
note target closure, background preservation, source equality, default labels-off,
no overwrite, wrong-scene failure without partial output, explicit regeneration
and conflicting asset rejection. Native export/Toolkit import and calibration
remain required; the command does not automate the licensed application.


## Native token semantics and bounded writer (2026-10-16)

Resumed `cursor/dynamic-lighting-c6b0` / PR #8 from 90b721b, preserving existing
source assets, campaigns and unrelated local files. Toolkit v0.5.1.18 desktop
control works. On the isolated fresh manor, Stoker's native Size 1→2 doubles its
sprite bounds around a fixed center. Numeric movement saves and persists after a
blank-map switch/reopen. A separate horizontal transform 1.024→1.5 saves but resets
to 1.024 on reopening with Size still 2. This confirms Size normalization for this
control; the earlier transform-only result was not evidence of a converter bug.
Restart persistence of these latest edits is still pending.

Added Foundry token adapter → immutable Token IR → experimental native target
writer. The bounded slice preserves qualified source identity, texture reference,
name, calibrated center, square footprint, texture scale (baked centered RGBA
canvas), rotation and hidden serialization. Padding/grid and native origin/scale
are explicit; no universal 2.56 assumption. Native Size is converted separately
when source/native grid calibration differs. Both inherited transform copies are
updated. Original control maps/notes are preserved, including map backlinks;
output overwrite and native map-name collisions are refused. Non-square or
animated textures, rectangular footprints, mirrored/oversize textures and custom
anchors/transforms remain unsupported with reasons. Actors/stat blocks, scripts,
vision, light behavior and other fields stay retained-only and are reported. No
Foundry scripts execute. Rotation orientation and actual player hidden behavior
remain unverified.

The generated Stoker candidate has source center (12.5,18.5), native (32,-47.36),
Size 1 and .8 texture scale. File-level checks pass: deterministic archive bytes,
native reparsing, metadata closure, source preservation and calibration tests.
Generated-token import, comparison with the manual control and restart remain
DEFERRED, so this is not a completed automatic-token runtime milestone.

Prepared a combined candidate from the newly UVTT-imported saved map, retaining
fresh geometry. Its calibration is still a file-derived candidate requiring UI
cross-check; cloning only FB Cal A from the old template does not validate fresh
geometry behavior. All 176 native files parse and 161 metadata reference
occurrences close. Created an original synthetic red/blue/green animation fixture;
playback/position/persistence have not been observed.

Activating Toolkit's local player stream opened a Windows Firewall modal for its
Node.js server. The tool sees that modal over Toolkit but exposes no selectable
PickerHost window; dismissal through Toolkit did not work. No firewall access was
granted. User cancellation is needed to restore interaction; this blocks the
remaining runtime work, not file generation. Actual player output is DEFERRED.
All-five-marker navigation, representative rolls, every PDF page, wall/door
blocking, fireplace/moved-light checks, bounded local fog and animation remain
unfinished on the current packages. Earlier user-confirmed passes are kept
separate. Labels remain off. Two unresolved table UUIDs and seven media gaps are
unchanged.

Validation: 136 tests run, 132 pass, four WinError 1314 symlink tests skipped;
skips are not passed safety checks. See the updated summary and controlled-change
evidence in `validation/2026-10-15/VALIDATION.md`, plus the compact Oct 16 file
audit. Next milestone: dismiss the modal, import the generated token candidate
without conflicts, compare Size/texture/placement with the control, then
save/switch/reopen/restart; complete fresh combined-map and independent fog/media
runtime checks before extending token conversion.

## Runtime follow-up after firewall approval (2026-10-16)

The firewall modal is resolved by the user's approval. Actual browser player
streaming works: covered output is black with native fog text, and Clear all fog
reveals the projected map/grid. Bounded local reveal/hide remains inconclusive;
this is not automatic Foundry fog or vision conversion.

Installed only absent files from conflict-checked native test ZIPs (100 files;
existing identical dependencies skipped). Generated Stoker now passes native
import, calibrated center, Size1/.512 transform, .8 raster texture scaling,
one-square movement and save/switch/reopen/Toolkit restart. Control Size2/X22
also persists. Rotation orientation and actual player hidden state are unverified.

Fresh combined package loads and saves/reopens, its half-grid calibration agrees
with the UI, and all five room markers open correct native notes. Journal order
and all 17 PDF page images/order pass, plus representative Despair rolls (1 and 3).
Ismark opens in a readable enlarged preview. Older combined-map full regression
remains unfinished. Library fireplace on/off
visibly changes local illumination at night; opaque door/wall isolation and
moved-light alignment are still incomplete. An inconclusive selection-wide edit
was discarded; saved baseline hash remains unchanged.

Synthetic GIF import, red/blue/green playback, numeric movement and map reopen
work natively, including GIF playback/position/FPS after Toolkit restart. Two PNG-sequence attempts created only
one-frame objects and remain failed attempts with unresolved cause. Neither
workflow implements automatic animated-media conversion. Labels stay off; source
table/media gaps are unchanged. See the appended validation results and compact
runtime file audit for hashes and precise scopes. Next: finish
bounded fog/geometry/content regression before broadening the token writer.

Resume checkpoint: the combined Start Here note incorrectly claimed markers were
not automatic because the media-note stage dropped its map context. Fixed that
context propagation and checked the serialized text in a package regression.
Four package and six native-image tests pass. A separate fresh wording-check
build parses all 176 native files and closes 161 metadata references; it was not
installed. The runtime-tested package hashes remain unchanged.

The local fog polygon retry was also inconclusive; it was discarded by switching
to Blank without saving the fresh combined map. No native fog defect established.
Next implementation milestone: validate rotated and hidden generated tokens
against actual player output, then extend the bounded writer to a per-scene token
set. Keep actor/stat-block conversion separate and retain unsupported behavior.


## Portable capture execution results (2026-10-18)

PASS (file-level): Manor/Crypt native bundles and relocated profiles, with original
bytes, source identity, hashes, calibration and namespaces retained. Controls stay
separate from geometry. Native bundles contain 8/12 files. Final targeted run: 6
passed. Initial full run: 148 total, 142 passed, 4 skipped,1 corrected safety failure
and1 inventory error subsequently passed. No clean full rerun claimed.
An initial Crypt source-reader failure passed controlled comparisons/retry;
cause unconfirmed. No conversion math changed.
See [execution details](validation/2026-10-18/PORTABLE-CAPTURE.md) and
[hashes](validation/2026-10-18/portable-capture-results.json).

BLOCKED/PENDING: desktop helper setup/enumeration after bounded recovery.
Full support diagnostic stays local; no new activation/capture/input/runtime pass.
Crypt actual-player visibility, profile player restart and bounded fog remain
pending independently of development. Accepted GM/earlier player evidence remains
accepted. Labels off. Manual import/export/calibration, reviewed installation,
GIF setup and conversion gaps remain explicit. No original assets, campaigns,
manually edited notes or installation changed.


## CPU recovery and clean regression run (2026-10-19)

PASS: desktop enumeration/capture/input recovered; Toolkit maximum FPS changed
from 60 to 30 through supported UI. Active stream verified at 1280x720 / 15 FPS,
then stopped before compute. Crypt loaded; Toolkit CPU 15.21-17.22% with stream.
The final bounded capture sequence completed 5/5 with no timeouts. Historical
contention is correlated; the cap's isolated causal effect is not established.
PASS: clean full suite 148 run, 144 passed, four Windows symlink skips, 48.387s.
Crypt player visibility / both profile player restart checks remain PENDING;
bounded fog DEFERRED. No package/content edits or installations in this pass.
See [measured recovery](validation/2026-10-19-CPU-RECOVERY.md) for precise scope.
## Profile player follow-up and reference audit (2026-10-19)

BLOCKED: browser connection caused native Toolkit Unity WebRTC empty ICE-candidate
ArgumentException; lit Crypt room was not established. No token source states or
saved profiles changed. Toolkit closed/restarted normally; active-window captures
worked. 30-FPS application setting retained; stream explicitly configured 720p/15
before activation, then stopped by shutdown before compute. Accepted Manor initial
player visibility and profile GM persistence stand; profile player restart and Crypt
visibility remain pending. Bounded fog deferred. No rebuild/reinstall.

PASS: portable capture now rejects unfamiliar native dependency paths with exact
origin/reference rather than silently omitting them. Five capture tests pass;
Manor/Crypt file recaptures retain original hashes. Latest full/diagnostic runs each
149 run, 143 passed, four skipped, two LevelDB errors. Retained diagnostics show
Windows .dbtmp replacement failures during both new test-DB creation and copied
snapshot opening; root cause unresolved. No retries or LevelDB logic changed.
Next independent task: controlled Windows LevelDB temporary-file replacement
reproduction and diagnosis; native reference schema coverage can proceed separately.
See [follow-up evidence](validation/2026-10-19-PROFILE-PLAYER.md).
## Resume checkpoint (2026-10-24)

PASS: full diagnostic regression 149 run, 145 passed, four Windows symlink skips,
41.137s. New bounded LevelDB diagnostic: 10 create, 10 copied-open, 10 ordinary
replace controls pass, fixture unchanged. Earlier .dbtmp failures remain unresolved;
no retry/suppression or reader change. See scripts/diagnose_leveldb.py.

BLOCKED: existing Toolkit activation timed out at low measured CPU; fresh target
capture showed foreground Resolve/terminal while metadata claimed Toolkit. Ordinary
Explorer capture also showed the wrong foreground surface. No input on unreliable
views, no unrelated windows minimized/closed, no settings/content/save/install edits.
Crypt player and profile player restart stay pending; accepted results stand; fog
separately deferred. Next independent work: controlled LevelDB failure attribution
and observed native-reference schemas. See validation/2026-10-24-RESUME.md.
