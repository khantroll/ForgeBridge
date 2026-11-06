# Scope check — 2026-11-05 (after v0.12.0)

Built from every loss line the code can emit (`src/forgebridge/*.py`), the
validation record, BUILD-MAP, ACCEPTANCE-MATRIX and the open PRs (#30, #31).
`docs/ROADMAP.md` and `docs/COMPLETION-ROADMAP.md` are from 2026-10-31 and are
stale (they predate PR #8's merge and every release); this file supersedes them
for planning.

Toolkit trial ends **Friday 2026-11-06 evening**. "Toolkit" below means the item
can only be proven inside Arkenforge.

## A. Before the trial ends (Toolkit)

| # | Item | Source | State |
|---|---|---|---|
| A1 | Animated/video tiles + Foundry ambient sounds, cosmetic stat-block gaps | PR #31 | Installed as *FB Motion Check*; needs Toolkit look + listen |
| A2 | **Fantasy Grounds on a real adventure**: NPC/item/spell/story notes have only been checked on a synthetic module | `fg_campaign.py` | Real unencrypted modules are on Xenos: *Well Met in Kithtakharos* (ks01 OGL), DD5E SRD Bestiary, DD5E SRD Magic Items |
| A3 | FG map **pins** (story/encounter links) → room markers | `fantasy_grounds.py` "map pins … not converted yet" | Not built |
| A4 | FG **tokens** placed on maps | "tokens placed on FG maps are not read yet" | Not built |
| A5 | FG one-step build (maps + notes + markers + tokens; GUI) | BUILD-MAP: "Map conversion … does not write these notes" | Two separate commands today |
| A6 | Missing Foundry art from a Data folder | PR #30 | File-level done; Toolkit look optional |
| A7 | **Foundry fog, vision and light animation** (Jeffrey 2026-11-05: in scope) | Native schema has light `_flicker`, token `_vision`, manual/visible-through-fog flags | Capture native fog/vision/animation controls in the Toolkit first (before trial ends), then map Foundry token sight, scene fog/darkness and light animation types; FG vision/LOS the same way |

## B. Should do next (file-level is enough, or low risk)

| # | Item | Notes |
|---|---|---|
| B1 | FG **tables** → rollable-table notes | FG `tables` records are not read at all (Foundry tables are) |
| B2 | FG **parcels/treasure, quests, reference manuals, image handouts** | Not read; reference manuals are how many FG adventures store their text |
| B3 | Foundry **system-compendium monsters/items** (links into dnd5e packs other than spells) | Spells resolve via `--spell-pack`; other compendium links stay as text |
| B4 | FG light/environment details | Lights saved off written on; bright/dim falloff collapsed; ambient/tint not mapped; only first bitmap layer; grid offset ignored |
| B5 | Foundry playlist settings | Loop, fade, channel, volume, mode → manual review today |
| B6 | Roll-table formula/weights | Native range table kept; weighted/formula tables need review |
| B7 | Release v0.13.0 | After #30/#31 (+ FG work): notes, tag, ZIP |
| B8 | User guide | No Fantasy Grounds or campaign-content walkthrough yet for non-developers |
| B9 | Cleanup | FB test maps/notes in MyAssets; stale roadmap docs (this file replaces them); retire script missing |

## C. Decisions for Jeffrey (not engineering)

| # | Decision | Why it matters |
|---|---|---|
| C1 | Buy Arkenforge after the trial? | Without it, every later feature is file-level only — the level that missed the playlist bug |
| C2 | Release/announce publicly | **Decided 2026-11-05: only after feature complete (A and B done)** |
| C3 | More game systems | **Decided 2026-11-05: not now** (dnd5e only) |
| C4 | Code-sign the `.exe` | SmartScreen warns on first run |
| C5 | Older Foundry versions | **Decided 2026-11-05: v13 only for now** |

## D. Out of scope by design (keep as reported losses)

- Executing Foundry macros, region behaviors, active effects or automation.
- Hex/isometric grids; FG terrain (movement-only) occluders.
- Encrypted FG Forge/vault modules.
- Roll20 (licensing), AboveVTT (browser extension).
- Bidirectional (Arkenforge → other VTT) export.
