# ForgeBridge operator guide

ForgeBridge discovers scenes in a Foundry package and builds native Arkenforge
output with code-defined records. The default path needs no manual UVTT import,
map export or calibration and no pre-existing imported map. Existing calibrated
profiles remain optional advanced overrides. Every output still needs its own
Toolkit check; this tool does not claim lossless campaign/behavior conversion.

## Setup and tested scope

- Python 3.13 is the Windows/Linux CI target; local Windows also tests 3.14.2.
  Path checks require Python 3.12+, but 3.12 is not the CI promise.
- Native protocol reference: Toolkit 0.5.1.18 / launcher 7.0.0.3. Other versions
  need validation. Real source corpus: Foundry v13 Count's Manor, plus synthetic
  module/world/Adventure fixtures; not every Foundry version or system.
- Use only source assets you may migrate. Imported JS/macros/active HTML never run.
- Folder and ZIP input support JSON/JSONL/NeDB and read-only LevelDB snapshots.

From a complete checkout in PowerShell:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt -r requirements-native-capture.txt
$env:PYTHONPATH = "$PWD\src"
python -m forgebridge convert fixtures/synthetic-module --out converted-example
```

If activation is blocked, use .venv/Scripts/python.exe directly; don't change
global security settings. On Linux use python3, source .venv/bin/activate and
export PYTHONPATH="$PWD/src". Optional requirements-pdf.txt enables PDF pages;
otherwise PDFs remain retained/manual references. CI runs the synthetic command.

## Graphical workflow

After setup, double-click forgebridge_gui.pyw on Windows (it prefers .venv's
Pythonw), or run `python -m forgebridge gui`. Tkinter must be installed. No web
server or browser is needed.

1. Choose the Foundry folder/ZIP and click Discover scenes.
2. Select scenes (Ctrl-click for multiple). Pack/Adventure scope remains separate
   even if scene IDs match.
3. Choose an output parent; the app proposes a new child folder. Profiles are
   optional overrides; default output uses schema-built native synthesis.
4. Build/export and read the source-stage and native-stage loss summary.
5. Review before using Install reviewed native outputs. Select actual MyAssets
   and a separate existing backup folder; keep Toolkit closed and confirm the
   displayed destination/backup summary. Rejected/UVTT-only results cannot install.

Wait for file work to finish before closing. The GUI has headless controller
coverage, but was not launched/visually validated by Codex in this session.

## Command-line conversion and output

```powershell
python -m forgebridge convert "C:/Sources/MyModule.zip" --list-scenes
python -m forgebridge convert "C:/Sources/MyModule.zip" --out "C:/Conversions/MyModule-01"
```

Repeat --scene ID or select exact --scene-key KEY from discovery. Default native
calibration is 2.56 units/grid, upper-left origin, native y up; source padding and
grid are normalized before synthesis. No source pixel/native coordinate shortcut.
Choose new output; existing paths are never refreshed or overwritten.

Open conversion-report.json first: source/UVTT grades are retained separately
from native_counts/native_losses and each native_report. BUILT is not runtime
PASS. PARTIAL/exit 1 lists rejected scenes; invalid requests exit 2. Supported
features can coexist with explicit token/media/link gaps. No replacements for
unresolved source tables/media are invented. Counts are not a fidelity percentage.

MyAssets/ is the combined ready-to-copy native tree. Each scene also has a native
ZIP, UVTT ZIP, original companion and readable notes. Reports/original PDFs stay
outside MyAssets. Missing completion report means incomplete publication: preserve
it for inspection and choose a fresh destination after fixing the cause.

## Supported / manual / unsupported

| Feature | Scope |
| --- | --- |
| Geometry/background | Direct native maps, barriers, doors, lights, background assets and browser previews from known schemas; no native files shipped. |
| Notes and tokens | Existing journal/table/image/marker/token writers; supported square/static tokens preserve identity, position, footprint, scale, rotation and hidden state. |
| Non-success | Invalid marker positions/targets, unsupported token geometry/scales, source/media gaps and unsupported light ranges remain explicit. |
| Light fidelity | Uses observed Toolkit UVTT-import color/intensity defaults; independent Foundry color/intensity/animation mapping not claimed. |
| Audio and GIF | Loose audio is not automatic scene music; GIF import/FPS remains manual. Procedural light animation is separate. |
| Fog/vision | Fresh native manual fog starts covered. Foundry exploration, vision/detection and token vision aren't converted. |
| Actors/behaviors | Source retained/reported; full actors/stats/combat/automation remain gaps. No script execution. |
| Labels | Off. Player behavior cannot be inferred from GM view. |

Advanced profile/capture/batch workflows remain in SCENE-PROFILES.md,
NATIVE-CAPTURE.md and SCENE-BATCH.md. Don't repin hashes just to clear errors.

## Installation, backups and recovery

Toolkit must stay closed; wait for the launcher to stop saying Running Arkenforge
Toolkit before relaunching. Keep Toolkit/launcher/helper non-elevated.

```powershell
python -m forgebridge convert "C:/Sources/MyModule.zip" --out "C:/Conversions/MyModule-02" --install --myassets "C:/ArkenforgeData/MyAssets" --backup-root "D:/ForgeBridgeBackups"
```

This deliberately authorizes add-only installation after build/conflict checks;
it does not pause for review. Prefer build-only plus the explicit install command
in SCENE-IMPORT-RELEASE.md when you want to review first. A full MyAssets backup
comes before copying; conflicts/running Toolkit/inspection failure refuse writes.
Only absent files are added; identical files untouched. Backups are separate,
existing folders. No permission/security changes or automatic elevation.

The backup run holds hashes and an uninstall receipt. Review later references
and preserve later edits before:

```powershell
python -m forgebridge install --uninstall "D:/ForgeBridgeBackups/forgebridge-RUN_ID/uninstall.json"
```

Only recorded unchanged additions are removed. Edited/missing additions block
removal; existing content, later user files, directories and backups remain.

Opening a converted note in the Toolkit can rewrite its file, so after real use a
plain uninstall may refuse with "Added file changed/missing". To remove
everything that is still exactly as installed and keep the changed files (they
are listed, and recorded in the receipt), add `--keep-changed`:

```powershell
forgebridge install --uninstall "D:/ForgeBridgeBackups/forgebridge-RUN_ID/uninstall.json" --keep-changed
```

Delete the listed kept files yourself afterwards if you do not want them.
INCOMPLETE receipts require manual review. Restore only reviewed affected backup
files with Toolkit closed; never Replace All or blind folder synchronization.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| Conflict/existing output | Select a new output; preserve/review user edits. Never overwrite to clear it. |
| Hash mismatch with advanced profile | Restore pinned inputs or deliberately recapture the correct profile; no blind repinning. |
| ICE/unstable Toolkit | Stop projection, close normally, use Claude's built-in browser at http://127.0.0.1/ with Waterfox/Chrome player tabs closed. This is an observed browser/session pattern, not a proved cause or converter defect. |
| Relaunch fails | Wait until the launcher no longer reports Toolkit running; no duplicate/elevated instances. |
| Black player view with fog text | Check native fog and framing on a disposable copy; fog-off and bounded reveal/persistence are distinct checks. Preserve original profile maps. |
| Windows LevelDB .dbtmp error | Retain diagnostics and stop that operation. Host intermittency remains unresolved despite clean CI; no blind retries, new probes or automatic Defender/indexer exclusions. Jeffrey owns exception decisions. |
| Lock/backup failure | Inspect the active/interrupted install and retained receipt; don't remove unfamiliar locks or bypass the closed-Toolkit guard. |
| Size limit | Export/select fewer scenes. Backup: 16 GiB/100k entries; combined review: 1 GiB/16384 native files; conversion tree: 1 GiB/16384 files. |
| PDF renderer absent | Keep PDFs manual, or install optional PDF requirements. Skips are not renderer acceptance. |

Runtime checks belong to Claude; see ACCEPTANCE-MATRIX.md and his direct-map
note. This guide adds no Toolkit observations or M1 acceptance claims.
