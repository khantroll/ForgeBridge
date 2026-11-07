# Changelog

## Unreleased

- Normalize FG prose newline escapes, preserve paragraph spacing and use shared explicit light journal/story text. Merge native empty-row collapse requests for legacy stat blocks; visual acceptance remains pending after the trial.

- Convert FG range tables, manual chapter/page navigation, treasure parcels, quests
  and image attachments; report unknown record types and unsupported roll behavior.

- Combine Fantasy Grounds maps, campaign notes, room pins and portrait tokens
  through the normal convert/GUI/review/install flow; explicit notes-only mode.
- Read nested/category FG and SRD records, formatted block text and qualified
  links; preserve string stats and non-5e source attacks without invented 5e rules.
  Missing grids/art and portrait-safe omitted NPC bindings remain reported limits.

- Development: schema-built Foundry video/animated-image tiles and map-attached
  ambient sounds with calibrated placement, bounded codecs and explicit losses;
  owned FB Motion Check fixture and reviewed install for pending Toolkit acceptance.
- Omit missing-CR Challenge labels and request zero-size empty stat rows; visual
  gap collapse still needs the Toolkit check. Native active flags remain respected.
- Add schema-built native Dynamic fog/persistence, bounded owned-character vision, flicker/blink and negative-light mapping with explicit approximation reports. File-level coverage only; runtime acceptance pending.

- Revision-scoped campaign note and playlist filenames preserve Toolkit-edited
  predecessors retained by uninstall; displayed playlist names stay unchanged.

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
