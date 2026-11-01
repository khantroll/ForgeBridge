# Scene-import acceptance matrix

Baseline: PR #8 at 3409bd9, 2026-10-31. One row per numbered item in
[completion roadmap M0–M2](COMPLETION-ROADMAP.md). PASS applies only to the
whole stated item; partial evidence leaves it OPEN. BLOCKED identifies a specific
external prerequisite. No runtime result is inferred from hashes or file builds.
Windows native observations below use Toolkit **0.5.1.18**, launcher **7.0.0.3**.
File-only checks have Toolkit **N/A**. No desktop testing occurred for this matrix.

| Item | Status | Evidence file and evidence commit | OS / Toolkit | Still needed |
| --- | --- | --- | --- | --- |
| M0.1 PR integrity, safety, determinism, provenance, overwrite refusal, profile pinning review | OPEN | tests/test_scene_profile.py; docs/SCENE-IMPORT-RELEASE.md; validation/2026-10-31-INSTALL-REVIEW.md (1907fc0); native merge safety (0919cf6) | Windows/Linux file checks / N/A | Complete independent PR review and resolve feedback; tests alone are not review acceptance. |
| M0.2 Complete clean Linux and Windows suites with exact provenance | PASS | validation/2026-10-31-SCENE-BATCH.md, implementation 9a86c63, GitHub run 41257170986: Linux 185 run/181 passed/4 skipped; Windows 185 run/182 passed/3 skipped; logs and suite artifacts retained by workflow | GitHub ubuntu-latest/windows-latest, Python 3.13 / N/A | Scoped to this tested implementation. Repeat release candidate checks; older local failures remain M0.3 evidence, not erased by CI. |
| M0.3 Bounded LevelDB diagnosis and justified release exception/containment | BLOCKED | validation/2026-10-31-NATIVE-REPLACE.md (d85e6f5); validation/2026-10-31-BINDING-PROVENANCE.md (69def77) | Windows 11 / N/A | Host replacement intermittency unresolved; explicit release exception or demonstrated containment required. Investigation frozen by user; no more probes/retries/tracing. |
| M0.4 Relocation, closure, pinned inputs, audit and unsafe-input refusals | PASS | tests/test_scene_profile.py; tests/test_native_capture.py; validation/2026-10-24-DEPENDENCIES.md (107fe2b); validation/2026-10-31-OPERATOR-REHEARSAL.md (dd824b9); merge safety (0919cf6) | Windows and historical Linux/Windows CI / N/A | Preserve regressions; Windows symlink tests skipped locally are not passed safety tests. PASS is file-level behavior, not runtime. |
| M0.5 Resolve review and merge | NOT STARTED | PR #8 remains open; docs/COMPLETION-ROADMAP.md (2603fee baseline) | N/A / N/A | Review/sign-off and gates; user explicitly prohibits merging in this work. |
| M1.1 Two real structurally different source scenes | PASS | validation/2026-10-16/profile-pair-audit.json; validation/2026-10-18/profile-runtime-file-audit.json; STATUS.md (39c163f, 7d701c5 history); validation/2026-10-31-PROFILE-PLAYER.md (af9d99e) | Windows / 0.5.1.18 | Manor/Crypt scoped acceptance only; private inputs are not redistributable fixtures. |
| M1.2 Geometry/grid/calibration, walls/doors/lights, tokens, notes/media/audio and isolation | OPEN | validation/2026-10-15/VALIDATION.md appended fresh combined/multi-token results (9de3e34); profile file audit and GM notes (39c163f, 7d701c5); player evidence (af9d99e) | Windows / 0.5.1.18 | Existing scoped blocking/light/token/note/PDF passes retained; comprehensive two-profile audio and all requested field coverage not demonstrated. Do not extend prior map observations to every output. |
| M1.3 Save, Toolkit close/reopen, actual player and unsupported review | PASS | validation/2026-10-18/profile-runtime-file-audit.json and VALIDATION.md GM persistence (7d701c5); validation/2026-10-31-PROFILE-PLAYER.md (af9d99e) | Windows / 0.5.1.18 | Accepted GM saved persistence plus representative player restart checks; Oct31 player session itself was not saved. Maintain scope and source states. |
| M1.4 Bounded manual fog reveal/hide and saved restart persistence | BLOCKED | validation/2026-10-31-PLAYER-ADDRESS.md (4a27535, 3409bd9) | Windows / 0.5.1.18 | Claude built-in-browser run on disposable fog map: reveal, observe player, cover, reveal, save, normal restart, confirm persistence. No Foundry fog/vision mapping claimed. |
| M1.5 Manual UVTT import/export/calibration and GIF/FPS behavior | PASS | validation/2026-10-15/VALIDATION.md appended fresh UVTT geometry and synthetic GIF restart results (cf50ebf / 9de3e34 historical baseline) | Windows / 0.5.1.18 | These steps remain manual; procedural light animation is separate. Repeat only for relevant changes. |
| M1.6 Non-success cases and unsupported edge conditions | PASS | tests/test_scene_profile.py and tests/test_tokens.py (9de3e34); validation/2026-10-31-OPERATOR-REHEARSAL.md (dd824b9); install conflict evidence (1907fc0) | Windows, historical CI Linux/Windows / N/A | Scoped synthetic missing/hash/identity/reference/grid rejection coverage; not proof for every Foundry source. |
| M2.1 Documented source-to-reviewable-package invocation and graded loss | OPEN | docs/SCENE-IMPORT-RELEASE.md (1bc58ea); package acceptance disclosures (69def77); docs/SCENE-PROFILES.md | Windows/Linux file pipeline / N/A | Calibrated profile package command works; raw source still needs explicit native import/export/calibration. No single automatic raw-source invocation or fresh operator acceptance. |
| M2.2 Relocation, dependencies/missing/conflicts before writes/install | PASS | validation/2026-10-24-DEPENDENCIES.md (107fe2b); validation/2026-10-31-OPERATOR-REHEARSAL.md (dd824b9); install review (1907fc0) | Windows / N/A | File-only; destination can change after review, so operator must recheck actual destination. Batch interaction is separately tested by the next slice. |
| M2.3 Safe preflight and human-reviewed installation/no overwrites | PASS | docs/SCENE-IMPORT-RELEASE.md; validation/2026-10-31-INSTALL-REVIEW.md (1907fc0); src/forgebridge/install_review.py | Windows / N/A | Static snapshot assertion is operator supplied. No automatic install, update, campaign edits or overwrite authorization. |
| M2.4 Prerequisites/versions/limitations/commands/rollback/troubleshooting | OPEN | docs/SCENE-IMPORT-RELEASE.md (1bc58ea, 1907fc0); README.md; docs/SCENE-PROFILES.md | Windows/Linux documented; native Windows / 0.5.1.18 | Fresh-operator review and explicit supported Foundry-version compatibility corpus; existing examples are not a broad compatibility promise. |
| M2.5 Build artifacts/release gates and v0.9 candidate tag | NOT STARTED | docs/COMPLETION-ROADMAP.md; .github/workflows/tests.yml (1bc58ea) | CI Linux/Windows / N/A | Release artifacts, complete gates, reviewed candidate decision. No release tag authorized or created. |

All evidence commits are historical anchors, not claims that each file was first
introduced there. Accepted runtime checks remain distinct from later session ICE
failures. Labels stay off; GIF migration remains manual; actor/stat/behavior,
Foundry fog/vision and procedural animation mapping remain conversion gaps.

## Batch/CI follow-up

Implementation and regression evidence: [scene batch](../validation/2026-10-31-SCENE-BATCH.md)
at 9a86c63. Its full CI suites pass on Python 3.13: Linux 185 run/181 passed/4
skips; Windows 185 run/182 passed/3 skips. This supersedes the pending current-head
CI verification in the baseline evidence and supports M0.2 PASS for 9a86c63.
It does not erase the older local host failure or resolve M0.3's release decision.
Release candidate checks must still be repeated at the eventual release head. M1 runtime statuses are unchanged. Batch package generation and
combined closure are file checks, never native runtime acceptance.
