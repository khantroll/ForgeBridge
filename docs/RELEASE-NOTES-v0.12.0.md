# ForgeBridge v0.12.0 — music, spell links and Fantasy Grounds campaign notes

Release date: 2026-11-05. Builds on [v0.11.0](RELEASE-NOTES-v0.11.0.md).
Download **ForgeBridge-0.12.0-windows-x64.zip** from
[GitHub Releases](https://github.com/khantroll/ForgeBridge/releases/tag/v0.12.0).
Unzip outside Program Files and MyAssets, then run **ForgeBridge.exe**.
Keep **forgebridge-cli.exe** and `_internal` beside it. No Python installation is needed.

## Included and checked in Toolkit

- Local **MP3 and OGG Vorbis** music is embedded unchanged, preserving its codec
  and extension. Playlist entries initialize Master at 80%; no encoder or Toolkit
  ffmpeg is required. Encoded local paths such as `Crypt%20and%20Lair.mp3` resolve
  safely. The maintainer heard Ambient's Manor, Crypt And Lair and Forest separately.
- Optional **dnd5e spell-pack** input resolves exact external spell UUIDs to 5e
  Spell notes and rewrites source links. Use the unzipped dnd5e system folder or
  `packs/spells`; the complete system ZIP can exceed the read budget. All three
  Count's Manor scroll links opened Bless, Spiritual Weapon and Protection from
  Poison in the final Toolkit check.
- **Fantasy Grounds 5e NPC/item/spell/story notes** use native stat/item/spell
  fields and story text/images. The campaign command writes a native ZIP and
  supports explicit add-only installation with full backup and uninstall receipt.
  Claude checked the synthetic NPC portrait/stat block, item, spell and story
  image/link in Toolkit. This is separate from the existing FG map adapter.
- **Rename-after-build guard:** the GUI requires rebuilding before install when
  edited map names no longer match generated files. Map names must be unique
  across the entire MyAssets library, including different folders.

Runtime evidence: [Claude + the maintainer, 2026-11-05](archive/validation/2026-11-05-FINAL-TOOLKIT-CHECK.md),
Toolkit **0.5.1.18** on Windows. That check did not repeat the unchanged map/token
writer or inspect the expanded mixer value. Earlier native MP3/OGG control
listening and byte preservation are recorded in the music fixtures/evidence.

## Display corrections — file-level validation only

These four corrections have synthetic regression tests and decoded native-record
checks; **no new Toolkit runtime validation is claimed for them**:

- Foundry `&Reference[poisoned apply=false]` becomes **poisoned**. Other @/&
  enrichers use inert explicit/positional labels; UUID markup stays available to
  the native link resolver. Source commands and scripts are never executed.
- Scroll-to-spell and other links inside 5e parchment blocks use a readable dark
  brown while retaining their link targets and underline styling.
- Empty Skills, Senses and Languages fields omit their labels. Supported
  `*FieldActive` flags remain respected; members absent from the captured schema
  are not invented. Proficiency is derived when supported CR/level data exists,
  otherwise its line is omitted instead of displaying Unknown.
- Level-zero spells display **Evocation cantrip**, for example, instead of
  **0-level evocation**, for both Foundry and Fantasy Grounds inputs.

## Limits and safe upgrades

- Stats are display data, not actor automation. Foundry effects, resources,
  ownership, token actor deltas, vision/fog/exploration and procedural animations
  remain conversion gaps. Labels remain off.
- Missing art outside the supplied package remains manual; no replacement is
  invented. Unresolved links and unsupported media remain graded losses.
- Playlist source volume, fades, channels, looping/mode and playback state need
  manual review. New packages still need representative listening checks.
- Encrypted/protected Fantasy Grounds store/Forge modules are refused. FG pins
  and tokens remain manual; campaign notes do not imply full rules automation.
- Animated/video media and map-attached ambience have native control evidence,
  but automatic conversion is not included here. Bounded fog and profile player
  checks retain their separately documented pending status.
- **Windows apps are unsigned. SmartScreen may warn.** For a trusted download,
  Windows may offer More info → Run anyway. Code signing is not included.
- Build to a new output folder and review the loss/conflict reports. Close
  Toolkit before explicit install/uninstall. Never overwrite user content;
  `install --uninstall RECEIPT --keep-changed` preserves edits. Toolkit may rewrite
  notes/playlists even without a Save action. Receipts and backups remain usable.
- The accepted host-specific Windows LevelDB replacement limitation remains;
  no blind retries or error suppression were introduced.

Local Windows full suite: **325 run, 321 passed, four Windows symlink privilege
skips**. Six new display regressions pass. Linux/Windows full tests and Windows
executable build/smoke are release gates.
See the release PR for totals and CI results. The tag workflow attaches the ZIP,
which is checked from a clean extraction before reporting release completion.
