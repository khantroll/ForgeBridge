# ForgeBridge

**Bring maps and adventure content from other virtual tabletops into Arkenforge.**

ForgeBridge is an experimental, local migration tool that translates external VTT content into the closest practical [Arkenforge](https://arkenforge.com/) equivalents. It supports **Foundry Virtual Tabletop** packages and **unencrypted Fantasy Grounds Unity modules**. ForgeBridge's direction is *source VTT → ForgeBridge → Arkenforge*, not a bidirectional exporter.

The current Foundry workflow can build native Arkenforge scene packages directly from supported source data—without requiring an existing Arkenforge map, a manual UVTT import, or per-scene calibration. It preserves available source information and generates explicit reports for anything it cannot convert faithfully.

**Latest documented release:** [v0.13.0](docs/RELEASE-NOTES-v0.13.0.md) · [Windows downloads on GitHub Releases](https://github.com/khantroll/ForgeBridge/releases) · [Operator guide](docs/USER-GUIDE.md)

> **Supported source scope: Foundry v13 / dnd5e and unencrypted Fantasy Grounds Unity modules.**

**Compatibility is limited to the versions and content described below.** A successful build is not proof of complete scene or campaign fidelity. Review the conversion report and validate generated maps in Arkenforge before using them in a game.

## Quick start

**Windows, no Python:** [download the Windows ZIP from Releases](https://github.com/khantroll/ForgeBridge/releases),
unzip the whole folder, and double-click **ForgeBridge.exe**.
[Windows app instructions, including unsigned-app SmartScreen](docs/USER-GUIDE.md#easiest-download-the-windows-app).
CLI commands use **forgebridge-cli.exe** in the same folder.

Alternatively, install Git and Python, then open PowerShell:

```powershell
git clone https://github.com/khantroll/ForgeBridge.git
cd ForgeBridge
git checkout v0.13.0
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

Fantasy Grounds Unity modules now use one build for supported maps and campaign
notes, including NPC/item/spell/story notes, tables/manuals/handouts, note-opening
pins and portrait tokens. Missing grids need an explicit size; encrypted modules
are refused. NPC links on tokens remain omitted to preserve portraits.

Supported Foundry animated/video tiles and map-attached ambience have earlier
Toolkit observations. Optional Data-folder art and fog/vision/light-effect mapping
are file-level only. Unsupported animations, source darkness, historical fog and
full actor/combat behavior remain reported limits. MP3/OGG playlists preserve
available bytes; source playback settings need review. Windows EXEs are unsigned.
See [the release evidence split](docs/RELEASE-NOTES-v0.13.0.md) and
[supported scope](docs/USER-GUIDE.md#supported--manual--unsupported).

## Resolving linked dnd5e spells

Foundry adventures often store only a *link* to a spell, such as a scroll of
Bless, and not the spell itself. The spell lives in Foundry's free **dnd5e game
system**. To turn those links into real spell notes, download the newest
non-pre-release `dnd5e-release-<version>.zip` (about 108 MB) from the
[dnd5e releases page](https://github.com/foundryvtt/dnd5e/releases), unzip it,
and choose that folder in the app's **Optional dnd5e system folder** field. On
the command line, use `--dnd5e-system "C:\Foundry\dnd5e"`. You don't need
Foundry installed or licensed. If you skip this, everything else still
converts, and those spells are listed in the loss report.
[Step-by-step guide](docs/USER-GUIDE.md#spells-that-need-the-free-dnd5e-system-download).

## Safe installation and rollback

**Building does not install anything.** You can inspect the generated `MyAssets` contents and reports before deciding whether to install them.

The optional installer is designed to work with the Arkenforge Toolkit closed. It takes a backup, adds only absent files, rejects conflicts rather than overwriting existing content, and records an uninstall receipt. Modified files are protected during removal; review the receipt and rollback instructions before proceeding.

Read the [installation and recovery guide](docs/USER-GUIDE.md#installation-backups-and-recovery) and [release checklist](docs/SCENE-IMPORT-RELEASE.md) before installing native packages.

## Architecture

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

Design principles:

- **Preserve meaning, not only images.** Translate supported scene structure and relationships instead of merely flattening maps.
- **Be deterministic first.** Optional future AI-assisted analysis should never be required for routine conversion.
- **Never execute imported macros or arbitrary source code.**
- **Make losses visible.** Distinguish native, approximate, manual, and unsupported results; retain useful source provenance.
- **Protect existing campaigns and licensed content.** No automatic overwrites, DRM circumvention, or redistribution of commercial assets.

## Compatibility and project status

The [v0.13.0 release notes](docs/RELEASE-NOTES-v0.13.0.md) distinguish earlier
**Windows / Toolkit 0.5.1.18** observations from new file-level-only work. Supported
source scope is **Foundry v13 / dnd5e** and unencrypted **Fantasy Grounds Unity**
modules. The trial has ended; this release has no new Toolkit runtime acceptance.
Windows/Linux tests and frozen-EXE checks do not replace it.

FG campaign notes, tables, manuals, handouts, pins and portrait tokens now share
the combined conversion path. Full actor/combat behavior, additional systems,
source-compendium monsters/items, environment fidelity and some playback/roll
settings remain gaps. ForgeBridge is not a lossless campaign migration tool.

Detailed compatibility evidence is maintained in the [acceptance matrix](docs/ACCEPTANCE-MATRIX.md) and [release notes](docs/RELEASE-NOTES-v0.13.0.md).

## Documentation

- [Operator guide](docs/USER-GUIDE.md) — installation, GUI/CLI use, output review, safe install, and recovery.
- [v0.13.0 release notes](docs/RELEASE-NOTES-v0.13.0.md) — tested release scope and known limitations ([v0.9.0](docs/RELEASE-NOTES-v0.9.0.md); [changelog](CHANGELOG.md)).
- [Acceptance matrix](docs/ACCEPTANCE-MATRIX.md) — evidence and boundaries of validated behavior.
- [Scene profiles](docs/SCENE-PROFILES.md), [batch builds](docs/SCENE-BATCH.md), and [native capture](docs/NATIVE-CAPTURE.md) — advanced workflows.
- [Scene import/release rules](docs/SCENE-IMPORT-RELEASE.md) — review and installation safeguards.

## Rights and safety

Only migrate material you have the rights to use. ForgeBridge does not ship Arkenforge native assets or commercial adventure content, and it is not intended to bypass licensing, DRM, or access restrictions.
