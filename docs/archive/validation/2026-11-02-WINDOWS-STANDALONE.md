# Windows standalone candidate — 2026-11-02

Branch windows-standalone, from main v0.10.0 (523cfcd). No Toolkit launch,
control, real MyAssets access or real installation. Toolkit was already running
on this host and was left alone. Names confirmed by the owner: ForgeBridge.exe
(windowed GUI), forgebridge-cli.exe (console); Windows cannot distinguish the
original requested names by capitalization alone.

## Local build and runtime evidence

- PASS: PyInstaller 6.22.3 on local Windows x64 Python 3.14.2; two onedir EXEs,
  shared _internal; no UPX or one-file extraction. CI independently builds 3.13.
- PASS: fresh ZIP extracted to a relocated path with spaces, no Python on child
  process PATH and no PYTHONPATH/PYTHONHOME/VIRTUAL_ENV. Actual EXE --version
  reports ForgeBridge 0.10.0; inventory validates generator 0.10.0 with IR 0.1.0.
- PASS: actual EXE converts untouched fixtures/synthetic-module to a native ZIP
  with pdf_mode pages; second synthetic fixture renders two PDF page images.
- PASS: actual EXE reads a freshly generated synthetic LevelDB module and builds
  native output, exercising the bundled plyvel-next/native DLLs.
- PASS (automated, not manual visual QA): real frozen Tcl/Tk 8.6.15 file-picker
  widgets, file selection, native dialog-command argument validation, psutil,
  worker queue, callback exception dispatch and traceback log. Blocking native
  modal interaction was not driven; dialog dispatch is captured by the smoke.
- SKIPPED LOCALLY: fake install/uninstall phase, because Toolkit is running.
  No guard bypass or app shutdown. CI must run the actual CLI fake installation
  and uninstall --keep-changed and requires an overall PASS.

The candidate contains Tk/Tcl, Pillow, plyvel-next's delvewheel DLL directory,
pdfium, psutil, package schemas, native note schema, release metadata, a version
fallback and dependency license notices. Frozen schema lookup refuses to borrow
data from a developer checkout. Versioning exposed an old schema constant:
generator version is now release-version text; IR version stays exactly 0.1.0.
No conversion/installer/uninstaller logic was changed.

Local folder: **55,023,480 bytes (52.47 MiB)**. ZIP: **28,231,981 bytes (26.92 MiB)**.
Both below the 150 MB ZIP limit; no risky Tcl/Tk trimming was needed. Test modules
and optional large packages are excluded. build-summary.json always lists the
largest contributors; local sizes differ from the Python 3.13 CI artifact.

Candidate:
.test-tmp/standalone-delivery/ForgeBridge-0.10.0-windows-x64.zip
SHA-256: d09115a7ff80aec03e289604bcff4efb4f4469a95e161e188638de3dcc6964ed
Full local results: 2026-11-02-windows-standalone-local.json.

## Source suite and limits

Full local suite: **255 run, 250 passed, one failed, four skipped**. Skips are
Windows symlink privileges. The one failure was the existing notes
LevelDB/adventure subcase: missing_entry instead of resolved. Its existing
focused test passed once in isolation. Both raw logs remain under .test-tmp:
standalone-full-suite-verified.txt and standalone-notes-focused.txt. Cause is
unconfirmed; the LevelDB reader was not changed, errors were not suppressed,
and no retry loop, attribution probe or security/settings change was introduced.
The earlier version/schema coupling failures were fixed and focused inventory
regressions passed (17 run, one symlink skip).

PR CI checks are separate evidence: source Linux/Windows suites, existing repeat
job, and the new Windows-standalone build plus extracted-EXE smoke. Its artifact
includes ZIP, size/hash summary, commands and GUI/fake-install results. Do not
describe the local skipped install or the failed full source run as passed.

No game rendering or Toolkit behavior is established by packaging. Binaries are
unsigned. On a future pushed v* tag, release upload uses matching release notes,
creates only missing releases as pre-releases, and retains the workflow artifact
with an explicit warning/summary if publication is refused. No old tag is moved
and no release is published by this PR session.
