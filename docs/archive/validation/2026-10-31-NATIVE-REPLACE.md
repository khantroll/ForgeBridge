# Windows replacement failure attribution — 2026-10-31

## What is now established

The original 173-test failure was at test_uvtt.py line 426, opening the committed
fixture through a temporary snapshot, after the newly built fixture's comparison
had completed. No source database was opened by LevelDB. The previous full suite
remains **173 run, 168 passed, four skips, one error**; not replaced by a green run.

The original diagnostic's Python `os.replace` control was not an equivalent test
of the upstream Windows rename path. Upstream LevelDB's
[WindowsEnv::RenameFile](https://github.com/google/leveldb/blob/main/util/env_windows.cc)
tries MoveFileA and then ReplaceFileA with the ignore-merge-errors flag. Installed
plyvel-next is 2.1.2; its exact linked native source/build revision is not established
by reading current upstream code. The new probe tests that API sequence explicitly,
not a claim of byte-identical wheel internals.

Microsoft documents error 1175 as the replaced file being unable to be deleted;
the [ReplaceFile documentation](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-replacefilew)
describes this outcome. The code does not identify which process/filter caused it.

## Bounded comparisons (new files for every trial; no failed operation retried)

| Case | Sandbox experiment | Host experiment |
|---|---:|---:|
| Create LevelDB | 10 pass | 10 pass |
| Direct copied-fixture open | 10 pass | 9 pass, 1 FAIL |
| Python os.replace | 10 pass | 10 pass |
| Actual reader copy/decode functions | 10 pass | 10 pass |
| Native MoveFileA/ReplaceFileA, no deliberate hold | 9 pass, 1 FAIL | 10 pass |
| Native target deliberately held without delete sharing | 10 expected blocks | 10 expected blocks |

Sandbox native failure: trial 2; MoveFileA returned 183 (destination already
exists); ReplaceFileA returned **1175**. No LevelDB call occurs in that probe
operation, but the combined diagnostic process had imported/used LevelDB earlier.
Both owned files remain: CURRENT is `old\n`, 000002.dbtmp is `new\n`.

Host copied-open failure: trial 6; native LevelDB error reports
`000006.dbtmp: Unable to remove the file to be replaced`. Failed database files
are retained this time. CURRENT still contains MANIFEST-000002, LOG records log
recovery; LevelDB's failure cleanup removed the dbtmp. No retry/open of that failed
database was attempted. Source fixture hashes unchanged in both experiments.

A separate standalone process imports neither plyvel nor ForgeBridge. Its 20 free
replacements pass and its 20 deliberately held targets block as expected. All
deliberately held controls return error **32**, not 1175. Thus a simple missing
delete-sharing handle is not a reproduced explanation of the observed error.
Neither the standalone pass nor any short comparison resolves intermittency.

Process token flags: separate sandbox query shows non-elevated, restrictions=1,
AppContainer=1; host report shows non-elevated, restrictions=1, AppContainer=0.
The host-side LevelDB failure rules out AppContainer alone as the cause. No token,
privilege, security, process priority or antivirus configuration was changed.
No kernel trace, external file-owner evidence or culprit identification is claimed.

Raw trial files/reports retained under `.test-tmp/2026-10-31-native-replace-comparison`,
`2026-10-31-native-replace-host`, `2026-10-31-standalone-native-replace`.
Sanitized summary, exact raw-report hashes and failures are in
[native replacement results](2026-10-31-native-replace-results.json).

## Reproducible diagnostic and implementation

```powershell
py scripts/diagnose_leveldb.py --out .test-tmp/leveldb-NEW --trials 10
py scripts/windows_replace_probe.py --out .test-tmp/native-only-NEW --trials 20
```

Both require new output directories and retain every owned trial file. The first
now includes reader-copy and native controls on Windows; Linux omits native cases.
The second uses only Python stdlib/Windows file APIs. It opens a non-delete-shared
handle only to its own newly created CURRENT, closes it in finally, and changes
no ACLs or global settings. Expected held-target blocks are mechanism checks, not
unexpected failures or evidence about another process. The scripts exit nonzero
if an unexpected operation fails. CI's bounded diagnostic phase will retain and
fail on such failures rather than treating a later success as a retry.

Reader diagnostics now preserve the end of a long native error instead of using
the entire bounded message for a temporary path. They explicitly state that only
a temporary copy was opened and no retry occurred. A regression injects a long
path plus native failure and verifies the cause survives with exactly one open.
No data conversion, retry, source-copy policy or database setting changed.

PASS: seven targeted LevelDB/native-probe tests, 0.474s, no skips. Full suite not
repeated; the earlier failed full result remains current evidence. Probe context
and standalone additions executed successfully in the experiments described above.

Next diagnostic evidence needed: a filesystem-operation trace scoped to the new
trial directory at the moment of error 1175, plus the wheel's linked native revision.
No external support report sent, new tracing software installed or system tracing
started. Root cause and release containment remain unresolved. Bounded fog stays
deferred; accepted player results stand. No desktop work or installed-content edits.
