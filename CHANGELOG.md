# Changelog

## v0.13.0 — 2026-11-07

### Checked in Arkenforge Toolkit (earlier check builds)

- Generated WEBM/GIF tiles animate; placed OGG/WAV ambience is audible.
- Sampled real FG NPC/story notes and owned FG pin/portrait-token controls work.
  The real Well Met module has no source pins/tokens; do not conflate the controls.
- v0.12 enricher labels, parchment-link colour, missing stat labels/proficiency
  and cantrip type text were checked. MP3/OGG music and spell links retain prior evidence.

### File-level only (not yet seen in the Toolkit)

- Fog/vision/light animation (#33), optional Foundry Data art (#30), and post-trial
  FG newline/colour/paragraph/empty-row corrections (#32). Gap collapse unverified.
- Combined FG conversion retains tables/manuals/parcels/quests/handouts and all
  prior real counts; 2129 notes / 13925 text strings audited without newline escapes.
- Shared FG maps/notes/tables/manuals/placements use one convert/GUI/review path.
- Version 0.13.0 metadata/fallback/tests and Windows one-folder release workflow.
- Revision-scoped campaign filenames preserve edited predecessors kept by uninstall, without changing displayed names.

### Known limitations

- Ghost/other unsupported effects, uncalibrated scene darkness and Toolkit-wide
  Simulate darkness; fog history, full vision rules and behavior remain gaps.
- Encrypted FG inputs refused; supported semantic target dnd5e / Foundry v13 only.
- Unsigned EXEs trigger SmartScreen; compendium monsters/items, FG environment
  details, playlist settings, weighted/formula rolls and cleanup remain open.
- No new Toolkit runtime evidence: the trial has ended. Full details and evidence
  split: docs/RELEASE-NOTES-v0.13.0.md.

## v0.12.0 — 2026-11-05

- Embed MP3 and OGG Vorbis playlist bytes directly, preserving extensions and
  initializing the Master stem; safely resolve encoded local audio paths.
  Count's Manor Ambient's three tracks were heard in Toolkit 0.5.1.18.
- Resolve optional dnd5e spell-pack links into 5e Spell notes; the three Count's
  Manor scroll links were checked in Toolkit.
- Fantasy Grounds NPC/item/spell/story notes have native packages, add-only
  install, backups and uninstall receipts; representative notes/images/links
  were checked in Toolkit. Encrypted modules remain refused.
- Refuse GUI install after map names change until rebuilding. Map names stay
  unique across the whole MyAssets library.
- File-level display fixes: flatten Foundry @/& enrichers to inert labels,
  use dark links on 5e parchment blocks, omit empty Skills/Senses/Languages and
  unknown proficiency, and label level-zero spells as school + cantrip.
  These display changes have regression coverage, not a new Toolkit check.
- Windows standalone GUI/CLI ZIP built and smoke-tested without Python on PATH.


- Fixed native music playlist stem initialization: generated single-stem songs
  now receive the Toolkit user-import default `Master` volume (80%) instead of
  an empty mixer dictionary. User ContentItem records use the current two-field
  schema. Payload bytes/codec are preserved; MP3 and OGG Vorbis are now embedded directly after native playback confirmation.
  Encoded local audio paths resolve safely; final-check campaign notes use a new
  internal revision so kept edited predecessors are not overwritten.

- Optional `convert --dnd5e-system` and GUI input resolve exact external dnd5e
  spell UUIDs to native 5e Spell notes, using the captured schema and styles.
  Referencing actor/item prose links are rewritten; missing source IDs and
  unsupported media remain graded losses. System folder/ZIP and standalone
  JSON/NeDB/LevelDB spells packs are read-only, bounded and fingerprinted.
- Docs: plain-English README/user-guide steps for downloading the free dnd5e
  system (needed for spells an adventure only links to). No Foundry install is
  needed. Unzip the release first, because its ZIP exceeds the per-entry read budget.
- Fixed: a missing external spell is reported once (`external-spell`), not
  also as an unresolved `link` loss. Link-alias iteration is now sorted.
- Validated: Count's Manor's Bless, Spiritual Weapon and Protection from Poison
  IDs resolve from the real dnd5e 6.0.6 system at file level
  (`validation/2026-11-04-SPELLPACK-REAL-RUN.md`).

## v0.11.0 — 2026-11-03

Fantasy Grounds Unity native maps, the Windows standalone app, and Foundry
campaign content. [Release notes](docs/RELEASE-NOTES-v0.11.0.md).
Audible MP3/OGG playback is not confirmed by ear; external art remains manual;
encrypted FG modules are refused; Windows executables are unsigned (SmartScreen
may warn).

- Fixed: current user playlist/song metadata (including previous-path members),
  display-name audio filenames and the chosen notes-folder layout.
- Fixed: omit token stat-block links after Toolkit showed they replaced map
  portraits with note-marker icons; preserve v0.10 token files instead.
- Fixed: equipment AC and structured attack bonuses, duplicate languages and
  walk-first speed text. Explicit source natural AC/attack abilities are honored.
  Revised campaign-note filenames preserve edited v1 notes during reinstall.

- Added: adventure-wide Foundry roll-table, dnd5e actor/item/spell display notes,
  local portraits and journal links. Native records use captured member schemas;
  scoped Toolkit checks confirmed stat-block/item/table rendering. Actor links
  from tokens are omitted to preserve portrait appearances.
- Added: static map tiles and native playlists/OGG song records, with explicit
  manual MP3, animation, missing-media and behavior losses. Shared campaign
  content deduplicates across selected scenes; reports retain original objects.

- Added: Fantasy Grounds .mod/folder/unencrypted-vault detection in convert,
  discovery and GUI, with ART filtering, explicit per-map grids and module-based
  visible naming. Stored grids always win; fractional image resampling is reported.
- Added: FG UVTT geometry through the shared native map/background/thumbnail
  writer and existing reviewed add-only installer/receipts. Source counts,
  metadata source, resampling and graded losses appear in reports/GUI.
- FG pins, story and tokens remain manual; encrypted modules remain refused.
  Scoped FG native geometry was checked in Toolkit 0.5.1.18.
- Fixed: rejected FG module initialization closes its archive immediately,
  including encrypted-input errors surfaced through the GUI.
- Added: Windows x64 one-folder GUI/CLI bundle, `ForgeBridge.exe` and
  `forgebridge-cli.exe`, with bundled Python, Tcl/Tk, native dependencies and
  schemas. No Python installation needed to run the app.
- Added: executable smoke tests, workflow artifacts and automatic release ZIP
  attachment for new version tags, retaining artifacts if publication is refused.
- Added: package version in CLI --version and GUI title; local error logs and
  visible worker/callback/startup error reporting for windowed builds.
- Fixed: inventory schema accepts the generator's application release version
  independently of the unchanged 0.1.0 IR version.

## v0.10.0 — 2026-11-02

- Added: user-chosen map folder, notes folder and map names (GUI and CLI);
  defaults to the Adventure name and plain scene names; Windows-safe names;
  name clashes reported, never silently renamed.
- Added: PDF handouts rendered into note pages by default (`--pdf`).
- Added: uninstall removes empty folders the install created; re-running on an
  already-uninstalled receipt tidies leftover folders only.
- Fixed: GUI keeps a pointer to the build loss report after installing; PDF
  checkbox falls back to references; clearer "output folder exists" message.
- Docs: rewritten quick start from the first fresh-setup run.
- Details: [release notes](docs/RELEASE-NOTES-v0.10.0.md).

## v0.9.0 — 2026-11-02

First release candidate: Foundry VTT scenes to native Arkenforge maps, notes,
markers and tokens with one command or a GUI; backed-up add-only installer with
uninstall receipts; graded loss report. Details:
[release notes](docs/RELEASE-NOTES-v0.9.0.md).
