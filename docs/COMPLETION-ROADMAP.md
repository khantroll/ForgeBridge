# ForgeBridge completion roadmap
**Baseline:** 2026-10-31 | **Status:** proposed release plan, not evidence of new implementation

## Mission and scope
**Primary objective: import foreign VTT/map/campaign structures *into Arkenforge*, preserving meaning, editable native structures, provenance, and clearly reporting loss.** Foundry VTT is the first inbound source. Fantasy Grounds Unity is a future *inbound* adapter; no Fantasy Grounds conversion has been implemented. Bidirectional export is a separate, post-1.0 decision, **not** a release requirement. Universal VTT is a useful bridge, not the functional ceiling. Do not silently flatten a supported structure or execute imported macros.

## What is verified (do not confuse branches)
- `main` has the inventory/UVTT and loose image/audio milestone; its README is historical and understates the work in open PR #8.
- **PR #8** (`cursor/dynamic-lighting-c6b0`) contains calibrated Arkenforge native scene packages and portable capture; *open and not merged*. Manor and Crypt packages have been built, installed separately with no overwrites, and runtime-tested.
- October 31 player validation: generated Crypt token visible → hidden → visible; Crypt and Manor generated tokens persist and appear on player output after a normal Toolkit restart. Black Crypt output was manual fog with no revealed area; temporary fog-off is **not** a bounded-fog pass. No map was saved in the October 31 test.
- PR #8 STATUS reports 164 Linux tests passing after Foundry fog/vision reporting work (check exact head/CI before a release); previous runs include platform-specific symlink skips. Intermittent Windows LevelDB `.dbtmp` replacement remains unrooted; do not call Linux green a Windows pass.
- Native import/export/calibration, GIF handling and bounded fog still require manual validation. Foundry vision/fog mapping, procedural light animation, actors/stats and combat/behaviors are gaps.
- **PR #9** is Fantasy Grounds research only; not an inbound adapter.

## Release strategy
Separate a **scene-import release (v0.9/1.0-scene)** from **full adventure/campaign fidelity (later milestones)**. Do not declare the original broad project complete based solely on map tests. Feature scope is explicit and loss reporting stays mandatory.

### M0 — Stabilize and integrate the existing scene work (P0)
**Inputs:** PR #8, tests, 2026-10-31 runtime evidence.
1. Review PR #8 changes for package integrity, regression risks, path safety, deterministic output, provenance, existing-map overwrite refusal and profile pinning.
2. Rerun complete tests on a clean Linux checkout **and** Windows; record exact command, commit SHA, platform, counts, skips, failures and artifacts.
3. Reproduce/diagnose the intermittent Windows LevelDB `.dbtmp` replacement failure with bounded, non-destructive fixtures; fix root cause or document reproducible containment and a release-blocking exception decision. Never conceal it with blind retries.
4. Confirm package/profile relocation, dependency closure, exact input hashes, read-only `native_capture --audit`, and safe failure of missing, case-aliased, symlinked, traversal and conflicting inputs.
5. Resolve review feedback and merge PR #8 only when checks/acceptance gates pass.
**Exit:** reproducible clean suites (Windows failure resolved or explicitly and justifiably gated), documented review, verified installation isolation, PR #8 merged. No silent source-content edits.

### M1 — Complete real Arkenforge scene acceptance (P0)
1. Use **at least two real, structurally different** Foundry scenes (existing Manor/Crypt plus a small independently selected fixture if needed), with rights-cleared data.
2. On current Toolkit: validate image/grids/origin/calibration; wall and door blocking/switching; moved-light positions, intensity approximation; token transforms and hidden state; room markers, journal targets, linked tables, attachments/audio; cross-scene identity isolation.
3. Repeat save → close Toolkit → reopen → player projection; compare expected to observed, and review any intentionally unsupported content.
4. Perform **bounded fog reveal/hide and persistence** in a disposable/snapshot fixture, explicitly separating native manual fog from Foundry vision/lighting conversion. Preserve originals.
5. Manually verify native UVTT import/export/calibration and GIF/FPS behavior; document any constraints.
6. Include non-success tests: missing assets, changed input hashes, duplicate identities, unsupported references, non-square/grid edge cases as available.
**Exit:** versioned acceptance matrix with evidence, before/after snapshots, no regressions, no unexplained lost geometry or hidden-state changes. If fog remains unsupported, expressly mark it as a release limitation rather than passing a fog test.

### M2 — Make scene conversion repeatable for users (P0)
1. One documented invocation from a supported Foundry module/Adventure/world source to a *reviewable* Arkenforge-targeted package and graded loss report.
2. Validate package-independent paths and relocatability; report dependencies, missing assets and conflicts *before* write/install.
3. Add a safe dry-run/preflight plus human-reviewed install guidance; never overwrite user content by default.
4. Document prerequisites, supported Foundry/Arkenforge versions, known limitations, example commands, rollback/backups and troubleshooting.
5. Establish build artifacts and release checks; tag **v0.9 scene-import candidate** only when M0–M2 pass.
**Exit:** a fresh operator can reproduce the accepted scene import without undocumented manual conversion or repository-specific paths.

### M3 — Structured adventure content parity (P1, post-scene candidate)
Deliver feature-by-feature, with capability tests and grades:
- journals/notes and hyperlinks, tables, playlists/audio and scene associations;
- actor/NPC/item/stat records and token relationships where an actual native Arkenforge equivalent is established;
- retained provenance for records with no safe equivalent;
- multi-scene Adventure completeness and migration summary.
**Exit:** corpus-based counts (converted/approximate/manual/unsupported) reconcile to source inventory; native representation and re-open behavior verified, or loss explicitly reported. Do not invent target schemas.

### M4 — Behaviors/automation fidelity (P1/P2)
- Deterministic interpretation of recognizable triggers/actions and static macro references; **never execute untrusted Foundry code**.
- Translate only confirmed Arkenforge capabilities; otherwise create reviewable GM-assisted instructions.
- Optional AI-assisted analysis behind opt-in and schema validation, never required for deterministic conversions.
**Exit:** each scenario has behavioral tests or an explicit unsupported/manual grade; no unreviewed code execution or magical lossless claims.

### M5 — Project-level 1.0 readiness (after agreed scope)
- Define supported feature matrix and promised input types; publish sample migrations, known gaps, security model, recovery instructions and upgrade/compatibility policy.
- Full regression on Windows + Linux; native Toolkit acceptance and user sign-off on representative real adventures.
- Only tag **ForgeBridge 1.0** once the explicitly promised *inbound-to-Arkenforge* capabilities are reliable, or clearly brand a narrower release if actor/behavior work remains outstanding.

## Parallel discovery (must not delay P0)
**Fantasy Grounds → Arkenforge:** use PR #9 as research; collect rights-cleared FGU XML/LOS/light/asset/module fixtures, document semantics and build a narrow inbound proof-of-concept **after** stabilizing the scene pipeline. Prefer a separate source adapter feeding the shared IR. Assess XML→UVTT for simple map features and native packaging for richer cases. Add no FGU release promise until fixture-based feasibility and acceptance criteria exist.

**Future exports:** consider Arkenforge → other VTTs or bidirectional flows only by separate architecture decision, not by stealth scope expansion.

## Suggested order of work
1. PR #8 review/CI; preserve LevelDB evidence and the unresolved release decision. Further LevelDB investigation is frozen by user instruction.
2. Use [the acceptance matrix](archive/ACCEPTANCE-MATRIX.md) for M0–M2 gates. Bounded fog is BLOCKED waiting for Claude's built-in-browser run; no desktop work in the current session.
3. Validate the minimal [multi-profile batch workflow](SCENE-BATCH.md) at file level. Native acceptance is separate; do not install automatically or tag a candidate while gates remain open.
4. Structured campaign content, then safe behavior translation.
5. Decide full 1.0 criteria from evidence; Fantasy Grounds input adapter separately.

## Release gates (always)
- No imported JS/macro execution; reject traversal/unsafe archive paths and ambiguous dependencies.
- No write to existing campaign/Toolkit data without deliberate user-reviewed action, no silent overwrites.
- Preserve source identities and per-scene content boundaries; deterministic builds.
- Every unsupported/approximate/manual feature visible in loss report with provenance.
- Claim only tests actually run on the relevant OS and Toolkit; skipped tests are not passes.
- A finished *scene* importer is not a finished *adventure* importer.

## References
- PR #8: https://github.com/khantroll/ForgeBridge/pull/8
- PR #9: https://github.com/khantroll/ForgeBridge/pull/9
- Current player validation: `validation/2026-10-31-PROFILE-PLAYER.md` on PR #8
- Detailed current implementation status: `STATUS.md` on PR #8
