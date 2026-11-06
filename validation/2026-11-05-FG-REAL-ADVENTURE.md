# Fantasy Grounds real adventures — 2026-11-05

Branch `feature/fg-real-adventure`, from main `f44dc64` (PR #31 unmerged at start).
Windows, Python 3.14. Native templates reference Toolkit 0.5.1.18. Toolkit was not
launched for this work. File-level evidence below is **not runtime acceptance**.
Original modules were read-only; no module XML, art or other third-party module
content is committed. The owned synthetic fixture is independently authored.

## Real builds

| Module | NPCs | Items | Story/reference pages | Image notes | Total notes |
|---|---:|---:|---:|---:|---:|
| Well Met in Kith'takharos (3.5E) | 5 | 2 | 26 | 17 | 50 |
| DD5E SRD Bestiary | 323 | 0 | 23 | 0 | 346 |
| DD5E SRD Magic Items | 2 | 1689 | 4 | 0 | 1695 |

All three ZIP modules were unencrypted and completed the existing campaign-note
native writer. Encryption refusal remains covered by the conversion/GUI tests;
no decryption or external-module lookup was attempted. Source SHA-256 before and
after each real build matched:

- Well Met: `4f1544ad363074f0bc4c2135f190a3beaf0dc95381a8476746c0fb8540b8c335`
- Bestiary: `fbc8b58f92ecf34da72d1463fc3ca5f1aa991b5076e9df3e1ef85055734e6747`
- Magic Items: `a094391a03ae881ec79ef6833eb7b4858798fbce65a90f37183d9cff8aa756cd`

Full real reports, every graded loss and record-specific details remain local:
`C:/AMD/fb-fg-phase4-notes-<module filename without .mod>-2026-11-05/fg-campaign-report.json`.
The adjacent `final-source-audit.json` supplements each native build with the final
source-field audit; it does not claim a second native build or runtime validation.
Earlier Well Met reports predate correction of category-qualified image links;
the final coherent install report below supersedes those Well Met link counts.
Baseline native loss counts were 13 approximate/33 manual (Well Met),
647 approximate/234 manual (Bestiary), and 1697 approximate/1025 manual (Magic Items).
Do not add source-audit counts to native counts: they overlap.

Losses cover external art/modules, unresolved links retained as labels,
identification/mechanical fields, non-5e source rules, source typography/frames,
spell/combat automation, and missing/calibration/placement data. None is silently
replaced by invented content. Local reports retain all details without committing
commercial module text. The Bestiary and Magic Items packages were not installed.

## Combined workflow and tests

- PASS (file level): repeated transparent category wrappers; SRD reference record
  groups; reference-page text blocks; paragraph/list/frame boundaries; local and
  same-module-qualified links; external references remain explicit losses.
- PASS (file level): numeric/string AC and HP, stored saves/skills, source speed,
  CR/XP, traits/actions/reactions/legendary actions. Legacy 3.5E stats preserve
  their source attack/save text with no invented 5e proficiency.
- PASS (synthetic file level): `fixtures/synthetic-fg-adventure/` produces one
  coherent map + notes + marker + two portrait tokens; repeated textures retain
  distinct token identities and placement. Grid/rotation/hidden/size serialized;
  dependency closure and fake install/uninstall preserve unrelated bytes.
- PASS (headless GUI): no selected FG maps builds notes only. Foundry selection
  behavior stays unchanged. Review/backup/add-only install is shared, not bypassed.
- PENDING: actual FGU pin/token coordinate alignment and native behavior. The
  centre-origin y-up source interpretation is explicit, not runtime-proven.
- UNSUPPORTED: embedding the NPC link in a portrait token. Earlier Toolkit
  evidence showed linked text changes portraits into note pins. Portraits remain
  intact; the report gives the separate NPC target. Do not say a token opens its
  NPC stat block automatically.

Owned combined file-only output:
`C:/AMD/fb-fg-owned-phase4-2026-11-05/native-package.zip` (not installed).
Its pin targets `FB FG Room`; its two tokens reference `FB FG Watcher`, whose
native note is separately available. Native labels remain off. Fog/vision and
actor automation are not implemented by this work.

## Real Toolkit preparation

The first combined Well Met request exited **2** before installation: one map
needs a grid. Outputs remain at `C:/AMD/fb-fg-real-check-2026-11-05` for inspection;
no install receipt or file additions resulted from that attempt.

The real module has **zero READABLE maps**, **16 ART images**, and one
**NEEDS_GRID** floor plan (`image.id-00017`, key `ee28b18626f9b475635b8f2a`).
That floor plan has sidecar LoS but no grid size. All 17 source images have zero
shortcuts and zero placed tokens. A map containing pins/tokens, or a legendary
5e NPC from this older 3.5E adventure, cannot be honestly claimed as a real test.
No grid, placements or legendary actions were invented.

The explicit notes-only coherent build is
`C:/AMD/fb-fg-real-check-notes-2026-11-05/`. Its map/notes folder setting is
**FB FG Real Check**. Installation details and verified receipt are appended below.

Toolkit targets (runtime PENDING):

- Notes → FB FG Real Check → **Carnivorous Lizard**, **Swamp Man Scout**,
  **Blood Priest**. Scout's source attack text includes multiple attacks; it is
  retained verbatim, not converted into invented 5e mechanics or legendary actions.
- Items: **Staff of Sharing**, **Flat Bottom Skiff**.
- Story: **1. READ FIRST: About White Haired Man Adventures**. Its converted links
  should open **Image: Well Met in Kith'takharos Cover** and **Credits**.
- No real map/pin/token target is installed: supply a calibrated export containing
  those placements for that part of the runtime check. For supported synthetic
  pins, clicking opens the converted story; portrait tokens keep their icon note
  and do not automatically open NPC notes.

## Final install and automated checks

- Explicit notes-only build/install exit **0**, **144 new files**, no refusals.
- Receipt: `C:/AMD/fb-backups/forgebridge-7df6f446170941b781e0ec04d24828ec/uninstall.json`.
- Backup retained in that receipt's sibling `MyAssets` directory.
- All 144 installed bytes match both receipt SHA-256 and the archive.
- Package SHA-256: `2443e0c3e5bc74b25f816dc368af08a4f0d0acc0ce36f45b4e0de2d741d5edc6`.
- Final coherent Well Met report: 50 notes; **13 approximate / 6 manual losses**.
  The six manual losses list unmapped extra NPC fields and item identification;
  all converted local story/image/NPC links now resolve. Missing map calibration
  and placements are separately recorded in `unbuilt_images` and above.
- Full final Windows suite: **332 run, 328 passed, four Windows symlink skips**;
  all six new integration tests passed. Skips are not passed symlink safety checks.
- Toolkit remained closed, was never launched or killed; actual appearance,
  navigation, movement and persistence are PENDING, not inferred from these files.
