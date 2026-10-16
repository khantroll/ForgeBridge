# ForgeBridge validation — 2026-10-15

## Scope and initial inspection

Branch: `cursor/dynamic-lighting-c6b0`. Tracked working tree was clean on arrival. Existing untracked manor module, images, token assets, companions, UVTT files, templates and prior ZIPs were preserved. No AGENTS.md was found in the workspace or its checked ancestors. Read README.md, STATUS.md, architecture, fixture notes, Arkenforge research and UVTT compatibility notes; inspected CLI, package/map/media code and tests before edits.

This log distinguishes **file-level checks** from **observations inside Arkenforge**. Current-build Arkenforge observations began after desktop and launcher permissions were repaired, as recorded below. The summary includes the 2026-10-16 follow-up. Earlier user confirmations remain regression cases, not current PASS evidence.

## Results

| Status | Check | Evidence / limit |
|---|---|---|
| PASS | Automated checks | Latest full run: 136 tests, 132 passed, four Windows symlink checks skipped. Initial workspace assumptions were fixed in 90b721b. Sandbox temp-directory errors on the first Oct 16 attempt resolved by running the suite with approved access. |
| DEFERRED | Four symlink safety checks | WinError 1314 skips are not passed symlink protection checks. |
| PASS | Fresh source export and original separate package, file level | Original ZIP SHA256 c6ea282ae220f9eb7e9bf13905e1689668cd16d11356dae14507c3f9cfd2c3c1. Five markers, 46 notes, 36 attachments including 17 PDF pages. 170 native files parse; 154 metadata reference occurrences close. |
| PASS | Source/template preservation, file level | Source scene retained, original template media byte-identical; original campaigns/source assets and unrelated local files preserved. Two missing tables and seven media gaps remain explicit. Labels off. |
| PASS | Desktop control and launcher | Original sandbox/launcher blockers resolved. Toolkit v0.5.1.18 observed and controlled through Windows Computer Use. |
| PASS | Fresh UVTT import and map existence | Fresh manor image/barrier/door/light overlays render; separate map and manual Stoker survive map switch/reopen. Fresh map reopened after the preceding Toolkit restart. These observations do not pass blocking behavior. |
| PASS | Manual token Size/movement through reopen | Size 1→2 visibly doubles Stoker around fixed center. Numeric X move persists after save→blank→reopen. Details and native comparison hashes in Oct 16 section. |
| FAIL | Transform-only token scale persistence | Horizontal 1.5 saves but normalizes to 1.024 on reopen while Size remains 2. Causal control confirms Size normalization; this is not a converter defect. |
| PASS | Experimental token writer, file level | Source adapter→Token IR→native target; deterministic package, calibrated placement, native Size, scaled RGBA image, rotation/hidden serialization, identity and explicit losses. Generated token has NOT yet been observed in Toolkit. |
| PASS | Sample current-package notes/image after restart | Conservatory marker, Journal and First Floor navigation; Counts Manor 1st key image visibly displays. Scope is these samples only. |
| DEFERRED | Complete five-marker/navigation/table/image/PDF runtime regression | All five markers, table rolls and all 17 PDF pages have not been exercised in this build. Earlier user confirmations are separate historical evidence. |
| PASS | Native whole-map fog, GM view only | Enable/clear/cover changes observed; covered state persists through map switch/reopen. |
| DEFERRED | Local fog reveal/hide, restart and player output | Local bounded change still inconclusive. Stream activation opened a Windows Firewall modal; no actual player output observed. |
| DEFERRED | Wall blocking, door open/close blocking, fireplaces, moved lights | Overlays and a door UI response observed; behavioral isolation still outstanding on current packages. |
| PASS | Fresh-map combined candidate, file level | Uses the newly UVTT-imported saved geometry, not the older template geometry. 176 native files parse; 161 metadata reference occurrences close. UI calibration/import/reopen remains pending. |
| DEFERRED | Generated token restart, full rebuilt package runtime, animation | Firewall modal currently blocks Toolkit interaction. Synthetic three-frame media prepared; playback/position/persistence unobserved. |
| DEFERRED | Labels | Remain off by request; player-facing behavior untested. |

## Explicit source gaps

The conversion report has no source read errors. Two table UUIDs remain missing source documents: RollTable.gbpWgQkZli1luOMi and RollTable.SOSYImI25aYkvTTv. Seven media collection gaps remain explicit. See file-audit.json, and conversion-report.json / handout-report.json inside the ZIP for individual reasons. No replacements or source edits were invented.

## Original tools blocker — resolved historical state

The following describes the initial failure, resolved by the later desktop/permissions results. The current blocker is the Oct 16 firewall modal, not missing desktop control.

The normal shell, Node REPL and CUA runtime fail before starting with `helper_unknown_error: setup refresh had errors`; CUA diagnostics additionally report `windows sandbox failed`. Read-only and workspace commands succeeded through approved shell escalation, allowing file checks and package generation. The app terminal tool reports no attached terminal session.

Read the installed Computer Use SKILL.md plus guidance and confirmation policy. Its prescribed `@oai/sky` import through Node REPL also fails during kernel initialization, before it can enumerate apps. CUA native APIs are disabled in that surface. No working screenshot/window enumeration/input surface was established. An installed Arkenforge executable does not resolve this missing control capability. No custom automation workaround was used.

Shortest recovery: restart Codex, reopen this workspace and retry Node REPL initialization / `@oai/sky` app enumeration. If the same sandbox setup error remains, repair/update the Codex local runtime through normal app support, then retry. Required capability: a working Node REPL with the installed Windows Computer Use package able to enumerate windows, capture screenshots and send input. Restart is a recovery attempt, not a guaranteed fix. Alternatively the user can perform the checklist below and provide observations/exported evidence; that remains user-observed validation.

## Original resume checklist — progress recorded below

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


## Controlled token semantics and implementation — 2026-10-16

Branch baseline: 90b721b on cursor/dynamic-lighting-c6b0, PR #8. Read this entire
log including its appended runtime results, latest STATUS milestones, README and
architecture/code before changes. Tracked tree initially clean; private untracked
source/assets/packages preserved. Enumerated windows and inspected the running
Toolkit before acting. Reused existing validation maps and Stoker assets, saved
the isolated combined map before switching, and did not restart setup. Toolkit
version displayed: **v0.5.1.18**; launcher previously observed v7.0.0.3.

### Observed control sequence

All changes below concern **ForgeBridge Runtime 2026-10-15 Fresh Manor 2nd** and
its manually imported Stoker_token_1, not automatic token migration. Native saved
files were copied read-only into local control snapshots before/after controlled
changes. These are saved native-file snapshots, not a claim that Toolkit's export
wizard was used. Screenshots were inspected through Windows Computer Use.

1. PASS — Opened the existing fresh manor after the preceding Toolkit restart;
   manor, Stoker and covered GM appearance were present. This establishes initial
   token/map existence after that restart, not persistence of subsequent changes.
2. PASS — Inspected note **Size → Object size: 1 squares**. Changed only Size to
   2, then saved note and map. Stoker visibly doubled around its fixed center.
   `_squareSizeNew` changed 1→2. Native center remained (53.62068,-41.15851).
   Transforms showed 1.024 in each scale axis (previous Size 1 display: .512).
3. PASS — Changed only Transforms X from 20.946 to 22.000. Sprite moved right;
   Size stayed 2. Saved native X changed 53.62068→56.32, Y stayed -41.15851;
   both inherited position copies agree. UI coordinate display and serialized
   coordinates differ in this configuration; source pixels are neither of these.
4. PASS — Changed only horizontal transform scale 1.024→1.5, ratio lock off.
   Sprite visibly stretched; saved native scale became (1.5,1.024), Size stayed 2,
   center stayed (56.32,-41.15851).
5. PASS — Saved, switched to the existing blank map, reopened the fresh manor,
   selected Stoker and read X=22.000, Y=-16.078, Size=2, scales=(1.024,1.024).
   Saved again for the post-reopen comparison. Movement and native Size persisted.
6. FAIL (expectation of persistent transform-only resizing) — Horizontal 1.5 was
   normalized to 1.024 on load. Controlled Size/transform isolation demonstrates
   the cause for this control. Do not interpret this as failed native Size sizing
   or a defect in preexisting converter code.
7. DEFERRED — Restart after these controlled changes, and generated-token UI
   comparison: blocked later by the firewall modal described below.

Compact snapshot evidence (SHA256 of the saved `.rwmap`):

| Snapshot | Position | Scale | SHA256 |
|---|---|---|---|
| Before | 53.62068,-41.15851 | 1,1 (old saved transform; UI normalized from Size 1) | 2d5b0c77cce8c8036b013b294315caf3870c9351886672f1574ae7f98ea4c012 |
| Size 2 saved | 53.62068,-41.15851 | 1.024,1.024 | f55c55b2fa5058cc0164b910aa48e56e27c72649d0479eab61920a4052467dc8 |
| Movement saved | 56.32,-41.15851 | 1.024,1.024 | 7623c043fabb766a2bd3781ae6e88caade4db31ba3860cfe700a56f30f4b40a3 |
| Transform saved | 56.32,-41.15851 | 1.5,1.024 | c5a5ef39be65f8f2ca607c13859668910622d963e13d8b106639d5df920c16e2 |
| Reopened/saved | 56.32,-41.15851 | 1.024,1.024 | a4f1180526866691982037827a3d79e3d76d64a5e6b1c3b29979625959636d4e |

The observed native representation is a ContentLink with Token placement enum 2,
backed by an ArkenNoteUpgrade containing ArkenNoteIcon and ArkenNoteFieldSize.
Size uses `_squareSizeNew`; duplicate inherited position/scale/rotation/hidden
fields exist. The imported 500×500 WEBP token asset uses encoded WEBP sentinel
(-2,-2,4); its thumbnail is PNG (-1,-1,4). Generated images use the already observed
PNG encoding, with the sentinel transition checked against the control blob.
This schema evidence is narrower than full actor/stat/vision semantics.

### Bounded conversion and file validation

PASS (file level) — Added foundry_tokens.py → token_ir.Token → native_tokens.py.
The source adapter subtracts explicit scene origin or padding rounded to whole
source grid cells, includes half the footprint to obtain the center, and emits
unpadded grid coordinates. The target applies explicit native origin/scale and
flips the Y axis. The native Size value separately accounts for native versus
source grid calibration. Identity is scene-qualified and retained in the note
summary/report and deterministic paths. Original control files remain byte-for-
byte dependencies, including its saved map because note metadata links back to
that map. Installation must refuse conflicts; no installation was attempted while
Toolkit remained open.

Manor source calculation: padding origin=(800,1000) source pixels; token top-left
(2000,2800), footprint1×1, grid100 ⇒ center(12.5,18.5) grids. Calibration used for
this candidate: origin(0,0), 2.56 native units/source grid and native Size grid ⇒
center(32,-47.36), native Size1. Source .8 texture scale becomes a 400×400 sprite
centered inside a 500×500 transparent canvas. This is a reported raster/resampling
approximation, not persistent transform-only scaling. Rotation is serialized with
coordinate handedness conversion but rotated orientation is runtime-unverified;
hidden serialization does not establish player behavior. Unsupported attributes,
actor links, bars, flags/scripts, sight, light and other behavior remain explicit
retained-only fields in token-report.json; full source_scene is included.

PASS — Seven new regression tests cover explicit/padded origins, finite/square
bounds, duplicate identity, retained scripts without execution, canvas alpha bounds,
separate footprint versus texture scale, non-2.56 calibration and native Size,
both inherited transform copies, deterministic complete ZIP bytes, reference
closure, unchanged control dependencies, no overwrite/name collision, unsafe
texture/archive paths, observed WEBP→PNG encoding and animated-media refusal.
Latest complete run: **136 tests, 132 passed, four WinError 1314 symlink skips**.
The first sandbox run had temporary-directory access errors; the approved-access
rerun passes. Skipped symlink checks are not counted as passed safety checks.

### Fresh geometry rebuild candidate

PASS (file preparation only) — Captured the fresh UVTT-imported saved map plus its
reachable native dependencies (8 files; no missing targets). Its saved background
center is (38.399998,-51.199997), scale(2.56,2.56), for the 3000×4000 source image
and 100-pixel source grid. Candidate calibration is upper-left(0,0), 2.56 units per
source square. UI cross-check remains DEFERRED.

Prepared fresh-calibration-candidate.zip by cloning **only FB Cal A** and its note
from the old template into a copy of this fresh saved map, at (1.28,-1.28). No old
map geometry was substituted. Existing fresh geometry records remain unchanged.
Built a separately named **ForgeBridge Fresh Combined 2026-10-16** package with
five room markers, native notes/media and PDF pages, labels off. Included the
original control map pair as dependencies to close its note metadata backlink;
existing map/note content was not rewritten. This is a file-derived candidate,
not an observed complete rebuild/import/reopen PASS.

| Artifact | SHA256 | File-only result |
|---|---|---|
| fresh-control-export.zip | c746331681a1cc0e5d7728446d761f6943e93ad9763d34a3c2d0842ffb134d57 | Eight native saved/dependency files; original snapshot preserved |
| manor-token-closed.zip | c756fa7f1104a397fe582140787771f116dbdc5d2234a7c107502e1354b031b3 | CRC passes; 14 native files parse; 15 metadata reference occurrences close |
| manor-fresh-combined.zip | b1507311c955c3b8fc896705c6c22746d7e75462bc24e2ec88d958da092de004 | CRC passes; 176 native files parse; 161 metadata reference occurrences close |

Private package/snapshot bytes remain local and untracked. The compact file audit
and synthetic fixture generator are reviewable without publishing original assets.

### Player output, fog, animation and exact current blocker

DEFERRED — Attempted **Live Play/VTT → Player screen → Enable Player Screen →
Local network streaming → Player Screen → Activate**. Projection box appeared;
Toolkit log records ArkenWebServer.exe starting. This is not an observation of
actual player output. Windows then displayed a Firewall permission modal for
**Node.js: Server-side JavaScript**, asking for public/private network access.
No access was granted. The modal's PickerHost owner is visible to tool diagnostics
but has no selectable window in list_windows/list_apps; Toolkit-targeted clicking
is rejected as another process owning the point. Toolkit-targeted Escape did not
dismiss it. User cancellation requested asynchronously. Shortest recovery: click
**Cancel** in that Windows prompt; then stop the isolated stream in Toolkit and
resume local tests. No security setting was changed or bypassed. The blocked
portion now includes further Toolkit input/restart, not just player validation.

DEFERRED — Local fog rectangle/brush reveal/hide and restart remain unobserved;
whole-map GM clear/cover evidence from Oct 15 remains scoped as such. Foundry fog
and token vision have not been converted. GM appearance and hidden flags do not
prove player behavior.

PASS (fixture preparation only) — Created original synthetic 128×128 red FB1,
blue FB2, green FB3 frames, 600ms each, as GIF and PNG sequence. GIF SHA256:
3e0c072a023c717c18b11e15f6e8e01c4a9a23e49450b79fd5be54311da48f8d.
DEFERRED — Import, playback, positioning and persistence, due to modal. No source
animated media was found; Foundry torch/ghost procedural light configurations
remain retained separately and are not claimed as animated media conversion.

DEFERRED — Complete all-five-marker/navigation/table/image/17-PDF-page runtime
checks, opaque wall/door blocking, fireplace illumination, moved-light alignment,
new token import and save/switch/reopen/restart, and fresh combined-map runtime.
These are unfinished tests; desktop permissions are otherwise working. Labels
stay off/deferred. Two unresolved source table UUIDs and seven media gaps remain
as listed earlier; no replacements invented and no imported scripts executed.
