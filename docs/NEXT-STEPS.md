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

## Part A — needs the Toolkit (before 11-06)

| # | Step | Owner | Done when |
|---|---|---|---|
| A1 | **M1.2 per-output runtime check on both profile maps.** On disposable copies of Profile Crypt and Profile Manor: walls block light/vision; each door toggles and blocks when closed; lights sit where the loss report says; every generated token present with correct size/rotation/hidden state; every room marker opens the right note; note attachments/images open; scene music reported as manual. Check the player view where it matters (door and light blocking). | Claude | A results table per map in `validation/`, matrix row M1.2 updated to PASS or with each failure listed. |
| A2 | **Decide whether to install a batch output.** Codex's `scene_batch` builds Manor+Crypt packages file-only. Validating one in the Toolkit means merging it into the real MyAssets. | Jeffrey | Yes/no recorded here. If yes: back up MyAssets, run `install_review` (expect 0 conflict/0 blocked), install, then Claude repeats a short A1 on the installed map. |
| A3 | **Capture final evidence before the trial ends.** Screenshots/notes of anything still unverified; list any check that cannot be done after the trial. | Claude | Matrix has no Toolkit-dependent row left at OPEN without a written reason. |

## Part B — file-level (can run in parallel with A; Codex)

| # | Step | Owner | Done when |
|---|---|---|---|
| B1 | **Finish the M0.1 code review**: native_map, native_tokens, nrbf, notes/handouts, scene_profile, scene_batch, uvtt geometry. Look for unsafe paths, unbounded reads, silent data loss, non-determinism. Fix with tests. | Codex (Claude reviews the diff) | `validation/` review note covers every module; matrix M0.1 PASS. |
| B2 | **M2.1 one documented invocation**: from a Foundry module/Adventure source plus an existing calibrated profile to a reviewable package and graded loss report, using only public commands. Raw-source calibration stays a documented manual step; say so plainly. | Codex | `docs/SCENE-IMPORT-RELEASE.md` has a copy-paste walkthrough that works from a fresh clone (CI runs it on the synthetic fixture). |
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
