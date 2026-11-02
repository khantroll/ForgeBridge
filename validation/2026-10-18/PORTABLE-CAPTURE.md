# Portable native capture evidence — 2026-10-18

Desktop checks remain pending independently of development. The full exact
operation/process/privilege/recovery report stays local in
.test-tmp/CAPTURE-SUPPORT-REPORT.md and has not been submitted externally.
No new screenshots, input, installation or native settings changes were made.

PASS (file-level): Manor/Crypt native bundles and relocated pinned profiles.
Source identity, input hashes, calibration and output namespaces were revalidated.
Native bundles contain 8/12 files. See [bundle hashes](portable-capture-results.json).
Original member bytes and control ZIPs are retained; calibration is preserved,
not inferred. This is not observation inside Toolkit.

PASS: four new tests cover closure, byte preservation/determinism, missing,
conflicting, case-aliased and unsafe paths, overwrite refusal, relocation and input
changes. Mid-copy profile edits abort publication without reverting the edit.
Running/unknown/closed Toolkit guards are simulated; saved snapshots reread bytes.
Source-reader failures retain their existing diagnostic text.

Initial full suite: 148 run, 142 passed, 4 Windows symlink skips, 1 failure, 1 error
(1618.064s). The safety failure rejected a process-launch import, now replaced by
read-only psutil enumeration and a declared optional dependency. The existing
zipped LevelDB comparison reported scene-vault absent and subsequently passed.
Final targeted run: 6 run, 6 passed (238.858s), covering all four new tests and both
affected existing checks. No clean full-suite rerun is claimed. The four symlink
skips remain skips, not passed safety checks.

An initial Crypt capture refused publication when the LevelDB reader could not
open the copied Adventure pack. Controlled reads then opened the original pack,
its copied Manor counterpart and the fixture without diagnostics. One controlled
retry produced the validated Crypt bundle; cause remains unconfirmed. No source
data or conversion math was changed to address it.

Full scene recompilation is optional in the demonstration script. An extra build
was stopped after verifying its owned Python process identity; its scratch scene
ZIP is not accepted as build/runtime evidence. Completed capture checkpoints were
revalidated and reused. No original content or installation changed.

BLOCKED/PENDING: bounded desktop helper setup/enumeration recovery failed.
No activation/capture/input followed; another-window comparison remains unavailable
before enumeration. Crypt actual-player visibility, profile player restart and
bounded fog remain pending. Accepted GM and earlier Multi Scene player evidence
remain accepted. Resource/recovery details stay local; no after-cap/causal claim.

Manual steps remain native import/export/calibration, reviewed installation, GIF
setup and bounded fog. Labels off; Foundry vision/fog, procedural light animation
and actor/stat behavior remain gaps. Next independent task: investigate intermittent
read-only LevelDB snapshots with controlled fixtures and retained diagnostics,
then extend native-reference audit reporting. No human framing prerequisite.
