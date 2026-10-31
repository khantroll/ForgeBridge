# Synthetic operator rehearsal — 2026-10-31

PASS (file-level/public CLI): `scripts/rehearse_scene_import.py` completed 18 CLI
commands from a directory unrelated to the inputs. Three synthetic profiles were
copied with their pinned inputs, moved to paths containing spaces, and built only
after their original fixture directory was renamed out of reach. All profile
input paths resolve within their respective relocated bundles.

| Scene | Generated tokens | Explicit rejections | Closed metadata references |
|---|---:|---:|---:|
| A | 1 | 2 | 29 |
| B | 1 | 2 | 29 |
| Zero | 0 | 0 | 24 |

A and B intentionally share source token identities/names and texture while using
different padding, grid, origin and scale. The rejected tokens are a rectangular
footprint and a missing texture. Combined native contents coexist with 74 closed
metadata references. Controls remain separate from scene geometry/calibration.
Per-scene archive and native-payload hashes are in the accompanying result JSON;
whole-package ZIP hashes are run evidence, not a promise of deterministic timestamps.

Each profile passes native export audit and package preflight/build. A second build
to the same output is rejected with unchanged package hash. Appending a newline to
the relocated companion is rejected with a hash mismatch and no output file;
the original bytes are restored afterward. Original synthetic fixture hashes are
unchanged. A new output directory is mandatory; the tool retains command logs on
failure and never installs content. No production retry, permissions change or
LevelDB behavior change was introduced.

Initial targeted regression failed because the rehearsal expected CLI exit 2 on
rejected package builds. Inspection showed the existing package CLI returns 1.
Corrected the rehearsal expectation; did not alter production CLI semantics.
Successful retained standalone run:

```powershell
$env:TEMP = "$PWD\.test-tmp"
$env:TMP = $env:TEMP
$env:PYTHONPATH = "$PWD\src"
py scripts/rehearse_scene_import.py --out .test-tmp/2026-10-31-operator-rehearsal
```

The script depends on this checkout's test fixture builders and requirements.txt.
This demonstrates the documented public CLI sequence with controlled inputs,
not fresh native export/calibration, redistributable real source fixtures, human
installation/rollback acceptance or Arkenforge runtime behavior.

PASS: full Windows 11/Python 3.14.2 suite **168 run, 164 passed, four Windows
symlink skips**, 64.140 seconds. The new end-to-end regression repeats the CLI
workflow in an isolated temporary directory and checks refusal to overwrite the
rehearsal itself. Skips are not safety passes. Local log:
`.test-tmp/2026-10-31-rehearsal-full.txt`. No further full run was needed.

GitHub status query for the prior CI correction returned unauthenticated HTTP 404;
the new CI result remains unverified, not failed or passed by inference. No secret
lookup or credential change was attempted.

Accepted profile player checks remain PASS. Window switching recovered Toolkit
capture in the preceding user-requested action; no new UI actions occurred during
this compute phase. Bounded fog remains DEFERRED, labels off. No installed assets,
campaigns, real source media or manually edited notes changed.
