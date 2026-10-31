# ForgeBridge

Portable native dependency capture and relocatable pinned profiles are available
through `python -m forgebridge.native_capture`; see [the capture workflow](docs/NATIVE-CAPTURE.md).
Profile generated-token player visibility/restart checks passed on October 31;
bounded fog remains separately deferred. See the [roadmap](docs/ROADMAP.md) and
[scene-import operator/release checklist](docs/SCENE-IMPORT-RELEASE.md).

Latest local Windows validation (October 31, Python 3.14.2): **167 run, 163 passed,
four symlink skips**. Shared capture/package checks reject case aliases and merge
conflicts before mutation. The CI diagnostic gate now propagates failed phases
after retaining evidence; its updated GitHub run must be checked separately.

> **Status: CALIBRATED SCENE PROFILES**
>
> ForgeBridge builds calibrated native scene packages with geometry, room markers, linked notes, attachments and supported tokens. Version 1 profiles pin source identity, hashes and scene-specific calibration. Portable capture includes a read-only audit. Manor/Crypt GM persistence and October 31 player visibility/restart observations pass. Bounded fog is deferred; Foundry fog/vision is reported as manual, not converted. Historical Windows LevelDB replacement failures remain unrooted despite later clean runs. Native calibration, reviewed installation and GIF setup remain manual; actor/stat/behavior and procedural animation gaps stay explicit. Labels off.

```powershell
py -m forgebridge.package --profile profiles/manor.json --preflight
py -m forgebridge.package --profile profiles/manor.json --out builds/manor-v1.zip
```

See [October 31 player evidence](validation/2026-10-31-PROFILE-PLAYER.md) for the
accepted Crypt token hide/restore and both-profile player restart checks. No map
was saved in that pass. A later Codex capture-target mismatch blocks new desktop
work without invalidating those observations; see [resume evidence](validation/2026-10-31-RESUME.md).

Desktop validation now follows a [CPU-aware runbook](docs/DESKTOP-VALIDATION.md)
with a read-only load sampler, separate compute/UI phases and sequential captures.
Verified operating settings are Toolkit 30 FPS and player streaming 1280×720 at
15 FPS. Later low-load failures show CPU contention is not the sole explanation
for desktop timeouts. Pending runtime checks do not block reader, profile or
dependency-tooling development.

ForgeBridge is a proposed migration/transpilation tool for converting **Foundry Virtual Tabletop** content into the closest practical **Arkenforge** equivalent.

The goal is deliberately more ambitious than extracting images or flattening maps. ForgeBridge should preserve as much *meaning and behavior* as practical: scenes, walls, doors, lights, tokens, audio, journals, actors, items, roll tables, and—where possible—Foundry-specific automation.

## Core idea

```text
Foundry module / world / export
          |
          v
    Foundry adapters
          |
          v
  ForgeBridge IR
 (platform-neutral)
          |
    +-----+------+
    |            |
    v            v
Native mapping  Behavior analysis
    |            |
    |       deterministic parser
    |            +
    |       optional LLM assistance
    |            |
    +-----+------+
          |
          v
 Arkenforge output
 + migration report
```

The architectural rule is:

**Foundry -> ForgeBridge Intermediate Representation -> Arkenforge**

Do not build this as a growing pile of direct one-off Foundry-to-Arkenforge transformations.

## Why an intermediate representation?

Foundry contains both portable concepts (maps, walls, lights, tokens, audio) and platform/system-specific concepts (Actors, Active Effects, macros, module flags, automation).

The IR gives ForgeBridge a place to describe *intent* independently of either platform. For example:

```yaml
behavior:
  trigger: open_object
  source: Sarcophagus
  actions:
    - play_audio: coffin.wav
    - reveal_token: Mummy01
    - enable_light: Light03
    - show_note: Journal17
```

An Arkenforge backend can then decide whether each behavior can be reproduced natively, approximated, exposed as a GM hotkey/action, or merely documented.

## Initial mapping hypothesis

| Foundry | Arkenforge target |
|---|---|
| Scene/background | Map |
| Grid/dimensions | Map/grid configuration |
| Walls | Barriers |
| Doors/windows | Toggleable/special barriers where supported |
| Ambient lights | Lights |
| Tiles | Map assets |
| Tokens | Tokens |
| Ambient sounds | Positional/map audio |
| Journals/notes | Encyclopedia/campaign notes or closest equivalent |
| Actors/NPCs | Character/encyclopedia/stat representation + token |
| Items/spells | Item/spell/stat representation where available |
| RollTables | Rollable-table equivalent where available |
| Playlists | Playlist/soundscape equivalent |
| Hidden/revealed content | Visibility controls |
| Regions/triggers | Native trigger if available; otherwise behavior approximation |
| Active Effects | Behavior/metadata approximation |
| Macros | Translation/emulation layer |
| Module-specific automation | Adapter + behavior analysis, case by case |

Exact mappings must be verified against the Arkenforge version/API/file formats available when implementation begins.

## Macro and automation strategy

ForgeBridge should **not** ask an LLM to blindly rewrite arbitrary Foundry JavaScript.

Preferred pipeline:

1. Parse macro/source statically.
2. Identify known Foundry API calls and referenced documents/assets.
3. Resolve references where possible.
4. Convert recognized operations into ForgeBridge behavior IR.
5. Use deterministic Arkenforge mappings first.
6. Optionally invoke an LLM only for ambiguous/long-tail behavior interpretation.
7. Validate any model-produced IR against a strict schema and allowed capability catalog.
8. Never silently discard unsupported behavior.

Every conversion should classify functionality as one of:

- **Native** — direct equivalent.
- **Approximate** — functionally similar representation.
- **Hotkey / GM action** — prebuild the pieces and expose a manual trigger.
- **GM-assisted** — partial recreation plus clear instructions.
- **Unsupported** — preserve source/reference and explain what could not be migrated.

Example: a Foundry macro that opens a sarcophagus, reveals a monster, plays audio, changes lighting, and opens a journal could become a single Arkenforge-side GM action/hotkey if those individual operations can be controlled, even when the original Foundry event trigger cannot be reproduced.

## Optional LLM / MCP layer

AI should be an **optional compatibility assistant**, not a requirement for ordinary conversion.

Potential uses:

- interpret unfamiliar macros and module automation;
- infer semantic intent from code after static analysis;
- propose mappings from system-specific Actor/Item fields;
- generate human-readable migration explanations;
- suggest safe GM-assisted equivalents when no direct feature exists.

Potential MCP/integration work could expose Foundry documents or an Arkenforge automation/control surface to the migration engine. This is exploratory. ForgeBridge must still support offline/deterministic conversion for ordinary assets and scene structures.

## Migration report

A major deliverable should be a report produced *before* or alongside conversion:

```text
Adventure
--------------------------------
Scenes                  34 / 34 convertible
Walls                 1842 / 1842
Doors                    96 / 96
Lights                   73 / 73
Tokens                  211 / 228
Journal Entries          87 / 87
Actors                   61 / 74
Items                   319 / 344
Roll Tables              18 / 18
Playlists                 9 / 9

Macros                    47
  Native                  12
  Approximate             19
  Hotkey / GM action       9
  GM-assisted              5
  Unsupported              2
```

Unsupported or lossy conversions should be conspicuous rather than quietly dropped.

## Proposed phases

### Phase 0 — Research spike
Document Foundry package/world/export structures, supported Arkenforge import/content formats, and any safe automation/interface surface. Collect representative legal test fixtures.

### Phase 1 — Asset bridge
Accept a Foundry module ZIP/folder or export, inventory assets, normalize paths/names as necessary, and produce an Arkenforge-friendly asset bundle plus report.

### Phase 2 — Scene bridge
Convert scene geometry and presentation: map/background, dimensions/grid, walls/barriers, doors, lighting, tiles, tokens, and ambient audio. Use UVTT as an interchange option where it preserves useful information, but do not let UVTT define the ceiling of ForgeBridge.

### Phase 3 — Campaign content
Translate journals/notes, actors/NPCs, items/spells, roll tables, playlists, links, and other structured content where meaningful equivalents exist.

### Phase 4 — Behavior engine
Introduce ForgeBridge behavior IR, deterministic macro recognition, triggers/actions, approximations, GM actions/hotkeys, and detailed compatibility reporting.

### Phase 5 — AI-assisted long tail
Optional constrained LLM analysis for otherwise unsupported automation and system/module-specific structures. All AI output must be schema-validated and reviewable.

### Phase 6 — Adapters
Add explicit adapters for popular Foundry systems/modules only where demand justifies the maintenance burden.

## Non-goals

- Reimplement Foundry inside Arkenforge.
- Guarantee lossless conversion of arbitrary Foundry modules.
- Execute untrusted Foundry macros during analysis.
- Depend on an LLM for deterministic content.
- Circumvent licensing, DRM, access controls, or publisher restrictions.
- Redistribute commercial assets. Users are responsible for having rights to migrate/use their content.

## Design principles

1. **Preserve intent, not just files.**
2. **Deterministic first; AI only where useful.**
3. **Never execute imported arbitrary code.**
4. **Never silently lose information.**
5. **Report confidence and conversion quality.**
6. **Keep source provenance/IDs so conversions are auditable.**
7. **Use adapters instead of contaminating the core with module-specific hacks.**
8. **Prefer reviewable generated actions over opaque automation.**
9. **Treat commercial content licensing as a first-class constraint.**
10. **Follow the current milestone in STATUS.md.** Implement only the work that page names as the current state.

## When this project is resumed

The first implementation session should **not start coding the converter immediately**. First verify current Foundry and Arkenforge formats/capabilities, obtain a few representative test packages, write the initial IR schema, and build an inventory-only CLI. That gives us a measurable corpus before deciding how ambitious the first conversion milestone should be.

That session is the inventory spike recorded in [STATUS.md](STATUS.md). The current milestone writes a UVTT file plus the scene's importable image and audio files, also recorded there.

---

This README captures the ForgeBridge concept. A UVTT file plus the scene's importable image and audio files is the current work.


## Tested Arkenforge import compatibility (2026-10-08)

Install `requirements.txt` before exporting; Pillow normalizes embedded backgrounds to compatible PNG. UVTT output now uses the native-tested geometry/light structure. Every `--uvtt-out` also writes a `.forgebridge.json` companion preserving the complete selected source scene and loss report. Imported door states are preserved, but blocking capabilities may need enabling in Arkenforge. See [the current compatibility notes](docs/compatibility/UVTT-SLICE.md) for evidence, limitations, and the next source-scene validation.

### Experimental native note smoke test

The native writer is an import experiment, separate from Foundry/UVTT conversion.
Generate two synthetic linked notes and one three-result table:

```powershell
$env:PYTHONPATH = "$PWD\src"
py -m forgebridge.native --out ForgeBridge_Native_Notes_Test.zip
```

Choose a new output filename; existing files are not overwritten. Extract the
ZIP and copy its `ForgeBridgeTests` folder from
`MyAssets/Encyclopedia/Notes/` into the matching folder in your existing
Arkenforge `MyAssets` directory while the Toolkit is closed. Reopen the Toolkit,
search for `ForgeBridge Native Test A`, inspect its text/line breaks, click its
link to B and B's link back, and roll A's table. The three possible results are
`ForgeBridge result one`, `ForgeBridge result two`, and `ForgeBridge result three`.

The user verified synthetic text, bidirectional links and matching table
outcomes in the Toolkit. Links require the exact installation path. A subsequent
startup log showed denied writes under Program Files; it does not establish
that the generated files damaged installed packs. Visibility remains unverified.

### Experimental native journals from a companion

Convert the already-retained scene journals/pages and supported tables:

```powershell
$env:PYTHONPATH = "$PWD\src"
py -m forgebridge.native --companion counts_crypt_links.forgebridge.json --out counts_crypt_native_notes.zip
```

This does not read the original Foundry package again. The ZIP includes a scene
index, journal indexes, separate page notes, table notes, `INSTALL.txt`, a
conversion report and the unchanged source companion. Copy only the generated
`ForgeBridge-...` folder into the existing `MyAssets\Encyclopedia\Notes` directory.
Keep its name and filenames unchanged: native links target the exact metadata
paths. Existing output ZIPs are never overwritten. Different retained content
gets a different folder to avoid overwriting a previous import.

Resolved journal/page/table UUIDs become native links. Additional pages are
checked against already-retained documents only; unresolved links remain literal
source references and are reported. HTML becomes plain text; media are explicit
references rather than copied assets. Non-BMP text characters are replaced and
reported. Original HTML, source permissions and all unknown data remain in the
companion. Only contiguous, unit-weight text outcomes on `1dN` replacement
tables become rollable; other table semantics remain readable references.

Review visibility before player use. The user verified Crypt room/rules links
and table rolls; handout files remain missing. This notes-only command generates
no native map or actor conversion;
the report retains scene-note grid positions and exact native targets for later
map-placement work. See `docs/research/NATIVE-NOTES.md` for evidence and limits.

### Experimental markers in an exported native map

`forgebridge.native_map` copies a single manually saved map export and inserts
the companion's room-note markers using an explicitly calibrated transform.
It requires an existing native note marker as its template. For the supplied
Crypt calibration export, one grid square is 2.56 native units and the image's
upper-left corner is (0, 0):

```powershell
$env:PYTHONPATH = "$PWD\src"
py -m forgebridge.native_map --template-pack assets_with_markers.zip --companion counts_crypt_links.forgebridge.json --out counts_crypt_native_map.zip --name ForgeBridge_Crypt_With_Notes --units-per-grid 2.56 --origin 0 0 --remove-marker "FB Cal A" --remove-marker "FB Cal B" --remove-marker "FB Cal C"
```

The ZIP contains a separately named map, generated notes, and the exported
media. Existing image, wall, door and light records are preserved. It does not
build a native map from scratch or infer a transform for other maps. Output
must use a new filename. The user verified the Crypt markers open their notes and persist after
save/reload. Player visibility remains unverified. Permanent room labels are optional and off by default.

To generate editable native room labels, the template export must contain a
text object whose text matches `--text-template` (default `Igor's Room`). Use
`--marker-labels on`; use `--marker-labels off` or omit the option to add none.
The switch is an **export option**, not an added Toolkit control.

For the supplied saved Crypt map with native text:

```powershell
$env:PYTHONPATH = "$PWD\src"
py -m forgebridge.native_map --template-pack MyAssets_with_text.zip --companion counts_crypt_links.forgebridge.json --out counts_crypt_labels.zip --name ForgeBridge_Crypt_With_Labels --units-per-grid 2.56 --origin 0 0 --template-name "Igor's Room" --marker-labels on
```

Matching existing room markers keep their exact native positions and UIDs;
exported native notes are preserved. The template's manual text object is
replaced with one generated label per room. Label style/font/size come from
that native object. Labels default to 1.25 grid squares right of the marker;
`--label-offset X Y` changes this offset (positive Y means down). Generated
labels have Hidden from players enabled, do not emit light or block movement,
light, vision or sound, and remain separate editable text objects. Verify their
appearance and Player View before use. Re-exporting a labelled map with labels
off removes ForgeBridge-labelled text objects; unrelated manual text remains.

### Collect journal handout files

Labels are deferred for further testing. Keep `--marker-labels off` (the default).
The Toolkit's simulated view left selected and deselected labels visible while
the map image disappeared; this is not a successful player visibility test.

To collect image, PDF, audio and video references from the retained journal/table
documents, use the original Foundry package and the existing companion:

```powershell
$env:PYTHONPATH = "$PWD\src"
py -m forgebridge.handouts --package "C:\AMD\lob-counts_manor-pk-v13.zip" --companion counts_crypt_links.forgebridge.json --out counts_crypt_handouts_v1.zip
```

Extract this ZIP to a separate folder. `assets/` contains original media;
`handout-report.json` maps references and journal fields to those files, records
sizes/hashes, and distinguishes missing, external, other-package, rejected and
unsupported references. Repeated references share one file; identical basenames
in different source directories remain distinct. URL-encoded local paths are
decoded, with traversal and symlink checks. No URLs are fetched and no source
content is executed. Collection is limited to 64 MiB per file and 256 MiB total.

This is a collection for inspection, not an Arkenforge import pack: do not copy
it into MyAssets. Existing native note links are unchanged. Native handout
fields/media linking still need a controlled exported sample and Toolkit test.
Use a new output filename; existing files are not overwritten.

### Native image attachment test

A controlled exported image note established `ArkenNoteFieldMedia` and its
`_contentPathRelative` link to native media `.rwmeta`. The supplied image and
thumbnail are embedded PNGs in `.rwfile` and `.rwmeta` respectively. Generate
a separate test note from this small export:

```powershell
py -m forgebridge.native_media --template-pack FB_Media_notes.zip --out native_image_test.zip
```

Follow its INSTALL.txt. It generates a fresh note with a native Media field,
relocates the supplied image asset pair while keeping its original filename,
metadata and complete file bytes. It does not overwrite the original note/map, add room labels,
convert arbitrary Foundry images or handle PDFs. Toolkit display and persistence
must pass before integrating source handouts. Native visibility is unverified.

The first image test reported a missing `.rwfile` despite both files being
present. The revised v2 test retains original asset names/provenance and the
source media-category folder layout. Its note is **ForgeBridge Generated Image
Test v2**. The exact v1 lookup cause remains unconfirmed.

The user subsequently confirmed v2 image display, note reopening and Toolkit
restart all pass. The exact v1 lookup cause is still uncertain.

### Attach collected images to converted journal notes

Use the existing source companion, collected handout bundle and small exported
native media template. Keep all three input files in the working folder:

```powershell
$env:PYTHONPATH = "$PWD\src"
py -m forgebridge.native_media --template-pack FB_Media_notes.zip --companion counts_crypt_links.forgebridge.json --media-bundle counts_crypt_handouts_v1.zip --out counts_crypt_image_notes_v1.zip
```

The output supplies generated notes and native image pairs. Follow INSTALL.txt:
back up MyAssets, then merge the contents and replace matching generated note
files. This regenerates notes from the source companion, so retain any manual
edits in the backup. Note folder/filenames and room-marker targets are unchanged.
No map or room labels are emitted. Image pages and inline images get native
Media fields; repeated references share one asset and duplicate occurrences in
a note share one field. PNG/JPEG/static WebP/GIF are re-encoded as RGBA PNG with
aspect-preserving thumbnails. The template's native names/filename agree and
its media-category layout is retained. The user confirmed Count's Crypt source-image
display, proportions, note reopening and Toolkit restart. Other packages still
require Toolkit checks; native map asset placement is unverified. Attachments
follow each note's source occurrence order and use readable source-filename
titles (for example, Image — Raven skull cane). They remain below the text;
original HTML layout is not reproduced.

The handout report's scene, reference origins and copied asset sizes/hashes must
match the current companion and ZIP. PDFs and animations remain references;
collection gaps and failed images are reported. `conversion-report.json` lists
native image assets, attached note targets and unresolved media. Check portrait
and landscape handouts, room-note navigation, and note/restart persistence.

### Optional PDF handout page images

Arkenforge's published import formats do not list PDF. To view collected PDF
handouts inside notes, install the optional renderer and enable page images:

```powershell
py -m pip install -r requirements-pdf.txt
py -m forgebridge.native_media --template-pack FB_Media_notes.zip --companion counts_crypt_links.forgebridge.json --media-bundle counts_crypt_handouts_v1.zip --pdf-pages --out counts_crypt_pdf_notes_v1.zip
```

This keeps existing note/marker paths and image attachments. Each PDF becomes
numbered native Media fields in source/page order. Successfully converted
original PDFs are retained byte-for-byte in `original-pdfs/` outside MyAssets,
with source references and hashes in the conversion report. They are page
images, not searchable text or interactive PDFs. Rendering is up to 144 dpi,
capped at 2400 pixels per side, 32 pages per PDF and 128 pages per package.
Invalid/encrypted PDFs remain explicit references; package size limits still
apply. Without `--pdf-pages`, PDF references behave as before.

Back up MyAssets and any manually edited generated notes before replacing them.
Check a single-page letter and all six pages of Court of Ravenloft for readable
text, correct page order, note reopening and Toolkit restart. PDF page runtime
behavior is pending; labels remain off and player visibility is unverified.

### Readable note folders

Native map and source-media commands accept `--note-folder`, for example
`--note-folder "ForgeBridge - Manor - 2nd Floor"`. Use the same value for both
commands so generated map markers and image/PDF notes share their target paths.
The folder must be one portable name, without slashes or reserved Windows names.
Choose a distinct folder for each scene/package. Without the option, existing
hash-based folder paths stay compatible. Navigation note titles now use the
scene name followed by `— Start Here`.

Changing this option changes note paths: regenerate map markers and notes
together in a separate map copy. Renaming a folder in File Explorer alone will
break references. Keep the old map and notes until the new copy is verified.

### One-command native package build

After exporting the scene companion and saving/exporting its calibrated native
Arkenforge map, build markers, linked notes, images and optional PDF pages in
one operation. Install `requirements.txt` and, for PDFs, `requirements-pdf.txt`.
Use a map export containing the `FB Cal A` marker and its note. For the tested
second-floor inputs:

```powershell
$env:PYTHONPATH = "$PWD\src"
py -m forgebridge.package --package "C:\AMD\lob-counts_manor-pk-v13.zip" --companion counts_manor_second_floor_test.forgebridge.json --map-template "MyAssets(1).zip" --media-template FB_Media_notes.zip --name "Manor - 2nd Floor - ForgeBridge" --note-folder "ForgeBridge - Manor - 2nd Floor" --units-per-grid 2.56 --pdf-pages --out manor_second_floor_complete.zip
```

`--package` collects assets from the original source. Alternatively use
`--media-bundle` with a previously collected bundle matching this companion.
The command produces one ZIP, conversion report and INSTALL.txt; the original
PDFs and collection report remain outside MyAssets. Labels stay off, and native
marker icons are retained. Scale/origin must be calibrated to the supplied map;
2.56 is the tested second-floor value, not a universal assumption.

If the export includes existing generated notes in the selected note folder,
the command stops. Back up those notes and pass `--regenerate-notes` only when
rebuilding from source is intended. Other exported assets may not be silently
replaced with conflicting media. Existing output filenames are never overwritten.
Inputs must come from the same scene/package. The native map export and Toolkit
import steps are still necessary; this command does not control Arkenforge.


## Experimental placed-token slice

This requires an exported native map containing one manually created **Token**
control with a native Size field, its note/image files and dependencies. Save and
reopen that control first: Toolkit 0.5.1.18 normalizes transform-only sprite scale
from Size. Preserve the original control export and use a distinct output/map name.

```powershell
$env:PYTHONPATH = "$PWD\src"
py -m forgebridge.native_tokens --template-pack CONTROL.zip --companion SCENE.forgebridge.json --package MODULE_FOLDER --out NEW-TOKENS.zip --name "Separate Token Test" --control-name "Stoker_token_1" --units-per-grid 2.56 --control-units-per-grid 2.56 --origin 0 0
```

The values above describe the tested control, not universal defaults. Calibrate
`--units-per-grid` as native units per **source** square and
`--control-units-per-grid` as native units per **native Size** square. The origin is
the native upper-left of the unpadded background. Source padding (rounded to source
grid cells), grid size and token half-footprint enter center placement. For the
manor, (2000,2800) source pixels become center (12.5,18.5) source squares, then
(32,-47.36) native units with the observed calibration.

This slice supports square footprints, centered static square textures and positive
texture scales up to one. Texture scaling is baked into a transparent canvas;
Size controls the footprint. It writes identity, name, image, position, Size,
rotation and hidden flags. Asymmetric 0/90/180/270-degree arrows and hidden-state
round trips pass in actual player output on the documented combined test scene,
including Toolkit restart. Other scenes still require validation. Actors, statistics, scripts, vision, fog, lights and combat
behavior remain retained source data with explicit report entries. Unsupported
geometry/media are reported rather than replaced. The archive preserves the
original control map/note assets because native metadata can link back to them;
installation must abort on conflicting existing content. The command does not
install anything and refuses output overwrite or a colliding map name.

To include the same token writer in the complete scene package, use the original
source directory and add the calibrated token control options:

```powershell
py -m forgebridge.package --package MODULE_FOLDER --companion SCENE.forgebridge.json --map-template FRESH-NATIVE-EXPORT.zip --marker-template-pack MARKER-CONTROL.zip --media-template IMAGE-NOTE-CONTROL.zip --name "Separate Combined Scene" --note-folder "Separate Scene Notes" --units-per-grid 2.56 --origin 0 0 --token-control-pack TOKEN-CONTROL.zip --token-control-name "Stoker_token_1" --control-units-per-grid 2.56 --pdf-pages --out NEW-COMBINED.zip
```

Omit `--marker-template-pack` when the geometry export already contains the
calibration marker control. The builder clones controls into the same generated
map, preserves existing map content and original map/metadata backlinks, includes
required control dependencies, and rejects conflicting or missing references.
Token assets are deterministic and namespaced by output map name to prevent
different scene copies from sharing mutable token notes. No ZIP surgery is needed.
The reports retain full source data and per-token rejection reasons; a missing
texture does not discard other supported tokens. Install only absent or identical
files and stop on conflicts with existing content. GIF import/playback remains a
manual Arkenforge operation; procedural Foundry light animations have no proven
mapping. Neither native fog operation nor token hidden state implements Foundry
vision/fog conversion.
