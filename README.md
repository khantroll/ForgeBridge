# ForgeBridge

**Bring maps and adventure content from other virtual tabletops into Arkenforge.**

ForgeBridge is an experimental, local migration tool that translates external VTT content into the closest practical [Arkenforge](https://arkenforge.com/) equivalents. It supports **Foundry Virtual Tabletop** packages and **unencrypted Fantasy Grounds Unity modules**. ForgeBridge's direction is *source VTT → ForgeBridge → Arkenforge*, not a bidirectional exporter.

The current Foundry workflow can build native Arkenforge scene packages directly from supported source data—without requiring an existing Arkenforge map, a manual UVTT import, or per-scene calibration. It preserves available source information and generates explicit reports for anything it cannot convert faithfully.

**Current release:** [v0.11.0](docs/RELEASE-NOTES-v0.11.0.md) · [Windows downloads on GitHub Releases](https://github.com/khantroll/ForgeBridge/releases) · [Operator guide](docs/USER-GUIDE.md) · [Handoff](docs/HANDOFF-2026-11-03.md)

> **Compatibility is limited to tested versions and content.** A successful build is not proof of complete scene or campaign fidelity. Review the conversion report and validate generated maps in Arkenforge before using them in a game.

## Quick start

**Windows, no Python:** [download the Windows ZIP from Releases](https://github.com/khantroll/ForgeBridge/releases),
unzip the whole folder, and double-click **ForgeBridge.exe**.
[Windows app instructions, including unsigned-app SmartScreen](docs/USER-GUIDE.md#easiest-download-the-windows-app).
CLI commands use **forgebridge-cli.exe** in the same folder.

Alternatively, install Git and Python, then open PowerShell:

```powershell
git clone https://github.com/khantroll/ForgeBridge.git
cd ForgeBridge
git checkout v0.11.0
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install .
forgebridge-gui
```

The GUI lets you choose a Foundry package or unencrypted FG module, discover/select maps, build output, and inspect conversion losses. Installation is a separate, reviewed action.

For a command-line conversion:

```powershell
forgebridge convert "C:/Sources/MyModule.zip" --out "C:/Conversions/MyModule-01"
```

Use a **new output directory** for each run; ForgeBridge does not overwrite existing conversion outputs. To develop from a source checkout instead of installing the package, or to use Linux and optional PDF dependencies, follow the [operator guide](docs/USER-GUIDE.md).

## What it converts today

The current Foundry adapter supports bounded conversion of:

| Source content | Arkenforge output |
| --- | --- |
| Scenes, backgrounds, grids | Native maps and background assets |
| Walls and doors | Barriers and doors, including supported open/closed states |
| Ambient lights | Native lights using tested mapping defaults |
| Scene notes and journals | Markers, linked native notes, and supported image attachments |
| Supported static tokens | Native token images, position, size, rotation, and hidden state |
| dnd5e actors, items and available spells | Native 5e stat-block/item/spell display notes and local portraits |
| Adventure roll tables and journal links | Native rollable-table notes and rewritten supported links |
| Playlists and static map tiles | Native playlists/local OGG song records and image tiles |
| PDF handouts | Rendered note pages within existing page/size limits |
| Source assets and references | Retained assets, companion data, and explicit loss reporting |

Each build produces a combined `MyAssets` tree, per-scene packages, and readable conversion reports. UVTT output is also available; **UVTT is an interchange option, not the limit of the native converter**.

The Fantasy Grounds Unity adapter converts backgrounds, grids, walls, doors/windows and lights to native maps. Stored grids win; missing grids require an explicit size. Encrypted modules are refused; FG pins, story, actors/items and tokens remain manual.

Actor notes contain display statistics, not automation or live token bindings. MP3 tracks, external art, ambient sounds, animated media/GIF setup, procedural light animation and Foundry fog/vision/exploration remain manual or unsupported. Audible MP3/OGG playback is not yet confirmed by ear. Windows executables are unsigned; SmartScreen may warn. See [supported scope and limitations](docs/USER-GUIDE.md#supported--manual--unsupported).

## Safe installation and rollback

**Building does not install anything.** You can inspect the generated `MyAssets` contents and reports before deciding whether to install them.

The optional installer is designed to work with the Arkenforge Toolkit closed. It takes a backup, adds only absent files, rejects conflicts rather than overwriting existing content, and records an uninstall receipt. Modified files are protected during removal; review the receipt and rollback instructions before proceeding.

Read the [installation and recovery guide](docs/USER-GUIDE.md#installation-backups-and-recovery) and [release checklist](docs/SCENE-IMPORT-RELEASE.md) before installing native packages.

## How ForgeBridge is designed

```text
External VTT package (Foundry or unencrypted Fantasy Grounds Unity)
                      |
                      v
               Source adapter
                      |
                      v
          ForgeBridge intermediate representation
                      |
             +--------+---------+
             |                  |
             v                  v
      Native mapping      Compatibility/loss
             |                 analysis
             v                  |
      Arkenforge files <--------+
             |
             v
       Review, optional install, and validation
```

The **intermediate representation (IR)** separates source-specific formats from Arkenforge output. That makes it possible to add another inbound VTT adapter without rebuilding the entire converter around a second proprietary format.

The guiding principles are:

- **Preserve meaning, not only images.** Translate supported scene structure and relationships instead of merely flattening maps.
- **Be deterministic first.** Optional future AI-assisted analysis should never be required for routine conversion.
- **Never execute imported macros or arbitrary source code.**
- **Make losses visible.** Distinguish native, approximate, manual, and unsupported results; retain useful source provenance.
- **Protect existing campaigns and licensed content.** No automatic overwrites, DRM circumvention, or redistribution of commercial assets.

## Compatibility and project status

The v0.11.0 release documents testing with **Foundry v13** and selected **Fantasy Grounds Unity** source content and **Arkenforge Toolkit 0.5.1.18**. Windows and Linux automated coverage exists, alongside scoped Toolkit validation for selected real scenes. Other source versions, systems, and native Toolkit releases need separate verification. An intermittent Windows/LevelDB temporary-file issue was seen on one development PC and never reproduced elsewhere; it is an accepted, documented quirk (see the release notes).

ForgeBridge is **usable within its tested scene-conversion scope**, but it is not a lossless campaign migration tool. FG campaign text/actors/items, additional source systems and behavior/automation translation remain future work.

For implementation evidence, acceptance boundaries, known blockers, and the current milestone, use the [handoff](docs/HANDOFF-2026-11-03.md) and [latest runtime recheck](validation/toolkit-recheck-2026-11-03.md) rather than treating this README as a test log.

## Documentation

- [Operator guide](docs/USER-GUIDE.md) — installation, GUI/CLI use, output review, safe install, and recovery.
- [v0.11.0 release notes](docs/RELEASE-NOTES-v0.11.0.md) — tested release scope and known limitations ([v0.9.0](docs/RELEASE-NOTES-v0.9.0.md); [changelog](CHANGELOG.md)).
- [Handoff](docs/HANDOFF-2026-11-03.md) — release sequence and owners; STATUS and NEXT-STEPS are historical.
- [Acceptance matrix](docs/ACCEPTANCE-MATRIX.md) — evidence and boundaries of validated behavior.
- [Scene profiles](docs/SCENE-PROFILES.md), [batch builds](docs/SCENE-BATCH.md), and [native capture](docs/NATIVE-CAPTURE.md) — advanced workflows.
- [Scene import/release rules](docs/SCENE-IMPORT-RELEASE.md) — review and installation safeguards.

## Rights and safety

Only migrate material you have the rights to use. ForgeBridge does not ship Arkenforge native assets or commercial adventure content, and it is not intended to bypass licensing, DRM, or access restrictions.
