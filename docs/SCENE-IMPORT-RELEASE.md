# Scene conversion and installation

The default pipeline now creates native maps from code-defined Toolkit 0.5.1.18
records. No previous map, UVTT import/export, or manual calibration is needed.
Geometry uses the proved Toolkit convention: 2.56 units per source grid, image
upper-left at (0,0), native y up. No native files or image payloads ship with the
code. Existing pinned profiles remain explicit optional overrides.

## Fresh-checkout walkthrough

From the repository root, using Python 3.13:

```powershell
python -m pip install .
forgebridge convert fixtures/synthetic-module --out converted-example
```

`pip install .` adds the `forgebridge` command and the `forgebridge-gui` window; no `PYTHONPATH` is needed. CI installs the package and runs this on synthetic data without Arkenforge installed. Developers can still use `$env:PYTHONPATH = "$PWD\src"` with `python -m forgebridge`. Replace
the fixture with your module/world/Adventure directory or ZIP. Choose a new output
folder under an existing parent. Use `--list-scenes`, repeat `--scene ID`, or use
`--scene-key KEY` for exact selection when IDs repeat across Adventures.

Each supported scene produces UVTT, a schema-built background/map/thumbnail and
existing-writer notes, room markers, media and supported tokens. Padding/grid
normalization remains in the source adapter; source pixels are not native units.

```text
converted-example/
  MyAssets/                    ready-to-copy native content; no reports
  scene-001/uvtt-package.zip    geometry IR, original companion, loose originals
  scene-001/native-package.zip coherent scene plus dependencies
  conversion-report.json       combined source/native outcomes and losses
```

Only final scene maps are published; generated helper maps/notes are removed and
native references checked. Zero-token/journal-free scenes work. Missing note
positions or targets remain explicit unplaced-marker entries. Unsupported tokens,
media and light ranges remain reported with source retained. Source/UVTT grades
are preserved separately from `native_counts`, `native_losses` and per-scene
`native_report`; don't mistake UVTT-only losses for final native support.
Lights retain the proved Toolkit import defaults, not independent Foundry color,
intensity or procedural-animation equivalence. Labels stay off.

BUILT means files generated, not observed in Toolkit. PARTIAL exits 1 and lists
rejections; invalid requests exit 2. Existing, linked or source-contained output
is refused. Input hashes are rechecked; the completion report is published last.
A missing report means incomplete publication. No imported scripts execute.

## Review and optional advanced profiles

```powershell
forgebridge convert "C:/Sources/MyModule.zip" --out "C:/Conversions/MyModule-01"
forgebridge install_review --package "C:/Conversions/MyModule-01/scene-001/native-package.zip" --snapshot-root "C:/Backups/MyAssets" --static-snapshot
```

The review uses a static copy prepared with Toolkit closed and writes nothing.
Repeat `--profile PROFILE.json` with convert only when deliberately choosing its
pinned source/calibration/export over automatic synthesis. Original profile,
portable capture and scene_batch commands remain available; do not edit hashes
merely to clear a mismatch. See SCENE-PROFILES.md and NATIVE-CAPTURE.md.

## Add-only installation and rollback

Build and review first, then install explicitly:

```powershell
forgebridge install --package "C:/Conversions/MyModule-01/scene-001/native-package.zip" --myassets "C:/ArkenforgeData/MyAssets" --backup-root "D:/ForgeBridgeBackups"
```

Or intentionally authorize build plus installation in one invocation:

```powershell
forgebridge convert "C:/Sources/MyModule.zip" --out "C:/Conversions/MyModule-02" --install --myassets "C:/ArkenforgeData/MyAssets" --backup-root "D:/ForgeBridgeBackups"
```

`--install` is an explicit write request, not a preview or interactive prompt.
Both destination flags are required. Without `--out`, a unique output directory
is created under the working directory and printed. installation-report.json
records installation; conversion-report.json remains the pre-install build.
The GUI provides a separate review/confirm native installation button.

Toolkit must stay closed. Inspection failure, conflicts, aliases and links refuse
installation. The complete MyAssets backup is made first; only absent files are
created, identical files untouched. Inputs/destination must stay static. A lock
prevents concurrent ForgeBridge installs, not writes by unrelated programs.
Backup limit: 16 GiB/100,000 entries. Combined installation-review limit:
1 GiB/16384 native files. Select fewer scenes if needed; never bypass checks.
Reports and original PDFs stay outside installed MyAssets.

```powershell
forgebridge install --uninstall "D:/ForgeBridgeBackups/forgebridge-RUN_ID/uninstall.json"
```

Check later references to imported content first. Uninstall removes only recorded
unchanged additions; edited/missing additions block removal. Existing files,
later user content, directories and backups stay. INCOMPLETE receipts need manual
review. Restore backups only after preserving later edits; never Replace All.

## Limits and release gates

GIF/FPS setup, native manual fog, Foundry fog/vision, procedural animations and
actor/stat/combat/behavior fidelity remain manual/unsupported. Default geometry
no longer requires native import/export/calibration. New combined schema outputs
and thumbnails still need Claude's Toolkit checks; file generation is not native
or player acceptance. No desktop work occurs in this implementation.

Review, current CI/skip evidence, host LevelDB exception decision, native and
fresh-operator acceptance and explicit merge/tag authorization remain gates.
See USER-GUIDE.md and ACCEPTANCE-MATRIX.md. No merge or release tag here.
The existing scripts/rehearse_scene_import.py synthetic profile rehearsal remains
available alongside the new public convert CI walkthrough.
