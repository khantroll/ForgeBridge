# Independent reader hardening — 2026-10-24

Implemented a portable single-filename boundary in `read_leveldb_bytes`.
Previously it rejected forward slashes but did not independently reject Windows
backslashes, drive-qualified paths or alternate data stream syntax. The function
now rejects those forms and NUL names before any file write, retaining the existing
`leveldb-skipped-name` diagnostic. This closes the low-level reader boundary even
when callers already sanitize ZIP paths. No claim that a public CLI exploit was
demonstrated, and no attribution to the earlier intermittent `.dbtmp` errors.

PASS: five LevelDB tests, including a new controlled regression with relative
escapes, an absolute destination outside the snapshot, Windows drive/UNC names,
alternate streams, NUL and empty/dot names. Only the permitted CURRENT file reaches
the decode stage, with its exact original bytes. Ordinary fixture directory/ZIP
inventory and rebuilt fixture comparisons pass.

The first test command hit sandbox TEMP directory WinError 5 errors (five errors,
including before database opening). Re-running with process-local TEMP/TMP pointed
at existing workspace `.test-tmp` passed in 0.269 seconds. This is an explicit test
environment correction; no global environment, production retry or permissions
change. It does not establish the cause of previous LevelDB replacement failures.

PASS: full suite **150 run, 146 passed, four Windows symlink skips**, 31.173
seconds. Skips are not passed safety checks. Command:

```powershell
$env:TEMP = "$PWD\.test-tmp"
$env:TMP = $env:TEMP
$env:PYTHONPATH = "$PWD\src"
py -m unittest discover -s tests -v
```

An earlier full invocation omitted PYTHONPATH and had two subprocess CLI failures
(`ModuleNotFoundError: forgebridge`), with the other tests completing; the corrected
invocation above passes. Neither environment failure was suppressed or retried in
production. Local full log: `.test-tmp/2026-10-24-reader-hardening-full-tests.txt`.

No desktop work, player streaming activation, installation, source/campaign edits
or Foundry script execution occurred. Crypt actual-player visibility and profile
player restart remain BLOCKED; bounded fog DEFERRED. Accepted results unchanged.
Labels off; GIF setup, native import/export/calibration and reviewed installation
remain manual. Actor/stat behavior, Foundry fog/vision and procedural animation
remain conversion gaps.

Next independent task: expand native-reference audit regression coverage for
conflicting dependency identities using observed schemas and synthetic exports.
No new native schema or calibration needs to be invented for that work.
