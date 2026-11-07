# Changelog

All notable changes to ForgeBridge. Each release links to its full release notes,
which list exactly what was tested and how.

## v0.13.0 — 2026-11-07

Combined Fantasy Grounds adventures, fog/vision conversion, and animated tiles.
[Release notes](docs/RELEASE-NOTES-v0.13.0.md)

### Added

- **Fog, vision and light animation** from Foundry scenes.
- **Foundry Data folder art:** optionally point ForgeBridge at your Foundry Data
  folder to pick up art an adventure references but doesn't include.
- **One build for whole Fantasy Grounds adventures:** maps, NPCs, items, spells,
  story entries, tables, manuals, parcels, quests and handouts now convert together
  through the same app and review screen.
- **Animated and video tiles** (WEBM/GIF) and **map-placed ambient sounds** (OGG/WAV).

### Fixed

- Fantasy Grounds text: line breaks, colours, paragraphs and empty rows now display
  correctly. Checked across 2,129 notes from real modules.
- Reinstalling no longer overwrites campaign notes you edited after a previous install.

### Not yet verified in Arkenforge

v0.13.0 passed automated Windows and Linux tests, but no v0.13.0 build has been
opened in the Toolkit yet. Animated tiles, ambient sound and the Fantasy Grounds
workflow were checked by hand using earlier test builds. Fog/vision, Data folder art
and the Fantasy Grounds text fixes are new and should be reviewed after import.

### Known limitations

- Not converted: some animation effects, scene darkness level, previously revealed
  fog, full vision rules, and actor/combat automation.
- Monsters and items that exist only in a source compendium, Fantasy Grounds
  environment details, playlist loop/volume settings and weighted or formula
  roll tables still need manual work.
- Encrypted Fantasy Grounds modules are refused. Only Foundry v13 with dnd5e is supported.
- The Windows EXEs are unsigned, so SmartScreen will warn on first launch.

## v0.12.0 — 2026-11-05

Spells, music, and Fantasy Grounds campaign notes.
[Release notes](docs/RELEASE-NOTES-v0.12.0.md)

### Added

- **Spells linked from the dnd5e system:** many adventures only link to spells
  rather than including them. Point ForgeBridge at the free dnd5e system download
  (`--dnd5e-system`, or the field in the app) and those links become real spell
  notes. Foundry doesn't need to be installed.
- **MP3 and OGG music** is now embedded directly in playlists and plays in the
  Toolkit at its default volume.
- **Fantasy Grounds campaign notes:** NPCs, items, spells and story entries, with
  the same backed-up, add-only install and uninstall as Foundry content.
- **Windows standalone app** tested on a machine without Python.

### Changed

- Foundry inline references (`@UUID`, `&Reference` and similar) display as plain
  labels instead of raw markup.
- Stat blocks hide empty Skills, Senses and Languages rows, and cantrips read
  "Evocation cantrip" instead of "level 0".
- Links on parchment-style stat blocks use a darker, readable colour.

### Fixed

- The app won't install after you rename maps until you rebuild, so names and
  files can't get out of sync. Map names stay unique across your whole library.
- A spell that can't be found is reported once, not twice.

## v0.11.0 — 2026-11-03

Fantasy Grounds maps, the Windows app, and Foundry campaign content.
[Release notes](docs/RELEASE-NOTES-v0.11.0.md)

### Added

- **Fantasy Grounds Unity maps** from `.mod` files, folders and unencrypted vaults,
  including walls, doors and grids.
- **Windows app:** `ForgeBridge.exe` and `forgebridge-cli.exe` in one folder,
  with everything bundled. No Python needed. Release ZIPs are built automatically.
- **Foundry campaign content:** roll tables, dnd5e NPCs, items and spells as
  stat-block notes, character portraits, and working journal links.
- **Map tiles and playlists** from Foundry scenes.
- Version number shown in the app title and `--version`; errors in the Windows
  app are logged and shown instead of failing silently.

### Fixed

- Tokens keep their portraits. Linking tokens to stat-block notes replaced the
  portrait with a note icon, so those links are left off.
- Armour class, attack bonuses, languages and speed now read correctly on stat blocks.
- Reinstalling keeps notes you've edited.

### Known limitations

- MP3 music, external art, and Fantasy Grounds pins, story notes and tokens
  still needed manual steps in this release.

## v0.10.0 — 2026-11-02

Naming, PDF handouts, and cleaner uninstall.
[Release notes](docs/RELEASE-NOTES-v0.10.0.md)

### Added

- Choose your own map folder, notes folder and map names in the app or CLI.
  Defaults use the adventure and scene names. Name clashes are reported, never
  silently renamed.
- PDF handouts are rendered into note pages.
- Uninstall removes empty folders that the install created.

### Fixed

- The app keeps a link to the loss report after installing.
- Clearer message when the output folder already exists.

## v0.9.0 — 2026-11-02

First release: Foundry VTT scenes to native Arkenforge maps, notes, markers and
tokens, from one command or the app. Includes a backed-up, add-only installer
with uninstall, and a report listing anything that couldn't be converted.
[Release notes](docs/RELEASE-NOTES-v0.9.0.md)
