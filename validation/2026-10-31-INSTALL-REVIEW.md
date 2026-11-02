# Installation review and release blocker — 2026-10-31

PASS (implementation): `forgebridge.install_review` accepts multiple completed
package ZIPs and an explicitly selected static MyAssets copy. It requires a
`--static-snapshot` CLI acknowledgement, emits JSON and never writes a report,
installs assets or changes settings itself. The acknowledgement declares caller
intent; it cannot prove how the copy was made. No live installation was read here.

Reuses the native archive path/size/symlink guards, atomic merge and metadata
reference audit. A new bounded combined-package loader permits safe supplemental
reports outside MyAssets while preserving the stricter native-export loader.
Supplemental files are listed as not installed. Windows case aliases and linked
ancestors/components are blocked; exact identical shared dependencies deduplicate.
Snapshot reads have per-file/aggregate limits and a second comparison to detect
changes. Review is point-in-time evidence, never an installation/overwrite permit.

PASS: five regression tests cover new/identical/user-edited classification,
no writes, case aliases, parent-file collisions, conflicting packages, ZIP links,
missing metadata references and a controlled snapshot mutation. The mutation is
reported as failure; its simulated user edit is left intact. The extended portable
operator regression also passes: 20 CLI commands, including an identical simulated
destination and one detected/preserved manual note edit. No private fixture or
real campaign is required by these tests.

PASS (retained real packages, simulated destinations): Manor/Crypt packages from
the accepted profile milestone compare as 458 new files against an empty static
destination, then 458 identical files after seeding a disposable copy. Replacing
one copied note with a synthetic user edit yields 457 identical/one conflict; the
edit remains unchanged after review. Metadata references close at 529. No live
installation was read or edited. Input package hashes and totals are in
2026-10-31-install-review-results.json; disposable files remain under
.test-tmp/2026-10-31-real-install-review.

FAIL (full suite): Windows 11/Python 3.14.2, **173 run, 168 passed, four Windows
symlink skips, one error**, 71.266 seconds. Command uses process-local workspace
TEMP/TMP and PYTHONPATH=src:

```powershell
py -m unittest discover -s tests -v
```

Failing test: `test_rebuilt_leveldb_scene_matches_committed_uvtt` in test_uvtt.
The copied database could not open. Retained reader diagnostic:

```text
leveldb-not-decoded: LevelDB directory could not be opened.
IOError: IO error: <workspace>/.test-tmp/<temporary-copy>/db/000006.dbtmp:
Unable to remove the file to be replaced.
```

Full local log: `.test-tmp/2026-10-31-install-review-full.txt`. No error suppressed,
no retry added and no full-suite rerun to replace this evidence. Earlier clean
runs remain historical, not current proof. Skips are not safety passes.
The failing database copy was managed by the existing test's temporary-directory
cleanup and is not claimed retained; the full diagnostic/error log is retained.

PASS (bounded diagnostic only): a separate new output directory ran three trials
each of new database creation, copied-fixture opening and ordinary file replacement:
9/9 pass; source hashes unchanged. Command:

```powershell
py scripts/diagnose_leveldb.py --out .test-tmp/2026-10-31-leveldb-recurrence --trials 3
```

This controlled comparison does not establish root cause or fix the intermittent
failure. Diagnostic operations and original failure evidence are retained. Local
Python launcher inventory exposes only 3.14 and 3.14-32; upstream CI uses 3.13.
No Python version, antivirus, indexing, sync, permissions or process priority was
changed to force a pass. No imported scripts run.

STOP/RELEASE BLOCKER: intermittent Windows snapshot opening remains unrooted;
reviewed CI outcomes for this new head are not yet available. Continue root-cause
investigation with retained failing context or another controlled environment,
not automatic retries or source database mutation. No merge/tag/release performed.
Bounded fog remains deferred/excluded; accepted profile player results stand.
Labels off; native calibration, reviewed installation, GIF setup and actor/vision/
procedural behavior gaps remain as documented.
