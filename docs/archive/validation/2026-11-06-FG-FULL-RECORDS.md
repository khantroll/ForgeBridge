# FG Phase 4 full record families — 2026-11-06

Extends PR #32 on `feature/fg-real-adventure`, from main `f44dc64`.
Read `docs/SCOPE-CHECK-2026-11-05.md` A2–A5/B1–B2 before the work. This record
supersedes the **active installation** in 2026-11-05-FG-REAL-ADVENTURE.md;
historical build/runtime results are not upgraded or overwritten.

Windows / Python 3.14; native schema reference Toolkit 0.5.1.18. Toolkit was
checked closed and was never launched/killed. All new evidence is **file-level**.
No real module XML, prose, images or archives are committed. Owned fixtures only.

## Implemented

- FG tables use the existing RollTable IR and schema-built native rollable-table
  fields. Range bounds, result text, column labels and converted result links
  survive. Source dice/modifiers/output/hidden-roll/chaining behavior is retained
  and reported as approximate; no imported roll expressions are executed.
  Unsupported/overlapping ranges remain reference text with an explicit loss.
- Reference-manual chapters/sections link converted pages, whose text blocks and
  local/module-qualified aliases remain intact. Native link dependency closure
  is checked; no external module loading or invented cross-module targets.
- Treasure parcels and quests preserve text, currency/item/reward/status fields,
  links and an available image as notes. No inventory/reward automation.
- Unknown top-level/reference record types emit individual unsupported losses.
  Existing source fields not mapped to display remain record-specific losses.
- Existing combined maps/notes/marker/portrait-token convert and GUI paths are
  retained. Pins can target tables or any other successfully converted note.
  Missing grids refuse; explicit notes-only mode does not infer calibration.
- Source HP formula enclosing parentheses are normalized once because the native
  stat block supplies its own pair. Source AC/HP/speed/CR/XP and actions remain
  display data, with legacy 3.5E attacks preserved without invented 5e mechanics.
- Native NPC bindings on portrait tokens remain **unsupported**. The observed
  content-link schema exposes one content target; linked-text approaches changed
  portraits into cyan pins in earlier Toolkit tests. Source NPC associations and
  separate targets are reported, not claimed as working automatic bindings.

## Automated evidence

PASS: final full Windows suite **337 run, 333 passed, four skipped**. These are
Windows symlink privilege skips, not passed symlink safety checks.
Five new regression cases cover tables/result links, chapter navigation,
parcels/quests, unknown records, malformed range fallback, a pin targeting a table,
quest attachment preservation and HP formula punctuation. The six earlier FG
integration cases remain. No imported scripts/expressions were executed.

## Real module outputs

Fresh coherent builds use `C:/AMD/fb-fg-full-records-2026-11-06/`:
`well-met/`, `bestiary/`, `magic-items-local-links/`. The earlier
`magic-items/` run is retained as pre-wildcard-fix evidence. Every graded loss is in each
`conversion-report.json` under `campaign_content[0].losses` and the combined
`native_losses`. No older/supplemental audit is needed for these builds.
Input SHA-256 is compared before/after each run; no FG folder files are modified.
All three requested modules are unencrypted; protection refusal remains tested.
Final counts/hashes are recorded in the adjacent JSON after all builds finish.

## Isolated real installation

The previous owned Well Met check receipt
`C:/AMD/fb-backups/forgebridge-7df6f446170941b781e0ec04d24828ec/uninstall.json`
was retired through the normal uninstaller with `--keep-changed`: **exit 0,
144 removed, zero changed retained**, backup/receipt preserved. No hand deletion.
No original campaigns or unrelated user content were removed.

Fresh Well Met install: **exit 0, 144 added**, receipt
`C:/AMD/fb-backups/forgebridge-d50a6f38f30548fba595b4d27086ead9/uninstall.json`.
Backup is its sibling `MyAssets/`. All 144 installed bytes match the receipt
SHA-256 **and** the root native-package.zip. Package SHA-256:
`4fff7bb76df247a27a0c00ac156aa8ea9f33c3b122b6b4e44a92f7f7a1834081`.

### Exact real Toolkit targets (PENDING runtime)

Notes → **FB FG Real Check**:

- **Carnivorous Lizard**, **Swamp Man Scout**, **Blood Priest**. Scout has multiple
  source attacks, retained verbatim; this legacy adventure contains no 5e
  legendary-action records. It is a 3.5E display conversion, not 5e automation.
- Items: **Staff of Sharing**, **Flat Bottom Skiff**.
- Story: **1. READ FIRST: About White Haired Man Adventures**. Its links should
  open **Image: Well Met in Kith'takharos Cover** and **Credits**.

**Not present in Well Met:** tables, reference manuals, parcels, quests, placed
pins or placed tokens. Its 17 images are **16 ART + one NEEDS_GRID** floor plan,
**Floor Plan: Player Old Temple** (`image.id-00017`, key
`ee28b18626f9b475635b8f2a`). Sidecar LoS exists, but a grid size does not. There
are zero calibrated/readable maps; only notes/images were installed. No grid or
placements were invented to manufacture requested runtime targets. A real pin/
token check needs an FG export containing those records and a calibrated grid.

## Owned control targets, separate from real-module evidence

File-only coherent package:
`C:/AMD/fb-fg-full-records-2026-11-06/owned-control/native-package.zip`.
Names use **FB FG Real Check - Owned** so they cannot be mistaken for real data.
It contains map **FB FG Owned Map**, a pin opening **FB FG Room**, and two bronze
portrait tokens (one hidden, Size 2/90°, one visible/Size 1). Clicking a token
opens its own icon/Size note, not the separate **FB FG Watcher** stat block.
Watcher has two actions and one legendary action in the synthetic source.

Additional owned notes: **FB FG Watch Table**, **FB FG Manual Chapter**,
**FB FG Manual Section**, **FB FG Manual Page**, **FB FG Treasure**, **FB FG Quest**.
Manual page links should open Watch Table and Room; chapter → section → page
navigation is closed. The d2 table links its results to Watcher/Key notes.
Source unknown records deliberately produce unsupported losses and are not run.

The maintainer explicitly approved adding the separate owned control. The initial
file-only package is retained above; the installed final package is
`C:/AMD/fb-fg-full-records-2026-11-06/owned-control-final/native-package.zip`. Actual placement, roll behavior, visibility, note
rendering, navigation and persistence remain Toolkit checks. Labels remain off;
fog/vision and procedural animation are not implemented or claimed here.

## Local wildcard-reference correction

Final loss inspection found 58 `@*` references with converted local targets and
1020 wildcard references without a local target in the first Magic Items run.
Local aliases now resolve `@*` only when the converted target is unique. Missing
or other-module references stay loss lines; no external modules are opened.
Regression coverage checks wildcard aliases on tables and quest links, while
explicit foreign-module references remain rejected/unresolved.
Well Met and Bestiary had zero unresolved wildcard links before this correction;
no installed native bytes depend on it. Magic Items is freshly rebuilt through
convert into `magic-items-local-links/`; that report supersedes the first run.

Final full Windows run after the correction: **337 run, 333 passed, four skips**
(211.759 seconds). No installed native behavior is claimed from these files.

## Approved owned control installation

- Initial convert/install attempt exited **2** before copying: "Cannot verify
  Toolkit is closed; installation refused". The Windows guard uses
  `tasklist.exe /FI "IMAGENAME eq Master*" /FO CSV /NH` with a 15-second timeout.
  The underlying first-call cause was not retained, so it is **unconfirmed**;
  CPU contention is not established as the cause. No permissions/settings changed.
- One read-only call to the same `require_toolkit_closed()` guard then passed.
  One normal install of the already-built package was made after that recovery;
  the production guard was unchanged and ran again. No bypass, elevation or kill.
- Recovered install exit **0**, **40 files added**, all 40 hashes and archive
  bytes verified. Receipt:
  `C:/AMD/fb-backups/forgebridge-d274a447da5b4946b86cc7da16f4115a/uninstall.json`.
- Package SHA-256: `0ad2f65339d31e44d746cba5459a3141c58c55be82596d83aad9cd167c966ac6`.
- Real Well Met and owned controls remain separate namespaces and receipts.
  Bestiary/Magic Items were built file-only, not installed.

Actual owned Toolkit targets now installed (runtime PENDING):

1. Maps → **FB FG Real Check - Owned → FB FG Owned Map**.
2. Central pin → **FB FG Room**, which links Watcher and Copper Key notes.
3. **Second watcher** is visible, Size 1; **Watcher token** is hidden, Size 2,
   source rotation 90°. Restore the hidden source state after any visibility test.
   Token click opens its icon/Size note; automatic NPC opening remains unsupported.
4. Notes → **FB FG Real Check - Owned → FB FG Watcher**: two actions, one
   legendary action, source portrait. This supplements the three real NPCs above.
5. Table: **FB FG Watch Table** (d2, results link to Watcher/Copper Key).
6. **FB FG Manual Chapter → FB FG Manual Section → FB FG Manual Page**;
   the page links Watch Table and Room.
7. Additional notes: **FB FG Treasure**, **FB FG Quest**, **FB FG Copper Key**,
   **FB FG Spark**, and the **FB FG Owned Map** image handout.

None of these synthetic records is attributed to Well Met or used as proof of
real-module placements. Native geometry/coordinate behavior, links, rolls,
rendering, visibility and persistence remain manual Toolkit checks.

## Final real counts and loss totals

| Input | NPCs | Items | Tables | Stories | Manual pages | Navigation notes | Handouts | Total notes | Approximate losses | Manual losses |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Well Met | 5 | 2 | 0 | 26 | 0 | 0 | 17 | 50 | 13 | 6 |
| SRD Bestiary | 323 | 0 | 0 | 0 | 23 | 5 | 0 | 351 | 649 | 508 |
| SRD Magic Items (corrected) | 2 | 1689 | 29 | 0 | 4 | 4 | 0 | 1728 | 1748 | 2712 |

All three have zero source spell, parcel and quest records; the owned fixture
covers those adapters. Every requested real module completed with status PASS
and unchanged source SHA-256. This means completed file generation, not lossless
conversion or interactive acceptance. Adjacent JSON has all hashes, report paths,
loss feature totals, receipts and counts without redistributing module content.

The corrected Magic Items report has 1021 unresolved links (1020 wildcard links
without a converted local target and one explicit missing target), retained as
labels with losses. No replacements or external-module loads were invented.
Other losses include display-only mechanics, identification, unavailable external
portraits, typography and source roll behavior. The full per-record list is in
each report, including the exact field/UUID/source identity. No loss is suppressed.

The final unknown-reference-group policy uses a finite navigation allowlist; a
future/unknown `*index` type is an explicit unsupported record, not silently
classified as navigation. The five new tests and final full suite cover this.
The flat bronze token texture distinguishes portrait/footprint from a cyan pin;
it is not a visual rotation-direction control. Rotation remains serialized-only
evidence until tested with an asymmetric texture in Toolkit.
