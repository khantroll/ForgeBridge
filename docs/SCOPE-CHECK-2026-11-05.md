# Scope check — updated for v0.13.0, 2026-11-07

This keeps the A/B identifiers from the 2026-11-05 scope review. It supersedes
stale roadmap planning; historical validation is not rewritten. **The Toolkit
trial ended 2026-11-06. All new release evidence is file-level.** Native schema
reference: Toolkit 0.5.1.18 on Windows. “Done” below distinguishes implementation
from observed runtime behavior; hashes and CI are not runtime validation.

## A. Toolkit-dependent scope — implementation and recorded observations

| # | Item | State / evidence |
|---|---|---|
| A1 | Animated/video tiles, ambient sounds, cosmetic stat rows (#31) | Motion and placed audio **observed PASS** on the owned FB Motion Check, 2026-11-06. Empty-row collapse is implemented/file-level only, not visually passed. |
| A2 | FG real modules (#32) | **Implemented.** Well Met, SRD Bestiary and Magic Items rebuilt; 50/351/1728 notes, matching prior counts. Sampled real Blood Priest/story notes observed; not every note in every module checked. Well Met is legacy 3.5E display-only. |
| A3 | FG pins → native note markers | **Implemented; owned pin-to-story observed PASS.** Real Well Met has no source pins; do not attribute owned controls to it. |
| A4 | FG placed tokens | **Implemented; owned portrait/size controls observed PASS.** Supported placement/rotation/hidden fields have file coverage. Automatic NPC binding omitted to preserve portraits; complete player/persistence behavior not newly proved. |
| A5 | Combined FG maps + notes + markers + tokens, GUI | **Implemented.** Same convert/review/add-only path, plus explicit notes-only mode. Missing grids refused; no manual ZIP surgery. |
| A6 | Optional Foundry Data art folder (#30) | **Done at file level only.** Safe read-only lookup; missing art stays loss. Not seen in Toolkit. |
| A7 | Fog, vision and light animation (#33) | **Done bounded implementation at file level only.** Captured Dynamic fog/persistence, character revealing lights, approximate darkvision, Flicker/Blink and negative-light flags; stored FG LOS/sight/effects share the path. No historical masks, full vision/detection permissions or calibrated scene darkness. Simulate darkness is Toolkit-wide. |

Historical native observations: [2026-11-06 Toolkit check](../validation/2026-11-06-TOOLKIT-CHECK.md)
and [v0.12 display check](../validation/2026-11-05-V0120-TOOLKIT-CHECK.md).
Post-trial FG text/gap corrections and duplicate-identity vision guards are
[file-level only](../validation/2026-11-06-FG-DISPLAY-FIXES.md).

## B. File-level / low-risk engineering and release work

| # | Item | State / what remains |
|---|---|---|
| B1 | FG tables → rollable-table notes | **DONE implementation/file-level.** 29 real Magic Items tables; ranges, columns and converted links. Formula/weight/roll equivalence remains B6, not silently declared complete. |
| B2 | FG parcels, quests, manuals, handouts | **DONE implementation/file-level.** Real manual navigation/pages/handouts and owned parcel/quest regressions; unknown record types have explicit losses. Broad runtime acceptance pending. |
| B3 | Foundry system-compendium monsters/items | **OPEN.** Beyond spells, dnd5e system-pack actor/item references remain losses. Optional spells use `--dnd5e-system`; no automatic external-module guesses. |
| B4 | FG light/environment fidelity | **PARTIAL.** Off lights, stored LOS/sight and recognized effects now mapped at file level. Bright/dim falloff, source color/intensity, ambient/tint, additional bitmap layers/transforms and grid-offset fidelity remain. |
| B5 | Foundry playlist settings | **OPEN.** Preserve/map loop, fade, channel, volume, mode and playback state beyond ordered playable song references. |
| B6 | Roll-table formulas/weights | **OPEN.** Range-table notes exist; nontrivial formulas, weights, replacement/drawn state and chained roll behavior need a supported mapping or explicit review. |
| B7 | Release v0.13.0 | **DONE.** v0.13.0 published as a pre-release; attached ZIP downloaded/hash-checked and both clean-unzip EXEs report 0.13.0. [Publication evidence](../validation/2026-11-07-V0130-RELEASE.md). |
| B8 | Non-developer user guide | **DONE.** FG one-build walkthrough, Foundry Data folder, optional spell pack, campaign-content summary, reviewed install and keep-changed uninstall. |
| B9 | Cleanup | **OPEN.** Existing FB test maps/notes and receipts remain preserved. Toolkit cleanup needs licensed access and review; missing Retire-ForgeBridgeTestContent.ps1 was not replaced with broad deletion. Old roadmap files are superseded by this scope check; reconcile/archive them deliberately. |

Remaining engineering/cleanup after publication: **B3, unfinished B4, B5, B6,
B9**. Outstanding native acceptance (fog/player output, external art and layout
gap removal) remains visible and does not block independent file-level work.

## C. Decisions for Jeffrey

| # | Decision | State |
|---|---|---|
| C1 | Toolkit access after the trial | A licensed environment is needed for further native observations; file-level development can continue. |
| C2 | Release/announcement | v0.13.0 release explicitly authorized 2026-11-07 with checked/file-level/known-limit separation. Remaining B work is disclosed, not hidden behind a feature-complete claim. |
| C3 | More game systems | Not now: supported semantic target dnd5e only. Legacy source-stat display is not new system support. |
| C4 | Code signing | Not done; unsigned Windows EXEs can trigger SmartScreen. |
| C5 | Older Foundry versions | Not now: Foundry v13 only. |

## D. Out of scope by design (reported losses)

- Executing source macros, region behaviors, scripts or active effects/automation.
- Hex/isometric grids; FG movement-only terrain occluders.
- Bypassing encrypted/protected FG content.
- Roll20, AboveVTT and bidirectional Arkenforge export.
