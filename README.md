# ForgeBridge

> **Status: UVTT, SOURCE PRESERVATION, AND JOURNAL CORRELATION**
>
> The current work exports one scene as UVTT, copies its loose image/audio assets, and preserves full scene data plus linked journals and roll-table dependencies in a companion JSON. A readable room-notes reference accompanies the map. Native Arkenforge note creation is not implemented. See [STATUS.md](STATUS.md).

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
must use a new filename. Toolkit placement, clicking, save/reload and player
visibility tests remain pending.
