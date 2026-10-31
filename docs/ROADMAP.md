# ForgeBridge Roadmap

**Updated:** 2026-10-31  
**Primary direction:** Import foreign VTT/map and campaign structures **into Arkenforge**. Foundry VTT is the first source. Fantasy Grounds Unity is a planned additional **inbound** source. Bidirectional export is a possible future decision, **not current scope**.

This is a prioritized plan, not a declaration that every capability is released. See `STATUS.md`, PR #8 and its validation evidence for the implementation record. The advanced native scene work resides in **open PR #8**; the main-branch README reflects an earlier UVTT milestone. PR #9 is Fantasy Grounds research only.

## Current verified baseline (October 31)

- Foundry scene ingestion includes zipped LevelDB and embedded Adventure scenes; UVTT output is already on `main`.
- PR #8 builds calibrated native Arkenforge scene packages with geometry, doors/walls, lights, supported tokens, room markers, linked notes/tables, media attachments and dependency-closed assets. Reusable scene profiles pin source identity, hashes and calibration; portable native capture has a read-only `--audit` mode.
- Real Manor and Crypt profile maps loaded, persisted and reopened in Toolkit 0.5.1.18. October 31 runtime validation **passed actual-player generated-token visibility and restart** for Crypt and Manor. The earlier black Crypt output was associated with saved manual fog covering the whole view; the prior WebRTC failure did not recur in two new sessions. Fog was disabled **for testing only**; this is **not** a bounded-fog PASS.
- Current PR #8 `STATUS.md` reports **164 passing Linux tests** for the newest fog/vision loss-report slice. Earlier reported runs had platform-specific symlink skips; platform coverage must be verified rather than inferred.
- Open issues: intermittent Windows LevelDB `.dbtmp` replacement failure, bounded fog/persistence, manual native UVTT/GIF steps, and incomplete Foundry fog/vision, actors/stat blocks, combat and advanced behavior. No general lossless campaign converter has been demonstrated.

## Definition of done: first stable scene-import release

A release may be labeled **scene importer**, not full adventure/campaign converter, once all of these are met:

- [ ] PR #8 reviewed for integrity, regression safety and evidence; either merged or clearly split with no loss of accepted functionality.
- [ ] Run complete automated suite on Windows and Linux; record exact versions, counts, skips, failures and known platform limitations.
- [ ] Reproduce or bound the Windows LevelDB `.dbtmp` problem; document cause or a safe, tested mitigation. Do not introduce blind retries, suppressed errors or mutation of source databases.
- [x] Explicitly exclude bounded native fog from current scene-import acceptance, with a visible warning in every package's conversion-report.json and INSTALL.txt. Native reveal/hide/restart testing remains DEFERRED; this is exclusion, not runtime PASS.
- [ ] Repeat end-to-end imports of representative real Foundry scenes into Arkenforge and verify geometry, walls/doors, lighting, supported tokens, notes/links and assets after Toolkit restart; compare generated/saved provenance and hashes.
- [ ] Verify source contents and user edits remain untouched, including rejected and missing dependencies, path escapes, conflicts, duplicate identities and repeated builds.
- [ ] Produce repeatable installation, import, validation and rollback instructions for a non-developer operator.
- [ ] Explicitly grade unsupported/manual/approximate features and provide sample conversion reports; no silent feature loss.
- [ ] Tag and document the scope of the stable release. No percentage-complete claim without a defined feature denominator.

## Milestone 1 — Stabilize the Foundry scene importer (P0)

October31 execution update: portable CLI rehearsal and static installation review
are implemented. The latest full Windows run has one LevelDB error (173 run,
168 passed, four skipped), so stabilization is not complete. Native API controls
reproduce replacement error1175; installed binary hashes match the pinned wheel
and loaded LevelDB reports1.23. User-approved WPR recording was denied0x80070005;
no trace started. Broader privileged tracing is a separate pending prerequisite.
See STATUS.md and the binding-provenance/trace-plan documents for exact evidence.

**Goal:** Turn the proven Manor/Crypt implementation into a repeatable, safe release candidate.

1. Investigate Windows-only LevelDB transient-file replacement, using controlled fixtures, native logs and reproducible Windows runs. Preserve source bytes; distinguish environment failure from conversion failure.
2. Audit and review PR #8, reconcile the newest status/test results, test packaging and ensure no unrelated Arkenforge campaigns are overwritten.
3. Validate bounded fog as a separate experiment; distinguish native fog configuration from Foundry vision semantics. Document unsupported properties instead of pretending parity.
4. Finish manual UVTT import/export/calibration, GIF/media and install steps with explicit PASS / FAIL / DEFERRED evidence.
5. Add release checklist, compatibility matrix, quick-start and troubleshooting guide. **Exit:** release-candidate scene importer reproducible on a clean test environment.

## Milestone 2 — Reliable multi-scene / adventure ingestion (P1)

**Goal:** Import an adventure's connected scenes without cross-scene contamination.

- Batch selection/inventory of embedded Adventure scenes and regular scene packs, with per-scene input identity and calibrated profiles.
- Detect repeated token IDs/names, shared textures, map naming collisions, missing references and conflicting assets; preserve source provenance.
- Aggregate dry-run/read-only preflight and graded loss reports; allow explicit partial imports rather than silent dropping.
- Validate real multi-scene examples, notes and linked media after restart; measure time/disk use and support deliberate re-import without clobbering edits.
- **Exit:** a reproducible multi-scene workflow with auditable results and safe failure handling.

## Milestone 3 — Rich campaign content (P2)

**Goal:** Extend beyond scene geometry where native Arkenforge equivalents have been validated.

- Journals, encyclopedia references, notes, linked tables, playlists and map-associated media.
- Actors/NPC identities, stat representations, items/spells and roll tables, using exact verified native schemas; keep source metadata and unmapped fields.
- Define a compatibility grade per field: **Native / Approximate / GM-assisted / Unsupported** (and manual hotkey/action where applicable).
- Test actual Toolkit rendering, link resolution and persistence with representative licensed fixtures.
- **Exit:** named feature sets ship only when independently validated; incomplete actor/combat behavior remains reported, never implied.

## Milestone 4 — Behavior and automation translation (P3 / research-gated)

**Goal:** Preserve intent safely when Foundry-specific interaction cannot map directly.

- Static, non-executing analysis of Foundry macros, triggers, regions and effects into a platform-neutral behavior IR.
- Deterministic mappings first; optional model assistance only for reviewable interpretation with schema validation.
- Propose manual GM actions where full behavior cannot be reproduced; no execution of untrusted imported scripts.
- **Exit:** bounded tested behavior patterns, explicit loss reports and no claim of full Foundry rule-engine equivalence.

## Milestone 5 — Fantasy Grounds Unity as an inbound adapter (P2 / parallel research only until M1)

**Goal:** **Fantasy Grounds → ForgeBridge → Arkenforge**, without forking the project or destabilizing Foundry imports.

- Use PR #9 research as a starting point, verify contemporary Fantasy Grounds image/LOS/lighting XML and legal representative exports.
- Create a **read-only inventory/provenance spike** and a mapping matrix for image, grid, LOS/walls, doors, lights, tokens, links and records.
- Compare native FG metadata to UVTT and Arkenforge native package routes, and use a common IR only where equivalence is demonstrated.
- Implement the smallest inbound scene fixture, with feature-loss grading and source safety tests; then expand behind a distinct source adapter.
- **Exit:** one independently verified Fantasy Grounds scene imported into Arkenforge, with no Foundry regression. Complete modules/campaign conversion is later scope.

## Future decision — Bidirectional translation (not scheduled)

Only after stable inbound adapters and proven IR compatibility should the project evaluate Arkenforge → Foundry, Arkenforge → Fantasy Grounds or VTT-to-VTT export. This requires separate product decisions, schema research and round-trip loss criteria. **Do not implement outbound export under the current roadmap.**

## Execution sequence and release gates

| Order | Work | Gate / evidence | Priority |
| --- | --- | --- | --- |
| 1 | Windows LevelDB diagnosis and PR #8 review | Documented cause/mitigation; complete CI/test results | P0 |
| 2 | Bounded fog and remaining manual native checks | Recorded runtime evidence or explicit release exclusion | P0 |
| 3 | Stable scene-import release candidate | Repeatable Manor/Crypt imports, safety checks and instructions | P0 |
| 4 | Multi-scene adventure workflow | Safe batch imports and aggregate loss reports | P1 |
| 5 | Content expansion | Native schema and runtime verification per feature | P2 |
| 6 | Fantasy Grounds inbound proof of concept | Real FG source converted to verified Arkenforge scene | P2 |
| 7 | Behavior translation | Safe, bounded pattern library | P3 |
| Later | Bidirectional exports | Separate approval/roadmap | Deferred |

## Operating rules

- No automatic merge or deployment merely because the roadmap exists.
- Prefer small PRs, fixture-backed tests and preserved evidence over broad rewrites.
- Keep calibrated geometry, native control bundles and source adapters separated.
- Never execute foreign macros and never modify source user content as a side effect of analysis.
- Never silently infer a missing reference, replace existing assets or call a partial import lossless.
- Record Windows-specific skips and native runtime limitations clearly.
- Update this roadmap after evidence-backed milestone changes; `STATUS.md` remains the detailed execution log.

## References

- [PR #8 — calibrated native scene packages and portable capture](https://github.com/khantroll/ForgeBridge/pull/8)
- [PR #9 — Fantasy Grounds inbound research](https://github.com/khantroll/ForgeBridge/pull/9)
- [October 31 profile player validation (PR #8 branch)](https://github.com/khantroll/ForgeBridge/blob/cursor/dynamic-lighting-c6b0/validation/2026-10-31-PROFILE-PLAYER.md)
- [Implementation status (PR #8 branch)](https://github.com/khantroll/ForgeBridge/blob/cursor/dynamic-lighting-c6b0/STATUS.md)
