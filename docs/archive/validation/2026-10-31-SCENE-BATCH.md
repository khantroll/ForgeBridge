# Multi-profile batch workflow — 2026-10-31

File-only session. No desktop/Computer Use, installation, Toolkit settings or
campaign edits. Labels off; bounded fog waits for Claude built-in-browser testing.
No further LevelDB attribution work or reader retry/suppression changes.

## Implementation

`python -m forgebridge.scene_batch --profile A --profile B --preflight` performs
combined read-only planning. Repeated profiles/scopes and case-insensitive map
names, native byte conflicts, aliases and output/dependency shadows are rejected.
Shared native bytes and repeated source token/note identities are reported;
distinct generated scene scopes keep those identities separate. One loss_report
array retains source grades and per-scene unsupported/missing/manual fields.

`--out NEW_FOLDER` stages separate production packages, checks combined native
bytes and metadata closure, then rechecks exact pinned input/profile hashes before
exclusive publication. It never installs or modifies prior output/user edits.
Missing completion report means publication did not finish; no automatic cleanup
of a possibly edited output folder. See docs/SCENE-BATCH.md.

## Automated evidence

Windows 11 / Python 3.14.2; Toolkit N/A. Commands use PYTHONPATH=src;tests and
TEMP/TMP set to the private ignored workspace .test-tmp directory.

- Initial default sandbox temp run: 8 tests errored with access denied before
  fixture setup. No conversion conclusion; changed test temp destination only.
- Development batch run exposed one assertion for the wrong collision category;
  corrected fixture to shadow another scene's preserved geometry. Original
  geometry is retained by the existing builder, so batch planning now includes it.
- Batch/profile targeted: **16 run, 16 passed**, 67.588s.
- Full suite at initial batch implementation: **184 run, 180 passed, four skipped**,
  234.302s. Four Windows symlink skips are not passed safety checks.
- Final batch targeted after input hash guard and changed-input regression:
  **10 run, 10 passed**, 82.222s. Final full suite is delegated to normal PR CI;
  it is not represented by the earlier 184-test run.

Raw command output stays in .test-tmp/batch-targeted.txt,
.test-tmp/scene-batch-full-suite.txt and .test-tmp/batch-targeted-final.txt.
Tests cover mixed supported/rejected tokens, zero tokens, shared textures/IDs,
different grids/padding/calibration, closure, naming/byte/case conflicts, no writes
on failed preflight/staging, changed profiles/inputs, and overwrite refusal.

## Real case (all file-level)

Inputs are the already pinned Manor and Crypt profiles:
validation/2026-10-16/profile-runtime-private/{manor,crypt}.scene-profile.json.
No calibration invented, input repinned or original asset edited.

1. Combined read-only preflight PASS; raw .test-tmp/batch-real-preflight.json.
2. Initial staged real build compiled both packages but refused publication:
   `Source scene identity is missing or ambiguous; select one exact scene` during
   a redundant post-build source-adapter read. Raw .test-tmp/batch-real-build.err.
   No batch destination published. This failed run is retained, not erased.
3. The batch guard now checks exact input and profile hashes instead of reopening
   the already validated source adapter. Unchanged bytes preserve the established
   preflight binding; changed bytes fail. This is a batch correctness/performance
   change, not a LevelDB fix, blind retry, error suppression or investigation.
   The revised real demonstration uses a new destination; outcome recorded below.

## CI on implementation commit 9a86c63

GitHub Actions run 41257170986, Python 3.13:
- Linux full suite: **185 run, 181 passed, four skipped**, 15.011s.
- Windows full suite: **185 run, 182 passed, three skipped**, 29.003s.
- CI skips optional PDF coverage (both OS) and the Windows-only probe (Linux);
  exact reasons are recorded below. Local Windows symlink skips are separate.
The existing repeat job is checked separately; no workflow probes were added or
changed for this feature. Previous step commits 3409bd9 (run 41256109150) and
3c3feab (run 41256207129) also completed successfully.

## Revised real build result — PASS (file level only)

The hash-guard implementation at 9a86c63 completed with exit 0. Output:
`.test-tmp/manor-crypt-batch-hash-guard-2026-10-31/` with scene-01/scene.zip,
scene-02/scene.zip and one batch-report.json. Raw stdout/error are
.test-tmp/batch-real-hash-guard.json/.err. Summary and full package SHA256 values:
[2026-10-31-scene-batch-results.json](2026-10-31-scene-batch-results.json).

- Manor: 1 supported token, 0 rejected; 5 room markers, 46 notes, 19 image attachments.
- Crypt: 9 supported tokens, 1 explicit rejection; 19 room markers, 84 notes,
  55 image attachments. Existing profiles have PDF rendering disabled; no PDF
  or GIF/runtime tests repeated by this demonstration.
- 529 native metadata references close together; 8 shared byte-identical native
  dependencies; 4 repeated source note/document IDs, isolated target scopes.
- Distinct map names/scopes retained, labels off. Original pinned inputs and
  profiles revalidated unchanged before publication. No original saved maps,
  assets, installations or previous batch folders modified.
- One combined loss report retains source reports, 3 unresolved UUID occurrences
  across these packages, token rejection/media gaps and manual/unsupported fields.
- The failed initial real build remains a failed run. This success follows a
  substantive guard correction and a new destination, not a blind retry.

GitHub run 41257170986 at 9a86c63 completed **success**, including the existing
Windows repeat job. Exact skip reasons from full-suite logs: Linux skips 3 optional
PDF tests (renderer absent) and 1 Windows-only native API test; Windows CI skips
3 optional PDF tests. Local 184-test run skips 4 Windows symlink-privilege tests;
its PDF checks run. These are different coverage sets and none is a passed test.
No new LevelDB investigation or workflow diagnostics were added.

Runtime validation of these newly generated ZIPs is **not performed**. Accepted
older profile GM/player observations stay separate. Bounded fog is BLOCKED,
waiting for Claude's built-in browser. Stop here after the minimal batch slice.
