# ForgeBridge v0.11.0 — Fantasy Grounds, Windows app and campaign content

Release date: 2026-11-03. Builds on [v0.10.0](RELEASE-NOTES-v0.10.0.md).
Download the Windows ZIP from [GitHub Releases](https://github.com/khantroll/ForgeBridge/releases).
The Windows ZIP is attached by the release workflow after the approved release
commit is tagged.

## What's included

- **Fantasy Grounds Unity → native Arkenforge maps.** Read unencrypted `.mod`
  files, module folders and supported unencrypted vault-style ZIPs through the
  same discovery, GUI, conversion and reviewed install workflow. Backgrounds,
  grids, walls, doors, windows and lights use the existing native map writer.
  Stored grids take precedence; maps without a grid require an explicit pixels
  per square or squares-across value. Artwork is hidden by default; fractional
  grid resampling and source losses are reported.
- **Windows app without Python.** Unzip `ForgeBridge-0.11.0-windows-x64.zip`
  into a normal user folder and run `ForgeBridge.exe`. The same folder contains
  `forgebridge-cli.exe` for CLI conversion, install and receipt-based uninstall.
  Keep both executables and `_internal` together. Python/Tcl/Tk, native libraries,
  PDF rendering and schemas are bundled. Windows build and executable smoke
  tests run in CI. Both executables carry the package version in build metadata;
  `--version` exits without opening the GUI (the windowed EXE has no console).
- **Foundry campaign content.** The selected Adventure's roll tables become
  native rollable-table notes; dnd5e NPCs/characters become 5e stat-block notes;
  items and available spells become 5e item/spell notes. Local portraits and
  journal links are preserved where supported. Tracked HP, scores/modifiers,
  saves, skills, defenses, senses, languages and embedded actions are display
  data, not Foundry automation. Static tiles become native map images. Playlists
  and local OGG song records use current Arkenforge user-content metadata.
- Existing Foundry scenes, geometry, tokens, room markers, linked journals,
  attachments, PDF note pages, naming controls, graded loss reports and the
  add-only installer remain available. Builds do not install automatically.

## Corrections and validation

The campaign recheck confirmed playlist/song listing, Boris's rendered stat
block, and six representative token portraits in Toolkit **0.5.1.18**. MP3 and
OGG experiment timers advanced without visible errors, but no one listening
through these tools confirmed audible output. The all-11 token portrait census
is still incomplete; file inspection confirms all 11 independent icon/Size
records. See [runtime evidence](archive/validation/toolkit-recheck-2026-11-03.md).

Token-to-stat-block links are deliberately omitted: adding a link changed map
portraits into note pins. Actor notes remain separately accessible. Derived AC
and attacks honor explicit source abilities/calculations, languages deduplicate,
and walk speed is first. Boris's source specifies natural AC 10 and INT-based
Claws +1; those are retained rather than guessed from DEX.

Real FG file-level cases and the scoped native geometry check are documented in
[FG phase 2](archive/validation/2026-11-02-FG-NATIVE-PHASE2.md) and
[native export evidence](archive/validation/2026-11-02-FG-ARKENFORGE-EXPORT.md).
Windows/Linux tests and the standalone EXE build/smoke are release gates.
Release-branch Windows full suite: **294 run, 290 passed, four Windows symlink
privilege skips**, including version consistency and GUI version-only exit.
Linux/Windows and executable CI results are reported in the release PR.
File-level success does not imply runtime acceptance of every source feature.

## Known limits

- **Audible MP3/OGG playback has not been confirmed by ear.** UI timer progress
  is the current observation. Production MP3 tracks remain explicit manual
  losses; no encoder is bundled, and ForgeBridge never borrows Toolkit ffmpeg.
  Playlist fades, channels, looping and volume behavior remain manual.
- **Art outside the input package remains manual**, including unavailable actor
  portraits, tile textures and system-compendium references. No replacements are
  invented. Missing media and unresolved spells remain in the loss report.
- **Encrypted/protected Fantasy Grounds modules are refused**, including
  encrypted store/Forge vault content. FG pins, story, NPCs/items and tokens are
  not migrated by the FG map adapter.
- **The Windows EXEs are not code-signed. SmartScreen may warn.** For an unsigned
  download you trust, Windows may offer **More info → Run anyway**. Code signing
  is not included in this release. Extract outside Program Files and MyAssets.
- Foundry actor automation, effects, resources, ownership, token actor deltas,
  fog/vision/exploration and procedural light animation are not translated.
  Animated tiles/video and GIF migration remain manual; labels stay off.
- Light/color/intensity mappings and supported token shapes have bounded
  approximations. Review each conversion report. A successful import does not
  prove complete campaign fidelity.
- Toolkit can automatically rewrite an opened note or played playlist even
  without a Save action. Use `install --uninstall RECEIPT --keep-changed` to
  retain changed files. The installer never overwrites conflicting user content.
- The intermittent Windows LevelDB temporary-file replacement issue on one
  development PC remains an accepted host-specific limitation, not a confirmed
  attribution to a particular process. Clean Windows CI passed; no blind retry
  or suppression was added.

## Upgrade and safe use

Download the complete Windows ZIP, or install the tagged Python source:

```powershell
git fetch origin
git checkout v0.11.0
python -m pip install .
```

Convert into a new output directory, review `conversion-report.json`, and close
Toolkit before any explicit installation. Existing installs and user edits are
not silently replaced. See the [operator guide](USER-GUIDE.md).
