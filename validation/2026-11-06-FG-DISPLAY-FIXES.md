# PR #32 main integration and display corrections

All new evidence is **file-level only**. The Arkenforge trial has ended. No real installation, desktop control, Toolkit launch or real MyAssets change was performed. The historical Claude/Jeffrey observations in `2026-11-06-TOOLKIT-CHECK.md` remain separate and unchanged. Windows / Python 3.14; native schema reference Toolkit 0.5.1.18.

## Merge resolution

Merge current main `b2d2e4e` into `feature/fg-real-adventure`, preserving the PR's published history. Resolve all six conflicts:

- `convert.py`: keep both notes-only FG selection and Foundry Data validation/CLI, scoped actor context, campaign and direct-package calls.
- `native_tokens.py`: retain the source-neutral IR target; pass optional Foundry Data through its Foundry wrapper to the shared safe art resolver. FG staged portraits still use the same target without an external Data root.
- `fg_convert.py`: retain campaign notes, pins, portrait tokens and their counts; apply #33 visibility after placement. Fog/light effects and layered explicit PC sight attach to existing native placements, never stray lights. Unsupported ranges, ownership/modes and effects stay explicit losses.
- CHANGELOG, BUILD-MAP and USER-GUIDE: retain both feature sets and remove contradictory duplicate feature rows. Motion/ambience, Foundry Data and native visibility wiring remain intact.

## Defect regressions

| Defect | Written-field result | Remaining runtime evidence |
|---|---|---|
| Literal FG carriage-return/newline escapes | Normalize actual CR/CRLF and singly/multiply escaped r/n sequences in prose before markup cleanup; native fields contain real newlines | No new native observation |
| Dim/unspaced story and reference text | Shared ordinary text-field writer emits explicit white body / pale links on dark background; campaign cleanup preserves paragraph boundaries like Foundry journals. Parchment text remains dark | Render appearance not re-observed |
| Empty legacy row above Challenge | Merge main's zero-size zero-width glyph request for nongated empty rows; preserve false native active flags. Owned 3.5E Blood Priest-like fixture asserts written fields, no newlines/labels in the empty proficiency row, and retained Challenge 4 | **Visual gap collapse remains unverified**; captured schema has no proficiency/skills/senses/languages active flags. No invented member or claim of visual PASS |

Five owned regression cases cover all three defects and a combined map with notes, pin, portrait tokens, LOS/persistence, flicker and a layered PC sight light. Existing Foundry Data, motion/ambience, ownership and visibility tests run with the full suite. No module prose/images are committed.

## Real-module reproduction

Use the original read-only `%APPDATA%/SmiteWorks/Fantasy Grounds/modules` modules and fresh outputs under `C:/AMD/fb-fg-pr32-display-2026-11-06/`. Build each through `convert MODULE --notes-only --out NEW_FOLDER`, matching the earlier full-record count table; do not invent grids for their uncalibrated images. Synthetic integration covers map placement/visibility wiring independently.

The adjacent JSON records source/output hashes, all note/text audit totals, losses and equality with every count in `2026-11-06-FG-FULL-RECORDS.json`. Complete per-record losses remain in each local conversion report. Audits decode written ArkenTextString fields (not the intentionally preserved source/provenance JSON); reject literal backslash-r/backslash-n and raw CR. All original modules must retain their SHA-256 values.

## Automated checks

Full Windows suite PASS: **368 run, 363 passed, five skipped**, exit 0 (140.903 seconds). Four inherited Windows symlink skips plus one isolated Foundry Data symlink-privilege skip; none is counted as a passed safety check. Main had unconditionally created that link in two broad art fixtures, causing WinError 1314 here. Core found/missing-art conversion now runs without requiring a link; a separate linked-art regression runs on capable hosts and skips only WinError 1314. No permission/system change or swallowed conversion error.

## Fresh real-module results — PASS at file level

| Module | Actors | Items | Tables | Stories | Pages | Navigation | Handouts | Notes | Text strings audited |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Well Met | 5 | 2 | 0 | 26 | 0 | 0 | 17 | 50 | 194 |
| SRD Bestiary | 323 | 0 | 0 | 0 | 23 | 5 | 0 | 351 | 8366 |
| SRD Magic Items | 2 | 1689 | 29 | 0 | 4 | 4 | 0 | 1728 | 5365 |

All source counts equal the prior table, including zero spells/parcels/quests. **2129 notes / 13925 decoded native text strings** audited: no literal backslash-r/backslash-n and no raw CR. Ordinary text fields have explicit FFFFFF body / B9CEFF link colours. Source hashes match the earlier run and remain unchanged. Output/package hashes are in the adjacent JSON.

All prior source-loss feature totals remain identical. The only additional losses are explicit actor-empty-layout approximations (five Well Met, 134 Bestiary); Magic Items loss totals are unchanged. Well Met: 18 approximate / 6 manual; Bestiary: 783 approximate / 508 manual; Magic Items: 1748 approximate / 2712 manual. In particular, Magic Items' 1021 unresolved links are retained as explicit losses. This is not lossless conversion or new runtime acceptance.

Reports and native packages are under `C:/AMD/fb-fg-pr32-display-2026-11-06/{well-met,bestiary,magic-items}/`. No install or uninstall was performed on real content. PR #32 remains open; no merge, tag or force-push.

Final integration guard: both source visibility adapters follow the placement writer's first-record policy for duplicate token identities. A duplicate PC record cannot give its sight to an already placed NPC. Unsupported duplicate identities have explicit loss lines. The additional owned regression covers both Foundry IR and combined FG map output. The real notes-only packages above are unaffected; no repeat installation or runtime claim.
