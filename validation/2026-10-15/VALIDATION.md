# ForgeBridge validation — 2026-10-15

## Scope and initial inspection

Branch: `cursor/dynamic-lighting-c6b0`. Tracked working tree was clean on arrival. Existing untracked manor module, images, token assets, companions, UVTT files, templates and prior ZIPs were preserved. No AGENTS.md was found in the workspace or its checked ancestors. Read README.md, STATUS.md, architecture, fixture notes, Arkenforge research and UVTT compatibility notes; inspected CLI, package/map/media code and tests before edits.

This log distinguishes **file-level checks** from **observations inside Arkenforge**. There were no Arkenforge observations in this session. Earlier user confirmations are regression cases, not current PASS evidence.

## Results

| Status | Check | Evidence / limit |
|---|---|---|
| FAIL | Initial automated run | 129 tests: 120 pass, five fail because existing user UVTT files violate a workspace-empty assumption; four errors are Windows WinError 1314 while creating symlinks. |
| PASS | Corrected automated suite | 129 tests run: 125 pass, four explicitly skipped. See automated-tests.txt. UVTT checks now compare pre/post file sets; only WinError 1314 is skipped, other errors still raise. |
| BLOCKED | Four symlink safety checks | Windows process lacks symlink creation privilege. Skipping is not proof of symlink protection. No system settings changed. |
| PASS | Fresh manor second-floor source export | Rebuilt from lob-counts_manor-pk-v13 using scene d0XKyRuR4GqdOagf; UVTT and companion generated with schema checks. Source scene equals previous companion semantically. |
| PASS | Separate native package build | manor-second-floor-validation.zip; distinct map and note folder ForgeBridge Validation 2026-10-15 Manor 2nd. Five markers, 46 notes, 36 image/PDF attachments, 17 pages from ten PDFs. Labels off. Existing calibrated second-floor native map template, 2.56 units/grid, origin 0,0. |
| PASS | ZIP integrity and inert native parsing | audit_package.py / file-audit.json: CRC passes, 170 native files reparse under explicit bounded image limits. |
| PASS | Native target closure | 154 metadata reference occurrences resolve inside archive; all reported marker and attachment targets exist. This does not establish successful UI navigation. |
| PASS | Preservation | Two original template media files byte-identical. Full source companion retained semantically (JSON formatting changes). Fresh source scene equals prior scene. Input/output hashes recorded in file-audit.json. Native map writer independently checks unchanged pre-existing objects outside map name, active tile list and UID counter. |
| BLOCKED | Complete manor rebuild/import/reopen | Second-floor package ready. Fresh UVTT geometry is separate; native map geometry comes from the saved template, not rebuilt from fresh UVTT. Import, opening, saving and reopening not observed. Other floors require corresponding calibrated native exports before combined native packaging. |
| BLOCKED | Tokens: import, placement, scale, movement, persistence | Stoker source token copied byte-for-byte to token-import-assets/Stoker_token.webp. Source pixel position 2000,2800, footprint 1×1 grid, texture scale .8×.8 retained. Native token writer absent; loose-image import needs separate UI test and must not be described as automatic migration. |
| BLOCKED | Fog: reveal/hide, persistence and player output | Source exploration=true retained; no native fog conversion or runtime observations. |
| BLOCKED | Animation: import, playback, positioning, persistence | No .gif/.mp4/.m4v/.webm files found in supplied manor source. Tile video settings alone do not establish animated content. Need a known animated test asset and working desktop control; no native animation conversion claimed. |
| BLOCKED | Labels: visibility controls and player-facing behavior | Labels remain off per repository validation notes. Actual player output not observed. A separate label variant also needs a native text template; hidden flags cannot establish player visibility. |
| BLOCKED | Walls and light blocking; doors open/close | Regression cases only; no interactive observation this run. |
| BLOCKED | Fireplaces/lights and light following moved icon | Regression cases only; preserved package data is not behavioral evidence. |
| BLOCKED | Player View | No display or stream observed this run. |
| BLOCKED | Linked documents, tables, scene index ordering | File targets close, but UI links, rolls and ordering not observed this run. |
| BLOCKED | Persistence after reopening | No map save/reopen or Toolkit restart performed. |

## Explicit source gaps

The conversion report has no source read errors. Two table UUIDs remain missing source documents: RollTable.gbpWgQkZli1luOMi and RollTable.SOSYImI25aYkvTTv. Seven media collection gaps remain explicit. See file-audit.json, and conversion-report.json / handout-report.json inside the ZIP for individual reasons. No replacements or source edits were invented.

## Tools and exact blocker

The normal shell, Node REPL and CUA runtime fail before starting with `helper_unknown_error: setup refresh had errors`; CUA diagnostics additionally report `windows sandbox failed`. Read-only and workspace commands succeeded through approved shell escalation, allowing file checks and package generation. The app terminal tool reports no attached terminal session.

Read the installed Computer Use SKILL.md plus guidance and confirmation policy. Its prescribed `@oai/sky` import through Node REPL also fails during kernel initialization, before it can enumerate apps. CUA native APIs are disabled in that surface. No working screenshot/window enumeration/input surface was established. An installed Arkenforge executable does not resolve this missing control capability. No custom automation workaround was used.

Shortest recovery: restart Codex, reopen this workspace and retry Node REPL initialization / `@oai/sky` app enumeration. If the same sandbox setup error remains, repair/update the Codex local runtime through normal app support, then retry. Required capability: a working Node REPL with the installed Windows Computer Use package able to enumerate windows, capture screenshots and send input. Restart is a recovery attempt, not a guaranteed fix. Alternatively the user can perform the checklist below and provide observations/exported evidence; that remains user-observed validation.

## Resume checklist — isolated test only

1. Confirm working control by listing windows and viewing Arkenforge. Preserve any unsaved user work before changing maps. Keep existing campaigns and original assets intact.
2. Extract the new ZIP outside Arkenforge. Review INSTALL.txt and back up MyAssets before merging. Keep reports and PDF originals outside MyAssets. Inspect destination conflicts before copying: the ZIP also preserves the template calibration note and media. Never overwrite conflicting existing content blindly.
3. Open **ForgeBridge Validation 2026-10-15 Manor 2nd** from the map browser. Record Toolkit version, exact package hash, screenshots, positions and observed results.
4. Check all five room markers, links to rules/pages, table rolls and Start Here order. Check images and all 17 PDF pages, readability and order. Retain the two unresolved table references as known source gaps.
5. Reproduce opaque wall/light blocking, each door open/close, fireplace illumination, moved-light/icon alignment and Player View. Record before/after screenshots on the new map.
6. Separately import staged Stoker as a token, compare its 1×1 footprint and .8 texture scale with source, move across known grid cells, save and reopen. Distinguish manual token recreation from ForgeBridge token generation. Use source scene padding/grid when translating pixel position; do not treat 2000,2800 as native coordinates.
7. On the test copy, reveal a rectangle/polygon, hide a subsection, inspect actual player output, save/reopen and restart Toolkit. Verify fog state and player rendering independently.
8. With an identified animated test asset, test import/playback, position and scale, movement, save/reopen and restart. Record asset hash and distinguish app import support from converter support.
9. Leave baseline labels off. For label tests, use another map copy and a supplied native text object; test visibility while selected/deselected and actual player output. Do not infer success from hidden flags or simulated view alone.
10. Save, switch to a blank map, reopen the test map, then restart Toolkit and recheck maps, notes, token positions, fog, lights and animations. Only observed behaviors receive PASS.
11. For a full geometry rebuild, import the freshly generated manor-second-floor.uvtt into a separate map, calibrate and export it with FB Cal A, then rebuild the combined package using that new export. The existing saved template cannot prove current UVTT importer behavior.

## Reproduction commands

Run from the workspace in PowerShell:

```powershell
$env:PYTHONPATH = "$PWD\src"
py -X utf8 -m unittest discover -s tests -v
py -X utf8 -m forgebridge lob-counts_manor-pk-v13 --uvtt-scene d0XKyRuR4GqdOagf --uvtt-out NEW-DIRECTORY/manor-second-floor.uvtt --compact
py -X utf8 -m forgebridge.package --package lob-counts_manor-pk-v13 --companion NEW-DIRECTORY/manor-second-floor.forgebridge.json --map-template 'MyAssets(1).zip' --media-template FB_Media_notes.zip --name 'NEW UNIQUE TEST MAP' --note-folder 'NEW UNIQUE TEST NOTES' --units-per-grid 2.56 --pdf-pages --out NEW-DIRECTORY/manor-validation.zip
py -X utf8 validation/2026-10-15/audit_package.py
git diff --check
```

Package outputs refuse overwrite; use new paths. The audit script checks the specific artifacts from this session. requirements.txt and requirements-pdf.txt dependencies were already available; no installations needed.

## Desktop retry — 2026-10-15

- PASS — Windows Computer Use initializes successfully through Node REPL and @oai/sky. App/window enumeration and launcher screenshots work. The earlier sandbox-control blocker is resolved for this retry.
- PASS — Installed ArkenforgeLauncher launched through its discovered app ID; launcher v7.0.0.3 visibly lists Toolkit v0.5.1.18.
- BLOCKED — Clicking Launch Arkenforge Toolkit produces this visible launcher message: "The launcher is trying to access a file or folder that requires admin permission: C:\Program Files (x86)\MastersToolkit\user Please run your launcher as Administrator". Toolkit did not open, and no test map was imported or modified. All interactive feature checks remain BLOCKED.
- Next action — User starts the launcher/Toolkit as Administrator and handles any Windows elevation prompt. Then enumerate the Toolkit window and resume the isolated test checklist. No permissions or security settings were changed, and no elevation workaround was attempted.

## Permissions fixed; interactive validation begun — 2026-10-15

- PASS — After the user's permission change, launcher starts Toolkit v0.5.1.18 without the previous admin-folder error. Desktop enumeration, capture and input work. One app approval timeout recovered on retry.
- PASS (interactive, limited scope) — Fresh validation/2026-10-15/manor-second-floor.uvtt imported into the initially blank New Map. The manor image, red barrier outlines, green door controls and yellow light icons visibly render at 36% zoom. This does not yet validate blocking, door transitions, light movement or fog.
- PASS (interactive, initial save only) — Saved a new map named ForgeBridge Runtime 2026-10-15 Fresh Manor 2nd using the UI; title changed to ForgeBridge Runtim... after confirmation. Reopen/restart persistence pending.
- Token work in progress — Created a new empty native token library folder ForgeBridge Runtime 2026-10-15 Tokens and submitted staged token-import-assets/Stoker_token.webp through Import content. Import completion and token placement not yet observed.
- Original maps/campaigns were not opened or edited. The separate generated native ZIP has not yet been installed. Previously BLOCKED feature rows remain pending except for the explicitly scoped import/initial-save observations above.

### Runtime results and safe native-package install

- PASS — Stoker_token.webp displays correctly in the new library folder and image preview; imported asset appears in Live Play/VTT Tokens search. Set only this new asset's default placement to Token; placed NPC Stoker_token_1 on the separate map via the Tokens panel.
- PASS (limited) — Token position visually changes under dragging; native movement semantics and source coordinate calibration remain pending. A later scale edit returned the sprite to its earlier position, so movement persistence is not passed.
- FAIL (runtime scale-persistence expectation; cause unisolated) — Token visibly resized via Transforms from 0.512 to 1.0 with ratio lock; saved file contains both scale copies at 1.0. After blank-map switch and reopen, the token visibly returns to a smaller appearance. This may be note Size-field normalization in Toolkit; no converter token writer exists. Do not change generator code on this evidence alone.
- PASS — Saved fresh manor, switched to newly created ForgeBridge Runtime 2026-10-15 Blank, opened the fresh manor from the Map Browser. Success toast and manor/token appearance observed. This passes map/token existence after reopening, not every token property or Toolkit restart.
- PASS (GM view only) — Fog enable darkens the map at GM strength 50; Clear all fog visibly reveals it; Cover all with fog darkens it again. Covered state remains after blank-map switch/reopen. Local box/brush reveal attempts did not show a clearly bounded change, so local reveal/hide remains BLOCKED/unverified, not PASS. Player output not observed.
- PASS — Closed Toolkit through its exit confirmation before installing generated native package. Process absence checked.
- PASS (file install only) — Preflight of manor-second-floor-validation.zip found 94 new native files, 76 byte-identical existing files and zero conflicting destinations. Created only the 94 new files using exclusive creation; all 76 existing files untouched. install-preflight.json and install-manifest.json record evidence. No existing content overwritten; no backup necessary for overwritten content because none was overwritten.
- Native test map: ForgeBridge Validation 2026-10-15 Manor 2nd; restart and runtime inspection underway. Fresh runtime map and native-template package are separate tests.

### Combined native map observed after restart

- PASS — Toolkit restarted successfully; the generated map appears under Maps/MapImport and opens as ForgeBridge Validation 2026-10-15 Manor 2nd. Native image, walls, door overlays, lights and note markers render.
- PASS — Conservatory marker opens 2. Manor — Conservatory. Its Journal link opens 2. Manor, displaying the ordered page list. The First Floor page link opens 2. Manor — First Floor, with the generated Counts Manor 1st key image visibly embedded. Scope: these sampled links and this image only; all five markers / all media / tables have not been exhaustively exercised.
- PASS (UI response only) — Clicking a lower hall door control updates the rendered scene and edit history. Full open/close/blocking isolation remains pending; this is not a wall/light-blocking PASS.
- Token scale follow-up (file evidence) — Native token note contains ArkenNoteFieldSize with _squareSizeNew=1.0. This is a plausible explanation for transform scale normalizing on reopen, not yet an observed causal UI test. Keep the earlier scale-persistence failure scoped to transform-only resizing; native Size-field workflow remains to validate.
- BLOCKED / pending evidence — Actual player output, local fog reveal/hide, animation playback (no source animation asset), labels-on player visibility (baseline labels off, native text template absent), complete token scale/movement persistence, all regression interactions and complete manor rebuild/import/reopen remain unfinished. Desktop access is now available; these are no longer blocked by the original sandbox or launch permissions. Local box/brush actions have not produced conclusive bounded fog changes with this control path. No converter code fix was justified by the observations so far.
- Current UI left on the separate generated native validation map; saved through the map Save control. All original campaigns and prior maps preserved. Runtime test maps, token library/note and newly installed files are intentionally retained for follow-up; no deletion performed.
