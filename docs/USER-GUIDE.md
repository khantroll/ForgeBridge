# ForgeBridge operator guide

ForgeBridge converts Foundry source data into reviewable Arkenforge scene outputs.
Keep the original Foundry package and your existing Arkenforge content unchanged.
Automatic native map synthesis is being validated separately in A0. Until that
backend is accepted, scenes without a matching calibrated profile are **UVTT
intermediates**, requiring Toolkit import and the native export/calibration step.
Do not copy UVTT/source ZIPs into MyAssets or treat them as native scene packages.

## Prerequisites and tested scope

- Use Python **3.13** (the Windows/Linux CI target); Python 3.14.2 is also used in
  local Windows tests. Python 3.12+ is required by path/junction checks, but 3.12
  is not the current CI promise.
- Tested native reference version: **Arkenforge Toolkit 0.5.1.18**, launcher
  7.0.0.3. This is not a compatibility promise for other Toolkit versions.
- Tested real source corpus: **Foundry v13 Count's Manor data**, plus synthetic
  module/world/Adventure fixtures. A synthetic manifest's compatibility range
  does not establish support for every Foundry version or game system.
- Supported source storage: JSON/JSONL/NeDB text and bounded read-only LevelDB
  snapshots; modules/worlds and embedded Adventure scenes in folders or ZIPs.
- Install dependencies in a virtual environment from a complete checkout. Optional
  PDF page images require requirements-pdf.txt; without it PDFs remain references.
- Use only assets you have rights to migrate. Do not execute imported macros,
  scripts or active HTML; ForgeBridge does not require them.

## Fresh checkout and one command

In PowerShell, from the folder where you want the checkout:

```powershell
git clone https://github.com/khantroll/ForgeBridge.git
cd ForgeBridge
git switch cursor/dynamic-lighting-c6b0
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt -r requirements-native-capture.txt
$env:PYTHONPATH = "$PWD\src"
python -m forgebridge convert fixtures/synthetic-module --out converted-example
```

If activation is blocked by local policy, use `.venv/Scripts/python.exe` directly;
do not change global execution/security settings. On Linux use
`python3 -m venv .venv`, `source .venv/bin/activate` and `export PYTHONPATH="$PWD/src"`.
The synthetic command above is also executed in CI; it uses no commercial assets.

For your source, choose a **new** output folder under an existing parent:

```powershell
python -m forgebridge convert "C:/Sources/My Foundry Module.zip" --list-scenes
python -m forgebridge convert "C:/Sources/My Foundry Module.zip" --out "C:/Conversions/MyModule-01"
```

Repeat `--scene ID` to select scenes. Review the scene's source pack/Adventure in
the discovery report: same IDs can occur in different Adventures. Without a more
specific selection, all matching scenes are kept separately rather than silently
merged. Existing outputs are refused, not refreshed or replaced.

With a previously prepared, hash-pinned calibrated profile, use its original
unpacked source directory and repeat `--profile` for each matching scene:

```powershell
python -m forgebridge convert "C:/Sources/MyModule" --profile profiles/my-scene.json --out "C:/Conversions/MyModule-native-01"
```

The [scene-profile guide](SCENE-PROFILES.md) explains native control capture and
calibration. Do not use another scene's geometry or edit hashes just to clear a
warning. A0 is responsible for replacing these manual native setup steps, once
actual record semantics and calibration are established in Toolkit.

## Review the outputs

Open `conversion-report.json` in the new output folder first. It combines every
scene's source identity and graded loss report, native conversion report where
available, manual requirements and explicit errors. `MANUAL` means a UVTT
intermediate was built; `BUILT` means a native package was built, **not** that it
was observed in Toolkit. `REJECTED` names the error; overall PARTIAL exits 1.
Invalid inputs/output requests exit 2. PASS exits 0 but can still include manual
and unsupported features. Graded counts include package inventory as well as
selected-scene features; they are not a percentage of campaign fidelity.

Each scene folder contains a UVTT ZIP; matched profiles add a native ZIP. Unpack
an intermediate outside Arkenforge and import `scene.uvtt` in Toolkit. The scene
companion retains original source fields, journals and loss grades; the notes
file is a readable GM reference. `source-assets/` holds supported loose originals.
These are not native notes or automatic token migration.

A missing top-level completion report means publication did not finish. Preserve
that incomplete folder for inspection and choose a fresh output after addressing
the error. Never install partial archives or replace a previous output folder.

## Supported and retained/manual features

| Feature | Current scope |
| --- | --- |
| UVTT geometry | Background, supported square grids, normalized source padding/origin, walls/portals and lights; restrictions and approximations are reported. Fractional grids refuse misaligned integer UVTT resolution. |
| Native scene package with matching profile | Preserved calibrated geometry plus room markers, linked notes/tables, supported image attachments and bounded tokens in one map. |
| Tokens | Supported square/static textures, identity, position, Size/footprint, bounded texture scale, rotation and hidden state; unsupported fields/rejections are explicit. |
| Journals/tables | Retained provenance and resolved links; supported simple tables become rollable fields. Missing source tables/media remain missing, never invented. |
| Media | Supported static images; optional rendered PDF pages. Loose audio collection is not automatic scene-music behavior. |
| GIF/animation | GIF import and FPS setup remain manual. Procedural torch/ghost light animation is not animated media and is not mapped. |
| Fog/vision | Foundry fog, token vision and detection modes are not converted. Native manual fog is a separate capability; imported maps can start fully covered. |
| Actors/stats/behaviors | Original data retained/reported, no complete actor/stat/combat or automation conversion. No imported script execution. |
| Labels | Off. Do not infer player-facing behavior from GM view or hidden flags. |

## Backup, add-only install and rollback

Install only a reviewed **native-package.zip**. Close Toolkit normally, wait for
the launcher to stop saying "Running Arkenforge Toolkit", and keep it closed.
Do not elevate Toolkit, launcher or desktop helper. Have enough free space for a
complete MyAssets backup plus additions. The installer never starts Toolkit.

```powershell
python -m forgebridge install --package "C:/Conversions/MyModule-native-01/scene-001/native-package.zip" --myassets "C:/ArkenforgeData/MyAssets" --backup-root "D:/ForgeBridgeBackups"
```

The backup root must already exist and be outside the MyAssets tree. Review the
printed destination carefully. The installer refuses a running/undetectable
Toolkit, conflicts, unsafe paths and existing locks; backs up the whole content
(up to 16 GiB/100,000 entries); checks it stayed unchanged; and adds absent files
only. Identical files stay untouched. It writes an uninstall receipt in a unique
backup folder. No real installation is performed by the build command. The
current `convert --install` integration is withheld until A0 is accepted.

Before uninstalling, check that no later maps/notes rely on an imported file.
Preserve later edits. The receipt removes only recorded unchanged additions:

```powershell
python -m forgebridge install --uninstall "D:/ForgeBridgeBackups/forgebridge-RUN_ID/uninstall.json"
```

Any changed/missing addition blocks removal. Existing files, later user content,
folders and backups are retained. INCOMPLETE receipts require manual review.
Full backup restoration is a deliberate operator action: close Toolkit and copy
only reviewed affected content after preserving later edits elsewhere. Do not
blindly replace MyAssets or delete files from an old import manifest.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| Existing output / conflict | Choose a new output directory; inspect conflict paths. Back up user edits. Never overwrite to clear the error. |
| Hash or calibration mismatch | Restore the original pinned input or regenerate source companion and deliberately review/capture the correct calibration. Do not simply replace a hash. |
| ICE-candidate exception / unstable Toolkit | Stop player projection and close the unstable Toolkit normally without discarding needed user work. Use Claude's built-in browser at http://127.0.0.1/ for the accepted player workflow; keep Waterfox/Chrome player tabs closed. Browser pattern is observed, not a proven root cause. No converter fix is implied. |
| Toolkit relaunch does not work | Wait until the launcher no longer reports Toolkit running before Launch. Do not start duplicate or elevated instances. |
| Player picture black with fog text | Native fog starts covered. Inspect projection framing and native reveal controls using a disposable copy; turning fog off is different from bounded reveal/persistence. Never change original profile maps for an experiment. |
| Windows LevelDB .dbtmp replacement error | Preserve the error/output and stop that operation. Host intermittency remains unresolved despite clean CI. No blind retries, trace/probe expansion or automatic Defender/indexer exclusions. Jeffrey owns the release exception decision. |
| Install lock exists | Check for an active ForgeBridge install. Do not delete an unfamiliar lock automatically. Review interrupted run/backup/receipt first. |
| Process inspection or backup fails | Installation refuses before adding files. Resolve the reported cause and choose/review a safe backup location. Never bypass the Toolkit-closed guard. |
| Optional PDF renderer absent | Install requirements-pdf.txt only if page rendering is wanted. Otherwise retain original PDF references/manual handling. CI skips are not renderer acceptance. |

For commands and detailed review/rollback rules see
[SCENE-IMPORT-RELEASE.md](SCENE-IMPORT-RELEASE.md). Native results/gates belong to
[ACCEPTANCE-MATRIX.md](ACCEPTANCE-MATRIX.md); this guide adds no runtime evidence.
