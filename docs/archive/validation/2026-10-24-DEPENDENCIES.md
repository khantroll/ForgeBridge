# Shared dependency validation — 2026-10-24

PASS (implementation/file-level): moved the existing capture path policy into
the shared native-export loader. Production control imports now reject Windows
case aliases, reserved names, ambiguous paths and ZIP symbolic links using that
same policy. Final metadata-reference audits check package paths as well, including
the no-token path. Supplemental inert reports remain supported outside MyAssets.

Dependency merges validate all paths and byte conflicts before mutating the
destination dictionary. Conflicting content names the exact path; case conflicts
name both spellings. Exact same-path/same-byte dependencies deduplicate. Different
paths with equal bytes remain distinct identities; no internal schema IDs or
calibration values are rewritten or inferred.

PASS: six new synthetic regressions cover late-conflict atomicity, cross-export
case aliases with identical bytes, exact deduplication with inert reports, unsafe
and symbolic-link exports, split-export cyclic dependency closure/provenance and
no-token package rejection before publication. Original export bytes and a prior
successful output remain unchanged after rejection. Unrelated files are excluded
from the selected closure, and each reachable member occurs once.

PASS: targeted native suite 53/53, 6.935 seconds; full suite **156 run, 152 passed,
four Windows symlink skips**, 37.037 seconds. Skips are not safety passes. Commands
use workspace TEMP/TMP and PYTHONPATH=src; local logs:
`.test-tmp/2026-10-24-dependency-targeted.txt` and
`.test-tmp/2026-10-24-dependency-full.txt`.

The first targeted run found one compatibility regression in the new merge guard:
it rejected the generated conversion-report.json supplemental member. Corrected
the guard to validate supplemental paths without requiring a MyAssets prefix;
the deduplication regression now covers that case. No production errors suppressed.

PASS (real file inputs): both current `*.scene-profile.json` profiles preflight,
and scene-geometry recaptures match the October 18 hashes exactly:

| Scene | Captured files | Bundle SHA256 |
|---|---:|---|
| Manor | 8 | `e60479e9424ced7d7c42fe5fd060bd6f35683cafa3864f52f76c80e31764c814` |
| Crypt | 12 | `5323d2eeae51b6eeb566000188f0a754549125cc90be4d4d3d3c0add1abc3c59` |

Outputs are isolated under `.test-tmp/2026-10-24-dependency-real`; no packages
were installed. An initial attempt selected the older `*.v1.profile.json` files,
which correctly failed shape validation because they lack calibrated `map_path`.
Used the existing current profiles instead; no profile, source or calibration was
modified to force acceptance. Hash equality is provenance evidence, not runtime PASS.

Next independent task: expose a read-only native bundle audit command for users
to inspect selected-map closure and conflicts before choosing a capture destination,
reusing these same checks rather than installing or rewriting assets.

No UI work, installation, campaign edits, PDF/GIF runtime retest or imported-script
execution occurred. Crypt actual-player visibility and both profile player restart
checks remain BLOCKED; bounded fog remains DEFERRED. Accepted results preserved.
Labels off. Native import/export/calibration, reviewed installation and GIF setup
remain manual. Foundry vision/fog, procedural animation and actor/stat behavior
remain explicit conversion gaps.
