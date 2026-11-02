# Next steps — agreed 2026-11-01

Working plan for PR #8 (`cursor/dynamic-lighting-c6b0`). The roadmap
([COMPLETION-ROADMAP.md](COMPLETION-ROADMAP.md)) is the general guideline; this
file is the concrete order. Status per item lives in
[ACCEPTANCE-MATRIX.md](ACCEPTANCE-MATRIX.md); update both when a step finishes.

**Hard deadline:** the Arkenforge Toolkit trial ends about **Thursday 2026-11-06,
~7 PM Central** (launcher showed 5 d 14 h left at 04:57 on 11-01). Anything that
needs the Toolkit must be finished before then. Everything else can follow.

**Who does what:** *Claude* = Claude desktop computer use + built-in browser
(the only player-stream client that has run without the ICE exception: four clean
sessions). *Codex* = file-level code and docs; no desktop/Computer Use work.
*Jeffrey* = decisions, approvals, and anything that writes to the real MyAssets.

**Desktop rules (all Toolkit steps):** launch Toolkit only after the launcher no
longer says "Running Arkenforge Toolkit"; player view only in the Claude built-in
browser at `http://127.0.0.1/` (no Waterfox/Chrome player tab open at the same
time); stream 1280×720 / 15 FPS; use disposable "Save as new" copies for any
edit; never save Profile Crypt / Profile Manor; one agent drives the screen at a
time.

## Product goal (set by Jeffrey 2026-11-01)

A new user runs **one command or a small GUI**, selects a Foundry package, and
either (a) has the scenes **auto-installed into Arkenforge** (Toolkit closed,
MyAssets backed up, conflict review, add-only copy, refuse on conflict) or
(b) gets **a ready folder set** to copy into MyAssets. **No manual UVTT import,
export or calibration.**

What stands in the way, and the plan:

1. **Calibration — computable.** Both hand-calibrated maps follow one rule:
   2.56 Toolkit units per grid square, origin at the image top-left, y down
   (Manor 3000×4000 → centre (38.4, −51.2); Crypt 4000×4200 → (51.2, −53.76),
   both 100 px grid). ForgeBridge writes the UVTT, so it can derive calibration.
   Confirm on at least one more map size/grid before relying on it.
2. **Native map without Toolkit import — unproven; trial-critical.** Today the
   geometry map comes from a Toolkit UVTT import + export used as a template.
   ForgeBridge must write the `.rwmap` itself (background, walls, doors, lights),
   using record shapes read from maps already in the user's MyAssets (no
   Arkenforge files shipped in the repo). Only the Toolkit can confirm it opens
   correctly, so the spike must finish before the trial ends.
3. **Installer** — add-only copy into MyAssets reusing `install_review`, with
   automatic backup and refusal on any conflict or running Toolkit.
4. **Front end** — `forgebridge convert PACKAGE [--install | --out DIR]`, then a
   minimal local GUI (folder picker, scene list, install/export button, loss
   report view) over the same command.
5. **Fallback if (2) fails by 11-05:** same command/GUI, but each map needs one
   Toolkit "import UVTT" click; everything else stays automatic.

## Part A — needs the Toolkit (before 11-06)

| # | Step | Owner | Done when |
|---|---|---|---|
| A0 | **Native map synthesis spike (top priority).** (1) Read record shapes from an existing saved map in MyAssets (Toolkit closed). (2) Generate a `.rwmap` for one Count's Manor scene directly from the Foundry source with computed calibration: background, walls, doors, lights. (3) Install it as a new disposable map and open it in the Toolkit: alignment, wall/door blocking, lights, player view. (4) Repeat for a second scene with a different size. | Claude — **Crypt + Manor PASS 11-01** (validation/2026-11-01-DIRECT-MAP.md). Schema-built records + convert/install done (Codex); **end-to-end convert --install PASS in Toolkit** (validation/2026-11-01-CONVERT-INSTALL.md); **all 34 scenes build; Manor 1st installed + Toolkit/player PASS** (validation/2026-11-01-MANOR-INSTALL.md) | Both generated maps open and match the UVTT-imported versions, or the exact failing records are documented and the fallback is chosen by 11-05. |
| A1 | **M1.2 per-output runtime check** (after A0; on generated maps if A0 passes, otherwise profile maps). On disposable copies of Profile Crypt and Profile Manor: walls block light/vision; each door toggles and blocks when closed; lights sit where the loss report says; every generated token present with correct size/rotation/hidden state; every room marker opens the right note; note attachments/images open; scene music reported as manual. Check the player view where it matters (door and light blocking). | Claude | A results table per map in `validation/`, matrix row M1.2 updated to PASS or with each failure listed. |
| A2 | **Decide whether to install a batch output.** Codex's `scene_batch` builds Manor+Crypt packages file-only. Validating one in the Toolkit means merging it into the real MyAssets. | Jeffrey | Yes/no recorded here. If yes: back up MyAssets, run `install_review` (expect 0 conflict/0 blocked), install, then Claude repeats a short A1 on the installed map. |
| A3 | **Capture final evidence before the trial ends.** Screenshots/notes of anything still unverified; list any check that cannot be done after the trial. | Claude | Matrix has no Toolkit-dependent row left at OPEN without a written reason. |

## Part B — file-level (can run in parallel with A; Codex)

| # | Step | Owner | Done when |
|---|---|---|---|
| B1 | **Finish the M0.1 code review**: native_map, native_tokens, nrbf, notes/handouts, scene_profile, scene_batch, uvtt geometry. Look for unsafe paths, unbounded reads, silent data loss, non-determinism. Fix with tests. | Codex (Claude reviews the diff) | `validation/` review note covers every module; matrix M0.1 PASS. |
| B2 | **Single entry point** `forgebridge convert PACKAGE --out DIR` (scene discovery, computed calibration, package per scene, combined loss report); `--install` added once A0 and the installer land. Until A0 passes, document the one remaining Toolkit step plainly. | Codex | `docs/SCENE-IMPORT-RELEASE.md` has a copy-paste walkthrough that works from a fresh clone (CI runs it on the synthetic fixture). |
| B4 | **Add-only installer** reusing `install_review`: refuse if MasterToolkit.exe is running, back up MyAssets, copy new files only, refuse on any conflict, write an uninstall list. Tests with a fake MyAssets. | Codex | Installer passes tests; never overwrites; uninstall list removes exactly what it added. |
| B5 | **Minimal GUI** (local, stdlib Tkinter or a local web page) over `convert`: pick package, list scenes, choose install or folder output, show loss report. | Codex, after B2 | A non-technical user can convert the Count's Manor package without the terminal. |
| B3 | **M2.4 user docs**: prerequisites (Python, Toolkit 0.5.1.18, Foundry v13 tested), supported/unsupported list, backup and rollback, troubleshooting (ICE exception → use built-in browser/loopback; relaunch timing; fog starts covered; LevelDB note). | Codex | README points to it; Jeffrey can follow it without asking. |

## Part C — decisions (Jeffrey)

| # | Decision | Notes |
|---|---|---|
| C1 | **M0.3 Windows LevelDB `.dbtmp`**: accept as a documented host-environment exception for v0.9? | Clean Windows CI runners pass every run (4 full suites, 10 repeats, 30/30 diagnostic). Cheap host test first: add the repo and temp folder to Defender exclusions, rerun the suite 3×. If it stops, document that as the containment. |
| C2 | **Merge PR #8 into main** once A1, B1 and C1 are done and CI is green. | Squash or merge commit — Jeffrey's choice. Then close PRs #10/#11 by keeping one roadmap file. |
| C3 | **Tag v0.9 scene-import candidate** (M2.5) after B2/B3 and a fresh-operator run by Jeffrey. | Release notes list limitations from the acceptance matrix verbatim. |

## Part D — after the trial (not started; do not begin before A is finished)

1. **M3 campaign content**: actors/NPC stat blocks into native 5e note templates; items; journals → notes completeness; roll tables; playlists (manual until a format exists). Validation needs a Toolkit licence or a new trial.
2. **M4 behaviors**: deterministic interpretation of simple triggers; never execute Foundry code.
3. **Fantasy Grounds inbound adapter**: research only (PR #9) until the Foundry scene release is tagged.

## Frozen

- Windows LevelDB tracing/probes (until C1 or a new supported-environment failure).
- Formatting-only commits.

## Part B execution updates

B2: public convert entry point and synthetic CI walkthrough implemented. Existing
profiles build native packages; scenes without profiles remain explicit UVTT/manual
outputs until A0. See SCENE-IMPORT-RELEASE.md and validation/2026-11-01-PART-B.md.

B4: add-only installer and fake-MyAssets tests implemented. Full backup, conflict
refusal, process guard and hash-checked uninstall receipts; no real installation.
See SCENE-IMPORT-RELEASE.md. Convert installation remains gated on A0.

B1: remaining module review completed with bounded-path/read/graph fixes,
deterministic archive publication, overwrite refusal and synthetic regressions.
See validation/2026-11-01-PART-B.md. Claude's diff review remains a merge gate;
no A-step evidence or M1 row changed.

B3: operator guide added and linked from README; tested version scope, public
convert workflow, limitations, backup/install/rollback and troubleshooting covered.
Jeffrey's fresh-operator run remains a release decision, not inferred from docs.

B5: local Tkinter front end and .pyw launcher implemented over convert/install,
with scoped selection, export, loss review and guarded native install. Headless
controller tests only; no GUI launch/desktop observation in this session. A0
native backend and fresh human GUI acceptance remain separate requirements.

## Schema-native integration update (file only)

Default convert now builds native maps/backgrounds from code-defined records,
uses computed 2.56/grid upper-left calibration, and runs the existing note,
marker/media/token writers. It emits a ready MyAssets tree, per-scene ZIPs and
combined source/native losses. Explicit --install and GUI review/install use the
same backed-up add-only backend. Profiles remain advanced optional overrides.
Synthetic schema/thumbnail, zero-token/journal-free, scoped-ID and fake-install
checks are in CI. New combined-package and thumbnail Toolkit checks remain Claude's
work; A-step notes and M1 rows are not changed by this implementation.

## Release-path order (agreed 2026-11-01 evening)

| # | Step | Owner | Status |
|---|---|---|---|
| 1 | Convert all 17 scenes (5e + SA) file-only | Codex | **DONE** — 34/34 BUILT, unique names |
| 2 | Install Manor 1st Floor; verify in Toolkit incl. marker note + player view | Codex + Claude | **DONE** — validation/2026-11-01-MANOR-INSTALL.md |
| 3 | Jeffrey tries `forgebridge-gui` on another scene (e.g. Manor 2nd Floor) | Jeffrey | next |
| 4 | Uninstall from both receipts (Crypt, Manor); prove MyAssets restored | Codex + Claude | after 3 |
