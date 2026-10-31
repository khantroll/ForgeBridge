# Scene-import operator and release checklist

This is a calibrated scene-import workflow, not lossless campaign conversion.
Use [the roadmap](ROADMAP.md) for priorities and [STATUS](../STATUS.md) for evidence.
No release is tagged or PR merged by these instructions.

## Prerequisites and input preparation

1. Back up the source package and your Arkenforge MyAssets/campaign data. Keep
   originals separate from working inputs. Use only assets you may migrate.
2. Install Python and `requirements.txt` in your chosen environment. CI currently
   covers Python 3.13 on Linux/Windows; local Windows evidence also uses Python 3.14.
   Native acceptance evidence is Toolkit 0.5.1.18, not a promise for every version.
3. Generate the selected scene's UVTT and preservation companion with the existing
   [README commands](../README.md). Review missing media, unsupported fields and
   identity/Adventure selection before continuing. Imported scripts never run.
4. Import that UVTT into a separately named Toolkit map. Save/export it and measure
   its origin and native units per source grid. Export reusable native marker,
   media and token controls separately. Do not borrow another scene's geometry or
   calibration. Native Size calibration is independent of sprite transforms.
5. Author and pin a [scene profile](SCENE-PROFILES.md), including measurement
   evidence. A profile requires the unpacked source directory. The repository's
   private Manor/Crypt fixtures are examples, not redistributable prerequisites.

## Audit, build and review

From the repository root, with a pinned profile and a new output filename:

```powershell
$env:PYTHONPATH = "$PWD\src"
py -m forgebridge.native_capture --export inputs/scene-native.zip --map "MyAssets/Maps/My Scene.rwmap" --audit
py -m forgebridge.package --profile profiles/my-scene.json --preflight
py -m forgebridge.package --profile profiles/my-scene.json --out builds/my-scene-v1.zip
Get-FileHash -Algorithm SHA256 builds/my-scene-v1.zip
```

Audit/preflight read inputs; they do not install, infer calibration or certify
runtime behavior. Stop on a failed command. Review audit conflicts/missing paths,
conversion-report.json, token-report.json when present, profile-provenance.json,
INSTALL.txt and retained source data inside the result. Reconcile converted,
rejected, approximate and manual content. PDF page rendering is a build step;
preflight alone cannot establish readability. Labels remain off.

If an input hash changed, restore the pinned input or regenerate the companion
and review/recalibrate that scene before explicitly pinning a new profile. Never
edit hashes just to clear the warning. Use a new output map name/note namespace
for an intentional parallel import, rather than replacing manually edited notes.

## Reviewed installation and rollback

For a repeatable read-only comparison, prepare a **static copy** of the destination
MyAssets with Toolkit closed, then run:

```powershell
py -m forgebridge.install_review --package builds/my-scene-v1.zip --snapshot-root snapshots/MyAssets --static-snapshot
```

Repeat `--package` to review multiple packages together. Exit 0 means no conflicts
were observed; exit 1 reports conflicting/blocked target paths; exit 2 rejects
invalid inputs or a changing snapshot. JSON includes input/member hashes, new and
identical files, conflicting user edits, blocked aliases/links and supplemental
files that must stay outside MyAssets. Nothing is written by the review command.
It checks package metadata references, not native runtime behavior. The flag is
your assertion that the copy is static; the tool cannot establish its origin.
The report is a point-in-time comparison, not authorization to install later:
recheck the actual destination with Toolkit closed before copying anything.

1. Close Toolkit normally. Extract the ZIP into a staging folder outside its data
   directory. Keep reports and source attachments outside the installed MyAssets.
2. Compare every staged MyAssets relative path against the actual MyAssets root:
   absent = eligible to add; byte-identical = leave existing file untouched;
   different bytes or case aliases = STOP. Do not use Replace All or blind folder
   synchronization. Inspect shared preserved native controls/backlinks too.
3. Record the ZIP hash, backup location and each added relative path/hash. Add
   only reviewed absent files. The build/audit commands do none of this for you.
4. Open the separately named output map. Verify its image/grid, opaque walls and
   doors, representative lights, supported token placement/Size/rotation/visibility,
   note links and attachments. Save, switch away/reopen, then restart Toolkit and
   check representative content in actual player output. Record Toolkit version,
   map/package identities, observed results and any manual changes.
5. To roll back, close Toolkit and review the installation record. A file added by
   this import may have acquired later user edits or references: do not delete or
   replace it merely because its path appears in the record. Restore only reviewed
   affected data from backup; preserve subsequent edits separately. No automated
   uninstall/rollback is supplied or claimed.

## Current acceptance and limits

| Area | Evidence / release treatment |
|---|---|
| Manor/Crypt GM token/link persistence | Accepted October 18 runtime samples |
| Profile actual-player tokens/restart | Accepted October 31 observations; no map save in that pass |
| Geometry/blocking/lights, PDF/GIF | Prior scoped runtime passes retained; repeat only for relevant changes |
| Bounded native fog reveal/hide/restart | DEFERRED; explicitly excluded from current acceptance |
| Foundry fog/vision | Manual loss-report guidance; no automatic vision/fog migration |
| Native import/export/calibration, installation | Manual reviewed steps above |
| GIF migration and FPS setup | Manual; procedural light animation is a separate unmapped capability |
| Actor/stat/combat/behavior | Retained/unmapped; no imported macro execution |
| Windows LevelDB intermittent replacement | Historical unresolved host failure; clean CI/local runs do not establish root cause |

Player streaming may require per-session 1280×720/15 selection; Toolkit's dialog
has reset to 1920×1080/30. Keep Toolkit at 30 FPS and only one player stream active.
Black output with native fog text requires a fog/projection check before drawing
conversion conclusions. A native WebRTC exception is a stream failure. A capture
showing another app is a desktop-control blocker; send no input from that view.
See the [desktop runbook](DESKTOP-VALIDATION.md).

## Release gates

- [ ] Review PR #8 and retain complete Windows/Linux CI logs; fail the gate on a
      failed diagnostic phase, even if a later repeat passes.
- [ ] Reconcile exact run/pass/skip totals per OS and Python version.
- [ ] Bound the historical LevelDB failure with diagnostics and an explicit release
      limitation or a reproduced, tested fix; no retries that hide failures.
- [ ] Close bounded fog or visibly exclude it (currently excluded above).
- [ ] Have a fresh operator exercise installation, native acceptance and recovery
      on separate content; confirm no overwrite/source mutation.
- [ ] Review provenance, loss reports, compatibility scope and release artifacts.
- [ ] Obtain deliberate review/release approval before merging or tagging.

## Synthetic operator rehearsal

From a complete repository checkout with requirements.txt installed:

```powershell
py scripts/rehearse_scene_import.py --out rehearsal-output-NEW
```

This developer tool intentionally uses the repository's synthetic test-fixture
builders, not private Manor/Crypt assets. It invokes the public capture/audit and
package preflight/build CLIs from an unrelated working directory, relocates all
three profiles and makes the original fixture paths unavailable. It verifies
dependency coexistence, a zero-token scene, supported/rejected tokens, unchanged
source bytes, overwrite refusal and changed-input rejection. It also reviews a
simulated identical destination and detects a retained manual note edit (20 CLI
commands total). Each command's
stdout/stderr and exit code are retained. Existing rehearsal directories are
refused; failed runs retain evidence instead of silently retrying.

Only the freshly created synthetic fixture directory is renamed. No installed
assets are read or written. Inputs already include synthetic native geometry and
controls: this does not automate native import/export/calibration, test a fresh
human operator, or establish Toolkit acceptance. Follow the manual steps above
for a real source. See [rehearsal evidence](../validation/2026-10-31-OPERATOR-REHEARSAL.md).
