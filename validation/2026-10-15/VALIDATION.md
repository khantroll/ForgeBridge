# ForgeBridge validation — 2026-10-15

## Scope and initial inspection

Branch: `cursor/dynamic-lighting-c6b0`. Tracked working tree was clean on arrival. Existing untracked manor module, images, token assets, companions, UVTT files, templates and prior ZIPs were preserved. No AGENTS.md was found in the workspace or its checked ancestors. Read README.md, STATUS.md, architecture, fixture notes, Arkenforge research and UVTT compatibility notes; inspected CLI, package/map/media code and tests before edits.

This log distinguishes **file-level checks** from **observations inside Arkenforge**. Current-build Arkenforge observations began after desktop and launcher permissions were repaired, as recorded below. The summary includes October 18: profile GM persistence is accepted, desktop input works without elevation, and the controlled player-output comparison below remains incomplete for generated-token visibility. Earlier user confirmations remain regression cases, not current PASS evidence.

## Results

| Status | Check | Evidence / limit |
|---|---|---|
| PASS | Automated checks | Latest full run: 144 tests, 140 passed, four Windows symlink checks skipped (66.104s); ../2026-10-18/resume-full-tests.txt. Includes scene identity/calibration and isolation regression. |
| DEFERRED | Four symlink safety checks | WinError 1314 skips are not passed symlink protection checks. |
| PASS | Fresh source export and original separate package, file level | Original ZIP SHA256 c6ea282ae220f9eb7e9bf13905e1689668cd16d11356dae14507c3f9cfd2c3c1. Five markers, 46 notes, 36 attachments including 17 PDF pages. 170 native files parse; 154 metadata reference occurrences close. |
| PASS | Source/template preservation, file level | Source scene retained, original template media byte-identical; original campaigns/source assets and unrelated local files preserved. Two missing tables and seven media gaps remain explicit. Labels off. |
| PASS | Desktop control and launcher | Original sandbox/launcher blockers resolved. Toolkit v0.5.1.18 observed and controlled through Windows Computer Use. |
| PASS | Fresh UVTT import and map existence | Fresh manor image/barrier/door/light overlays render; separate map and manual Stoker survive map switch/reopen. Fresh map reopened after the preceding Toolkit restart. These observations do not pass blocking behavior. |
| PASS | Manual token Size/movement through reopen | Size 1→2 visibly doubles Stoker around fixed center. Numeric X move persists after save→blank→reopen. Details and native comparison hashes in Oct 16 section. |
| FAIL | Transform-only token scale persistence | Horizontal 1.5 saves but normalizes to 1.024 on reopen while Size remains 2. Causal control confirms Size normalization; this is not a converter defect. |
| PASS | Bounded token writer and generated tokens | Source adapter→Token IR→native target. Prior Stoker Size/placement/movement/restart pass retained. New combined scene: five unique generated tokens; asymmetric rotations and visible→hidden→visible observed in actual player output through save/reopen/restart. Details below. |
| PASS | Sample current-package notes/image after restart | Conservatory marker, Journal and First Floor navigation; Counts Manor 1st key image visibly displays. Scope is these samples only. |
| PASS | Fresh combined notes, representative table and PDF pages | All five room links, journal/source index order, Despair rolls (1 and 3), and all 17 PDF page images observed across this follow-up. Ismark enlarged preview readable. Older combined-map exhaustive regression remains separate and incomplete. |
| PASS | Native whole-map fog and actual player stream | After user firewall approval, browser player output shows black fog-covered output, then visible map/grid after Clear all fog. Earlier covered state persists through map switch/reopen. This does not establish bounded local fog persistence. |
| DEFERRED | Bounded local fog reveal/hide and restart | Rectangle/brush attempts did not establish a visible local change. Tool drag/input limitation remains possible; not established as a Toolkit defect. Player output is available. |
| PASS | Targeted fresh wall/door blocking and moved lights | Multi Scene: single Library light moved numerically X12→14→16; illumination follows. With temporary white light at (16,-6.5), opaque wall cuts illumination and Secret Room door close/open removes/restores transmitted light. GM observation; no all-door or player blocking claim. Temporary edits discarded. |
| PASS | Fresh-map combined candidate, scoped runtime | Newly imported saved geometry; 176 native files parse, 161 metadata references close. Map loads, FB Cal A reads (.5,-.5), all five markers activate correct notes, journal index displays source order, and Strahd PDF handout displays. Saved map switches away and reopens. Full behavioral regression remains incomplete. |
| PASS | Native GIF import, playback, movement and restart | Synthetic GIF visibly changes colors at X-1,Y0; save→switch→reopen and full Toolkit restart retain playback, scale1 and FPS2. No automatic Foundry animation conversion claimed. |
| FAIL | PNG-sequence test attempts | Both filename-list and visibly selected three-file imports save one frame, not a playable sequence. Cause/workflow unresolved; separate from successful GIF import. |
| PASS | Coherent rebuilt scene, scoped runtime | Production builder combines genuinely fresh UVTT-imported geometry, markers, notes/media and five tokens in one map. Loading, token player output and restart pass; targeted lighting/blocking pass. Local fog remains deferred; prior PDF/GIF checks were not needlessly repeated. |
| PASS | Two real scene profiles, file-only | Manor 1 token and Crypt 9 tokens/1 rejection; 529 metadata references close; isolated scopes, no install conflicts. See Oct 17 section. |
| PASS | New profile GM switching/persistence, representative | Oct 18: both maps load/save/reopen through full Toolkit restart; Manor Stoker/Upper Hall and Crypt Swarm/Wight/Storage Area checked. Scope below. |
| PASS | Resume generated-token identity/Size, GM only | Correct inside-Manor Stoker explicitly selected: Size1, UI12.500/-18.500, rotation0, scales.512/.512. No edits; separate screenshots below. Both profile preflights and saved-file audit pass again. |
| PASS | Controlled native player baseline, scoped | Oct 18 native control (two yellow tiles and Bobbie), Multi Scene and Manor render through the same local browser output. Not a generated-token visibility pass. |
| PASS | Profile Manor generated-token initial visible→hidden | Working Waterfox stream: small inside Stoker visible then absent after explicit Toggle hidden; outside manual control remains visible. No restoration/restart PASS; subsequent capture blocker below. |
| BLOCKED | New profile actual generated-token player visibility/restart | Crypt remains black after bounded fog-off/camera-follow comparisons. Manor visibility experiment selected preserved manual Stoker, excluded from generated-token evidence. Prior player evidence remains separate. |
| DEFERRED | Labels | Remain off by request; player-facing behavior untested. |

## Explicit source gaps

The conversion report has no source read errors. Two table UUIDs remain missing source documents: RollTable.gbpWgQkZli1luOMi and RollTable.SOSYImI25aYkvTTv. Seven media collection gaps remain explicit. See file-audit.json, and conversion-report.json / handout-report.json inside the ZIP for individual reasons. No replacements or source edits were invented.

## Original tools blocker — resolved historical state

The following describes the initial failure, resolved by the later desktop/permissions results. The subsequent firewall modal was resolved by the user's approval; desktop control and actual player output now work.

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

## Firewall approved; resumed runtime — 2026-10-16

This follow-up supersedes the firewall blocker above. Enumerated current windows
before acting; the modal was gone following the user's approval. Used Windows
Computer Use and Toolkit **v0.5.1.18**, launcher **7.0.0.3**. No firewall settings
were changed by the agent.

### Player stream and fog

PASS (actual player output) — Settings → Display → Active extended screens →
Player Screen → Stream settings exposes a local address. Opened that address in
the in-app browser and clicked Start Streaming. Observed black output with
Toolkit's "Fog of war is active" text. Clicked Clear all fog in the isolated
fresh manor; actual browser output changed to the projected grass/grid and manor
image. This is player-output evidence, not inferred GM appearance.

DEFERRED — Local erase/paint brush and rectangle drags did not produce a clearly
bounded reveal/hide patch. Edit-history increments alone are not evidence. The
input tool has no configurable hold duration; Unity canvas drags also failed to
move UI panels. Do not diagnose a native fog bug or claim Foundry fog/token-vision
conversion. Local persistence/player rendering still require a successful bounded
control change.

### Safe runtime installation and generated token

PASS (installation/file checks) — Refreshed only the original-control map pair
inside the install ZIPs to match the newly saved local control. Generated map,
token/note/media payloads were unchanged. Preflight found zero conflicting native
files: token ZIP 6 absent/8 identical; fresh combined ZIP 94 absent/82 identical.
With Toolkit closed, installed **100 absent files only**, using exclusive creates;
identical existing files were skipped. No existing campaign/asset/note overwritten.
Reports and source PDFs remain outside MyAssets. Local package bytes are private.

| Installed package | SHA256 | File checks |
|---|---|---|
| runtime-token-install.zip | 257f08a197aa00a5e1886b9e9f9a377a2ddc4a02c8650dd0c68252a20d69926d | 14 native files parse; 15 metadata references close |
| runtime-fresh-install.zip | 4d49c52d88b65ce716db85e75527569b4a1c823dc58ac425d629cd2c48b8671d | 176 native files parse; 161 metadata references close |

PASS (runtime) — Opened **ForgeBridge Token Slice 2026-10-16**. Generated Stoker
displays a native token note with the correct dog texture and **Size 1**. UI
Transforms reads **X12.500,Y-18.500, scale .512,.512, rotation 0**, matching the
padded source's grid center and calibrated native (32,-47.36). Manual Size-2
control remains separate and visibly larger. Generated texture has the expected
centered .8 image scale baked into its canvas; this is raster approximation, not
independently persistent sprite-transform resizing.

PASS (runtime) — Changed only generated Stoker X to **13.5**; sprite moves one
grid square right, Size stays 1. Saved, switched to the isolated Blank map and
reopened: X13.5,Y-18.5,.512,.512 and Size1 persist. Closed Toolkit with save,
restarted through launcher and reopened; the same fields, texture and moved
sprite persist. Manual control in the candidate also reads Size2, X22,Y-16.078,
scale1.024,1.024 after restart. Hidden player behavior and rotated orientation
remain DEFERRED. A loose-image import was not used as evidence of token migration.

Saved token-map SHA256 **cb89ac912b598a65a5252d024875e92d83faa464118d7c677afaf6b083b91134**.
File inspection corroborates generated native X34.559998,Y-47.360001 and both
scales .512000024. Runtime evidence is the UI sequence above, not this hash.

Restart recovery note: launcher initially retained a stale Running indicator.
Direct EXE launch returned E02 (launcher required); its empty error session later
closed with Alt+F4. Refreshed launcher and launched normally. No application
validation was performed in the E02 session and no licensing bypass attempted.

### Fresh combined-map observations

PASS (scoped runtime) — **ForgeBridge Fresh Combined 2026-10-16** loads. FB Cal A
is centered half a grid square from the upper-left background edge and Transforms
reads **(.500,-.500)**, agreeing with the candidate calibration. All five room
markers select the correct native targets and Activate content link displays:
Library, Conservatory, Upper Hall, Secret Room, Servant's Quarters. Library →
2. Manor opens the ordered page list (First Floor through Approach the Manor;
Second Floor precedes Upper Hall/Servant's Quarters/Library/Secret Room/Conservatory).
Secret Room → Letter - To Count from Strahd opens its PDF note and visibly renders
Page1of1. This is one observed PDF page, not a pass for all17.

PASS (save/switch/reopen, limited) — Saved combined map, switched to Blank,
reopened; map/calibration marker render. Saved map SHA256
**9bb7582719689c43b686c526686bc85f1296fb028d1936eb4f658450e9d88cc8**.
All-five checks here apply to the fresh combined candidate; the older combined
package still has only the previously recorded Conservatory/image sample.

PASS (scoped fireplace runtime) — Manually ungrouped imported UVTT objects on the
fresh combined test map. At the native night preset, disabling Library fireplace
light (UI radius3.56, intensity100) visibly removes illumination from adjacent
floor/furnishings; re-enabling restores it. Night view also shows wall-cast shadow
wedges. Opaque-wall/door isolation remains incomplete, so the overlays/shadows are
not a full blocking PASS.

DEFERRED (movement test) — First numeric X12→10 moved the selected light outside
the west wall and removed its interior contribution. A second numeric edit
unexpectedly selected/transformed all content. This invalidates a clean alignment
comparison; no converter change is justified. Switched away without saving those
experiments; the explicit combined saved-map hash remains unchanged. A newer
experiment autosave may exist: choose **No** to "load more recent autosave" when
restoring the baseline. Temporary F6 camera focus binding and its newly created
Profile1 were removed; native Default hotkey profile restored.

### Animated media capability, separate from conversion

FAIL (test attempts, cause unresolved) — PNG sequence import with three quoted
paths produced one frame. Retried with three visibly highlighted files in a
PNG-only directory: again saved one frame (ForgeBridgeSignal-03). Both controls
remain on the isolated Blank map; second object moved to X2,Y0 and retained that
position after restart. This does not prove working animation playback.

PASS (native GIF import/playback/position) — Quick Import → Import as map asset
accepts the identified synthetic forgebridge-signal.gif (hash above), displays
GIF Complete, and creates a separate animated object. Observed red FB1, blue FB2
and green FB3 at a fixed center; moved X0→-1,Y0 and the playing image follows.
Set native FPS2. Saved data has three frames; this corroborates the observed
playback, rather than replacing it. Save→fresh combined→Blank reopen resumes
visible color changes at X-1. GIF restart remains pending. Native import defaults
to FPS30; source GIF frame durations are not automatically preserved by this UI
workflow. ForgeBridge animated-media writer remains unimplemented. Foundry
torch/ghost procedural light configurations stay separate, retained and unmapped.

Audit: `audit_runtime_files.py` checks installed ZIP CRC/native parsing/reference
closure and saved-map token/frame fields, producing `runtime-file-audit.json`.
It explicitly makes no runtime PASS claims. No converter code changed during
this runtime follow-up; existing 136-test result remains 132 pass/4 symlink skips.

### Resume checkpoint: restart and complete PDF display (2026-10-16)

PASS — Enumerated windows and inspected the existing Blank animation map before
acting. Midday had completed to 12.00. Closed Toolkit normally, verified its window
was absent, refreshed the stale launcher and launched Toolkit v0.5.1.18 normally.
Opened Blank: GIF visibly changes red/blue/green; Animation reads FPS2 and frame3,
Transforms X-1.000,Y0.000,scale1.000 on both axes. This closes GIF restart playback
and placement. It remains a manual native-media capability, not conversion.

PASS — Opened Fresh Combined after restart, declining the newer experimental
autosave. The saved manor/calibration content loads. Start Here shows room order
Upper Hall, Servant's Quarters, Library, Secret Room, Conservatory. Opened PDF
Handouts through its linked-document index, then individual note links. Observed
all 17 page images across this follow-up (Strahd was observed before restart):

| PDF handout | Pages displayed in order | Result |
|---|---|---|
| Letter to Count from Dr Seward | 1/1 | PASS |
| Letter to Count from Strahd | 1/1 (earlier in this follow-up) | PASS |
| Letter to Strahd from Elizabeth | 1/1 | PASS |
| Letter to Margret | 1/1 | PASS |
| Dr Seward's note | 1/1 | PASS |
| Night of Darkness | 1/1 | PASS |
| Arcane Tome of Knowledge | 1/2,2/2 | PASS |
| Count's Journal | 1/2,2/2 | PASS |
| Court of Ravenloft | 1/6 through 6/6, scroll track to later pages | PASS |
| Letter to Ismark | 1/1; enlarged image preview readable | PASS |

These are native UI rendering/order observations, not exhaustive transcription
or every-page enlarged readability/player sharing checks. No original PDFs or
user notes edited. The older combined-map exhaustive regression is still distinct.

PASS — Start Here → Despair opens native rollable table with retained unresolved
media reference. Roll returned Value1/Apathy, then Value3/Insane, displaying the
corresponding source text. This is the representative current-package roll check;
missing source table/media references remain explicit.

FAIL → FIXED (generated wording, file level) — Native Start Here incorrectly said
"Map markers are not placed automatically" in the combined map package. The media
note stage lost the map-marker context when replacing text-only notes. Threaded
that context through the native image-note writer; standalone exports retain the
default. Package regression decodes actual serialized note text and asserts the
combined wording. Four package and six native-image tests pass after the fix.
Installed packages were not overwritten; this text correction applies to new
builds. No token/geometry schema changed.

Automated rerun before the wording fix: 136 tests,132 pass,4 symlink skips with
approved temp-directory access (47.951s). Sandbox attempt had 74 temp permission
errors, not converter failures. Skips still do not pass symlink protection checks.

PASS (new-build file checks only) — Built separately named **ForgeBridge Fresh
Wording Check 2026-10-16** using the fresh calibrated template, original source,
same 2.56 calibration, PDF pages enabled and labels off. Added the preserved
control-map pair to close its existing note backlink, as for the earlier fresh
candidate. CRC passes; 176 native files parse; 161 metadata references close.
Decoded native text contains the corrected marker wording. ZIP SHA256
**869ca9b971aaeb295f73a872ea63e52b88827ce34ea2bdf2540d04ec4f0a0873**.
It is **not installed or runtime-tested**; installed package hashes above remain
the runtime evidence. Compact `wording-package-audit.json` records this scope.

DEFERRED — Another bounded fog attempt on Fresh Combined: erase point and
polygon-selection clicks yielded history increments/zero-size indication without
an observed bounded reveal. Escaped the brush and switched to Blank without
saving this experiment. Reliable canvas press/drag behavior remains uncertain;
the available API has no hold-duration control. This does not establish a Toolkit
or converter defect. Shortest independent control is one deliberate human bounded
reveal/hide on the isolated map, followed by save/switch/reopen/restart and actual
player checks. Desktop and firewall access themselves are working.

Still DEFERRED: opaque wall and door blocking isolation, moved-light alignment,
bounded local fog persistence/player output, rotated-token orientation and hidden
token player output, plus exhaustive older combined-map regression. Labels stay
off. Native animated-media conversion is unimplemented. Next token implementation
milestone is a calibrated per-scene token set after rotation/hidden controls.

### Combined multi-token milestone — 2026-10-16, after cf50ebf

Resumed the existing Toolkit window and actual browser player stream; no setup
restart or older PDF/GIF repetition. Toolkit **0.5.1.18**, launcher **7.0.0.3**.
Original module/campaigns/notes and unrelated untracked assets preserved. The
fixture script copies the source to a private directory before adding test tokens.

PASS (implementation/file level) — `forgebridge.package` now composes the existing
source adapter → Token IR → native writer into the same map as geometry, five
room markers, 46 notes and 36 image attachments including 17 PDF pages. Separate
marker/token control exports are supported without replacing the geometry map.
Production code preserves original map/metadata backlink dependencies, merges
identical controls, rejects conflicting content, and checks metadata closure.
No manual ZIP surgery or installed dependency patching is required.

FAIL → FIXED (file-level preflight) — Initial candidate reused the standalone
Stoker token-note path, conflicting with its previously edited installed note.
Nothing was overwritten. Generated token paths now include the output-map
namespace plus source identity. Final preflight: 114 absent files, 80 identical
dependencies, zero conflicts. Installed only the 114 absent files with Toolkit
closed. Later Toolkit edits are never silently overwritten by rebuilding.

Final package: `2026-10-16/multi-runtime-private/scene-v2.zip`, SHA256
**9c9cc84a5a514065e8321a0dcc406dd5aa1fe8281c7abaa9f4ace0253ca5d5f8**.
Map: **ForgeBridge Multi Scene 2026-10-16**. `multi-runtime-audit.json` records
194 native files parsed, ZIP CRC success, 195 closed metadata-reference
occurrences and exactly one active instance for each of five unique token targets
and UIDs. These are file checks, not runtime PASS evidence.

The geometry is from the genuinely fresh UVTT-imported and calibrated saved map,
read with its native dependency closure. The older `MyAssets(1).zip` supplies only
the room-marker control schema. Calibration is explicitly 2.56 native units per
source square here and 2.56 per native Size square; origin (0,0), source padding
(800,1000) pixels and 100-pixel grid are applied. Tests also exercise native units
3 with origin (7,11); 2.56 is not universal. Original Stoker remains Size1 with
texture .8; its previously passed movement map at X13.5 was not edited.

PASS (multi-token runtime and player output) — Original Stoker plus four instances
of one original asymmetric arrow texture appear once each. Texture SHA256:
**66a0b944694d2a7007fb414893b9155de362a9a715e0dea06eb1372920a375d7**.
The arrow has a red up tip, blue left wing and green lower-right dot. Source
center positions are (2,2), (5,2), (8,2), (11,2); clockwise rotations 0,90,180,270;
Sizes 1,1,2,.5. GM renders up/right/down/left with the larger down token hidden.
Actual player stream renders up/right/left and omits the down token. Selected
FB Arrow90 alone; native Hidden toggle removes it from actual player output,
then toggling back restores the same orientation/center. Clicking the down
token's native eye badge revealed it directly; actual player output showed the
larger down arrow. Re-hid it and saved the source-hidden state.

PASS (persistence) — Save → Blank → reopen retains the orientations, relative
sizes and hidden badge; actual player output again shows only up/right/left.
Exited Toolkit normally, verified its window absent, refreshed the stale launcher,
started Toolkit, opened Multi Scene and reactivated native player streaming.
After reconnecting the browser, actual output again shows up/right/left with the
down token absent. Mirror-DM and simulated-player modes were off. This is actual
stream observation, not inference from a GM flag. The native hidden→visible→hidden
round trip leaves source flags restored; the visible token also completed
visible→hidden→visible before saving.

PASS (targeted content regression on Multi Scene) — After restoring the saved
baseline and declining the experimental autosave, double-clicked Library marker:
it opens **2. Manor — Library**, with the Journal backlink and source page text/
document links visible. Prior all-five room order, table and 17 PDF observations
remain the broader content evidence; this sample checks composition with tokens.

PASS (supporting file comparison) — `audit_saved_multi.py` compares the generated
and saved active token records. All five names, UIDs, positions, rotations, scales
and hidden states are equal; `saved-multi-audit.json` records the values. Saved map
SHA256 **9f704435b385c3e4bac645bba994fd89554ff01c2d1ec5da47ebe40fb451e6b6**.
Intermediate visibility edits were observed live, not exported as separate files.

PASS (explicit partial conversion) — Eight source entries yield five supported
tokens and three rejection records: rectangular footprint, missing texture,
duplicate source identity. Missing-texture resolution formerly escaped as
InventoryFatal and aborted the scene; it is now reported per token while valid
tokens continue. Repeated textures retain distinct token names/identities/native
references. Full source scene and unsupported actor/vision/behavior fields stay
in reports. No actor/stat-block conversion, imported script execution or invented
media/table replacement was added.

PASS (targeted current fresh geometry, GM runtime) — Manually ungrouped the
82 imported UVTT objects on Multi Scene, cleared group selection and confirmed
only one Light Source selected (no +81). At native midnight, original Library
light radius3.56/intensity100 moves X12→14→16 at Y-7.5 through focused numeric
fields; illumination moves with its icon while walls/background/tokens stay fixed.
The contribution switches across the opaque Library partition. For an unambiguous
door comparison moved this same light to (16,-6.5), temporarily changed its dark
source color #575112 to white, and toggled the Secret Room doorway at screen
(1276,536) at 100% zoom. Open/green: a light wedge enters Secret Room; closed/red:
the wedge disappears; reopening restores it. White illumination terminates at the
adjacent opaque wall. This validates targeted blocking geometry with a manually
controlled light, not automatic white-color conversion or every door/player
blocking. Earlier current fresh-map fireplace on/off check remains its separate
PASS. Switched to Blank and explicitly declined saving these experiments; saved
Multi Scene baseline retained. Temporary F6/Profile1 removed; Default restored.

DEFERRED (bounded fog) — The previous materially different polygon attempt also
failed to establish a bounded reveal. No more inconclusive gestures repeated.
Exact short human control needed on the isolated map: Live Play/VTT → Fog of war,
manual erase rectangle, press/hold at one corner, drag and release at the opposite
corner; paint a smaller subsection back. Observe actual player output, then save,
switch/reopen and restart. The available Windows drag API has no hold-duration
option, and reliable Toolkit gesture timing is unresolved. Whole-map clear/cover
and actual player access already work. Foundry fog/token vision conversion remains
unimplemented regardless of this manual native control result.

PASS (automated) — 137 run, 133 passed, four WinError1314 symlink tests skipped;
175.388s, `multi-tests-final.txt`. Standalone token ZIP regression now covers three
tokens sharing a texture, supported sizes, unique references/UIDs, mixed rejection
and deterministic bytes. Combined regression decodes the same output map to check
existing objects plus room marker plus tokens, calibration, hidden/rotation fields,
original dependencies and missing-backlink rejection without partial output.
Skipped symlink tests do not establish symlink safety PASS. `git diff --check`
passes. Prior 17-page PDF and GIF restart observations remain scoped evidence.

Remaining manual steps: native UVTT import/export and coordinate calibration,
reviewed installation without conflicting overwrites, ungroup for individual
geometry edits, GIF import/FPS setup, and the bounded fog control above. Labels
stay off. Procedural light animation stays retained separately. Next concrete
implementation milestone: make the calibrated native-control/dependency workflow
a reusable scene profile with multi-scene token identity isolation tests; continue
bounded fog/vision capability research before adding a target mapping.


## Calibrated scene profiles — 2026-10-17

PASS (automated): 144 run, 140 passed, four Windows symlink tests skipped;
168.925s, `../2026-10-16/profile-full-tests.txt`. Skips do not establish safety PASS.
Seven new profile cases cover two isolated scenes with repeated token IDs/names
and shared textures, distinct padding/grid/origin/units, mixed rejections, zero
source tokens, closed dependencies, stable rebuilds, existing-output rejection and
preservation of a second package/user edits. Exact Adventure selectors resolve
ambiguous source IDs. Explicit primary geometry selection preserves backlink maps;
changing it requires matching calibration binding. Input/identity/hash mismatches
fail actionably. Legacy explicit CLI remains available; only output name, note
namespace, PDF choice and destination may override a profile.

PASS (file-only): real Manor and Crypt profile preflights/builds and pair audit.
Profiles pin source package `lob-counts_manor-pk-v13`, `packs/adventure-5e`, parent
Adventure `N63YevXMYeDZPCMh`, plus each matching companion and existing calibrated
native export. Origin (0,0), units/source grid 2.56 are bound to these specific
exports, not a universal constant. Native Size calibration is separately recorded.
Both preserve existing map content and dependency backlinks; controls do not supply
another scene's primary geometry. Profile/input hashes establish provenance only.
PDF page generation is disabled for this focused demonstration; existing completed
17-page PDF/GIF/blocking checks were not repeated. Source gaps stay in reports.

- manor: `ForgeBridge Profile Manor 2026-10-16`, scene `d0XKyRuR4GqdOagf`; 1 generated tokens, 0 rejected. Package SHA256 `14943c23d112c6bc25fd5a09a1e545b310d89d7d2a957372a7d1d04f32ecdf1c`.

- crypt: `ForgeBridge Profile Crypt 2026-10-16`, scene `fP7VKkP46gQPED6X`; 9 generated tokens, 1 rejected. Package SHA256 `3fdc4ba06e4d7469f9e8f51178e4e53e832c29663efd7b9df212263354b68b5c`.

PASS (file-only coexistence): 529 metadata references close across both packages;
token, note and media scopes differ. Eight shared native control/dependency files
are byte-identical. Installation review found 438 new files, 20 identical, zero
conflicts. A separate explicit runtime-install operation, while Toolkit was closed,
added only absent files with exclusive creation; no existing files were overwritten.
Build/preflight never installs content or changes settings. See pair audit JSON.
Crypt rejects one token whose texture scale is unsupported; no replacement invented.

BLOCKED (new runtime outputs): Toolkit v0.5.1.18 is the installed/tested baseline;
launcher v7.0.0.3. Enumerated current windows before acting; Toolkit was closed.
After reviewed installation, refreshed official launcher, but desktop activation/
capture recovery twice failed with `foreground window did not report a process id`.
No claim that either new profile map opened or persisted inside Toolkit. Short next
step after helper recovery: open `ForgeBridge Profile Manor 2026-10-16`, inspect
Stoker and a room link, save; switch to `ForgeBridge Profile Crypt 2026-10-16`, inspect
a generated token and room link, save; switch/reopen both and confirm persistence.
Accepted prior multi-token rotation/visibility/restart results remain historical
current-converter evidence, not a runtime PASS for these new outputs.

DEFERRED: bounded native fog human erase-rectangle press/hold/drag/release, paint
smaller subsection back, observe player output and persistence. Foundry fog/vision
conversion remains unsupported separately. GIF import/FPS is manual; procedural
light animation retained separately; actors/stat/combat behavior unmapped; labels off.
Original campaigns/assets and manually edited notes preserved. Profile capture and
preflight/build are repeatable; native import/export/calibration and reviewed
installation remain manual. Next runtime task is the two-map persistence check;
next implementation milestone is portable capture/export tooling with reviewed
native dependencies.


## Profile runtime recovery attempt — 2026-10-17, after 39c163f

BLOCKED (desktop control, cause unconfirmed; not a conversion failure). Followed
installed Computer Use guidance and selected the already-running Toolkit from a
fresh `sky.list_windows()` result. Enumeration succeeded and returned exactly one
MastersToolkit window: id 6881588, app
`process:C:\Program Files (x86)\MastersToolkit\MastersToolkit.exe`.
`sky.get_window({id:6881588,app:discovered_app})` succeeded. The first capture,
`sky.get_window_state({window:toolkitWindow,include_screenshot:true,include_text:false})`,
failed before input with Error: `foreground window did not report a process id`.
No Toolkit retry, launcher activation, click, key input, rebuild, installation,
permission change or application elevation was performed.

One comparison used the same enumeration's ordinary File Explorer window, id
199770, app `process:C:\Windows\explorer.exe`. `get_window` and
`get_window_state` returned without error. However the returned screenshots showed
Toolkit and an overlapping Codex window, not a clearly identifiable Explorer
surface. Therefore the API reported capture success for another target, but
reliable ordinary-window targeting is unconfirmed. The failure cannot yet be
attributed solely to Toolkit, permissions, or ForgeBridge. No alternative automation
mechanism was introduced. Full available Error name/message/stack/properties and
target metadata are in `../2026-10-16/profile-desktop-diagnostic-2026-10-17.json`.
No additional diagnostic code/cause was exposed by the error object.

Both new profile runtime checks remain BLOCKED. Prior multi-token player-output
and restart PASS evidence remains separate; neither file hashes nor the incidental
blank-map capture proves new profile behavior. Labels remain off and bounded fog
remains separately deferred. No code change or automated rerun was justified;
latest totals remain 144 run, 140 passed, four Windows symlink tests skipped.

### Short human checklist (installed profile packages; do not rebuild/reinstall)

1. Open **ForgeBridge Profile Manor 2026-10-16**. Confirm generated **Stoker**,
   distinct from preserved manual control **Stoker_token_1**. Record its native
   position (generated baseline X32, Y-47.36), Size and visible/hidden state. Open
   one room marker and record the correct room-note title/scene. Save the map.
2. Open **ForgeBridge Profile Crypt 2026-10-16**. Confirm nine generated tokens
   (one source token was explicitly rejected; preserved control content is separate).
   Record two representative token names/positions and a correct Crypt room-note
   target. Save. Use profile-pair-audit.json for baseline names/positions; it is
   file evidence only, not observed runtime PASS.
3. Switch Manor → Crypt → Manor and reopen both. Confirm each retains its own
   generated tokens, recorded positions and room-note targets without cross-scene
   substitution. Keep labels off; avoid editing original maps/control notes.
4. Quit Toolkit normally, reopen normally, and repeat representative token and
   room-link checks on both profile maps. Record Toolkit version and results.
5. Where a token is hidden/visible, inspect the actual player screen/stream:
   confirm hidden tokens are absent and visible tokens present in the displayed
   area. Record GM and player results separately; fog/viewport can obscure tokens
   and must not be mistaken for hidden-state proof. No bounded-fog test required.

Record PASS/FAIL per map, representative names/coordinates/room titles, and whether
observations occurred before switching, after reopening and after restart. These
human observations can close the milestone; file inspection cannot replace them.
Portable capture/export tooling remains out of scope until this runtime milestone
is finished.


## Post-reboot desktop attempt — 2026-10-18

PASS (capture capability only): fresh Windows Computer Use enumeration returned
Toolkit id 524980 and launcher id 852790. Selected Toolkit with its discovered app
identifier; initial `get_window_state` returned a Toolkit v0.5.1.18 screenshot of
blank `New Map`, no modal. The prior foreground-process capture exception did not
recur. This is not a package/runtime PASS and does not establish the old cause.

BLOCKED (input effect unverified): clicked the observed open-map folder at
(1863,23), refreshed, activated the same Toolkit window and refreshed, then clicked
observed Maps at (53,401). Calls returned without error, but fresh screenshots
continued to show the blank map with no map browser/menu change. A later capture
showed the clock advance from 09:09 to 09:10, but no requested UI transition.
Accessibility reports focused `0 pane MastersToolkit`; no child controls exposed.
Asked the user whether a manual Maps click responds and matches this blank-map
capture. No additional speculative clicks, restart, rebuild or reinstall performed.
Two-map token/link/switch/restart/player checks remain unobserved, pending verified
input response. Cause unconfirmed; not a ForgeBridge conversion failure. Original
content and test maps preserved; labels off and bounded fog separately deferred.


## Input privilege investigation — 2026-10-18

PASS (diagnostic): read Windows process TokenElevation flags without changing
processes/settings. ArkenforgeLauncher PID14300 and MastersToolkit PID5932 are
elevated; Codex processes and codex-computer-use-swift PID15328 are not. All are
in session1. Toolkit's parent is the elevated launcher; launcher parent is Explorer.
Both executable embedded manifests request `asInvoker`, uiAccess=false. No matching
HKCU/HKLM AppCompatFlags/Layers entries were returned; the discovered Start Menu
shortcut has flags0x8b with run-as-user bit unset. The original elevation trigger
is not established. Sandbox process enumeration omitted desktop apps; read-only
host process inspection supplied the actual data, without elevating any app.

Reset the supported Node REPL session and reinitialized @oai/sky. Capture still
works, but one Maps click has no visible effect. Confirmed app/helper elevation
mismatch strongly explains current ignored SendInput: Windows UIPI permits input
injection only toward equal/lower integrity targets. Microsoft reference:
https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput
This does not prove the earlier foreground-process capture exception had the same
cause. No application was elevated, no Windows security setting changed, and no
alternative UI mechanism introduced. Exact recorded measurements are in
`../2026-10-18/desktop-elevation-diagnostic.json`.

BLOCKED pending controlled retest: asked human to save wanted work, close Toolkit
and launcher normally, reopen launcher without Run as administrator, then launch
Toolkit. If UAC demands elevation, stop and report it. Recheck elevation before
one capture/Maps click. Do not elevate Codex/helper or bypass UIPI as a workaround.
The profile runtime milestone remains pending until actual two-map checks finish;
no rebuild/reinstall or converter change justified. Prior results remain separate.


## Profile runtime resumed with matched privileges — 2026-10-18

PASS (desktop control diagnosis/recovery): human closed and relaunched Toolkit and
launcher normally. Read-only TokenElevation recheck: launcher PID14304=0, Toolkit
PID8656=0, helper PID15328=0, all session1. Fresh Toolkit window id1376794 captures;
a Maps click immediately opens its menu. This controlled retest supports the prior
high-target/standard-helper UIPI mismatch as the cause of ignored input. No
Windows security setting or helper elevation changed. Earlier foreground-process
capture error remains a separately unproven cause. Toolkit v0.5.1.18, launcher7.0.0.3.

PASS (observed GM runtime, scoped): opened the already-installed **ForgeBridge
Profile Manor 2026-10-16** and **ForgeBridge Profile Crypt 2026-10-16**, with no
package rebuild/reinstall. Manor Stoker selects the generated note/texture and
Transforms reads UI X12.500,Y-18.500, rotation0, scales .512/.512 (native generated
position32,-47.36). Preserved manual Stoker_token_1 is separate, outside the manor.
Upper Hall marker's Customize → Content Link → Activate content link opens
**2. Manor — Upper Hall**, with Journal link **2. Manor**. Saved Manor normally.
Crypt has its distinct background/layout and generated token targets. Wight reads
UI35.500,-11.500; Swarm of Rats35.500,-7.500, rotations0, scales.512/.512, matching
native90.88,-29.44 and90.88,-19.2. Storage Area activates **3. Crypt — Storage Area**
with Journal **3. Crypt**. Saved Crypt; switched back to Manor and reselected Stoker
at unchanged coordinates. No cross-scene replacement observed in these samples.

PASS (observed full restart, scoped): exited Toolkit via normal exit dialog,
verified Toolkit absent from window enumeration, closed/reopened the official
launcher because it retained stale Running state, then launched Toolkit normally.
New Toolkit window id1181284. Reopened Crypt: representative Swarm/Wight identities
and placements remain, and Storage Area still opens its Crypt note. Reopened Manor:
Stoker still reads12.500,-18.500, scales.512/.512, rotation0; Upper Hall still opens
the Manor note. Other older maps, PDF/GIF/blocking tests were not repeated.

Native interaction correction: clicking a hidden token's cyan eye badge reveals
it as well as exposing/selecting the token. Swarm and Wight were manually revealed
during first inspection and saved/reopened that way. This is a manual visibility
change, not a converter failure. Restored both with the explicit **Toggle hidden**
action and saved Crypt again. No token coordinate/Size edits were made. File audit
then confirms all ten generated token identities/positions/hidden flags across
both maps match their generated baselines, with no duplicates, and all five Manor
and19 Crypt room-note targets remain equal. This is supporting file evidence,
not proof of actual player visibility. See
`../2026-10-18/profile-runtime-file-audit.json` and `audit_saved_profiles.py`.
Saved map hashes: Manor
`7fed48c9544b78a56e451e4552026386d0b14b83b1c457f160e7d66edc18b5c6`;
Crypt `d08058217fd719936d6a84ce88bbb7a61f331cacd67b9a80759fd2823217f87e`.
Original package hashes remain those in profile-pair-audit.json; no regeneration.

BLOCKED (new actual player visibility): used the existing browser player page
http://192.168.1.201/ and its Start Streaming action. After Toolkit restart, enabled
local-network **Player Screen** through native UI, reloaded browser and restarted
stream. It connects but renders black with the Toolkit watermark, no identifiable
map/tokens. One wider numeric projection width120 and one temporary native fog-off
check did not establish a visible scene. Restored width27.51, native fog on,
projection-box display hidden, and stopped temporary projection. No bounded-fog
gesture, firewall change or player-visibility PASS inferred. Remaining short human
step: frame a known visible profile token in a working actual player output, compare
hidden/visible state there on both maps, then confirm after restart. Prior accepted
multi-token actual-player rotation/visibility remains distinct evidence.

Profile GM import/coexistence/switch/restart samples now PASS; the full profile
runtime milestone remains incomplete only for new actual player observations.
Labels stay off, bounded fog separately deferred, native calibration/reviewed
installation/GIF setup manual. Foundry fog/vision, procedural animation and actor
behavior remain conversion gaps. No production code change or automated rerun was
justified; latest suite remains144 run,140 passed, four Windows symlink skips.
Portable capture/export expansion remains deferred until profile runtime closes.

## Controlled player-output comparison — 2026-10-18 (after 7d701c5)

One bounded diagnostic pass; Toolkit v0.5.1.18, launcher7.0.0.3. Fresh window
inventory finds Toolkit1181284, launcher722400 and Codex66932. Capture and input
work. Read-only TokenElevation: Toolkit1856=0, launcher5644=0, helper15328=0,
all session1. No elevation, permissions change, package rebuild or installation.

Native UI created and saved **ForgeBridge Player Control 2026-10-18**: two bright
yellow Flat Colour tiles (RGB255,220,28), one visible built-in NPC Bobbie. Default
midday lighting and native fog disabled. Local network streaming → **Player Screen**
(selected explicitly, not GM Extension), physical dimensions69.8×39.3cm. Projection
width27.51 squares; box centered at native origin visibly encloses both tiles and
Bobbie. Blackout, freeze, overlay, linked object, filters, Mirror DM view and
Simulate player view all off. Browser192.168.1.201 reload → Start Streaming shows
both yellow tiles, green background/grid and Bobbie: **PASS native player baseline**.
Only monitor1 and local-network output are offered; no independent physical player
monitor was available. **DEFERRED physical-display observation**; browser evidence
must not be described as physical-display evidence.

| Observation / controlled change | Result and scope |
|---|---|
| Open saved Multi Scene using same stream, same27.51-square projection | PASS scoped rendering: northwest map/image and asymmetric arrows visible. New observation; prior full rotation/hidden/restart acceptance remains separate. Declined newer autosave to use saved baseline; no overwrite/deletion. |
| Open saved Profile Manor, same output and width | PASS scoped rendering: northwest image visible; much of manor lies outside the box. |
| Manor projection width27.51→80, then blur field | Larger viewport reaches manor and outside manual Stoker. Browser shows map and portrait. Only projection width changed. |
| Select outside portrait, explicit toolbar Toggle hidden | Portrait disappears in actual player output. **Selection error:** selected `Stoker_token_1`, the preserved manual control, not generated Stoker. This experiment is excluded from generated-token PASS. Images below document only manual-control behavior. |
| Save temporary manual-hidden state; open Crypt | GM Crypt loads; browser initially retains stale Manor frame. A stale frame is not Crypt rendering evidence. |
| Reload browser, Start Streaming on Crypt | FAIL to establish visible scene: black with Toolkit watermark. Width field120, blackout/freeze/overlay/link/filters off; fog on; Mirror DM/Simulate off. |
| Crypt native fog toggle off, no reveal gesture | GM brightens; browser still black. Does not establish local reveal/hide behavior or Foundry fog conversion. |
| Crypt Mirror DM view on, separately | Box follows current GM framing; width subsequently reads87.18. Browser still black. No claim that this tests independent player visibility semantics. |
| Inspect Crypt lighting | Time12.00; custom ambient unchecked, white swatch. No lighting value changed. Saved root data also records time.5 and white ambient. |
| Restore diagnostic state | Crypt fog on, Mirror DM off, numeric width120 restored; no Crypt save. Reopen Manor; intentionally click manual control's eye badge to restore visibility, save. Restore width27.51, hide projection box, stop projection, save Manor. No token placement/Size/rotation edits. |

**BLOCKED:** new profile generated-token visible/hidden observations and their
Toolkit restart check. No new restart attempted after the unresolved Crypt output;
accepted profile GM restart and prior Multi Scene player restart remain PASS.
The pass rules out an entirely black session at its start, but does not establish
why Crypt is black or why the earlier session was black. No production converter
change is justified by this result. In particular, native fog-off did not establish
a fix, and the stale browser frame makes map-switch output unreliable without
identifying the newly loaded scene. Stop diagnostic retries here.

Smallest human handoff: open **ForgeBridge Profile Crypt 2026-10-16**, enable local
network **Player Screen**, show its projection box, and manually position that box
over a lit Crypt room. With native fog temporarily off and blackout/freeze off,
reload the player page and press Start Streaming. Confirm the Crypt room itself
appears; report if it remains black. This is an uncompleted framing check, not a
guaranteed fix. If a separate physical player display can be connected, compare it
and the browser independently. Once visible, select generated Igor and Wight via
explicit selection controls (an eye-badge click reveals a hidden token), check
visible/hidden output, restore source states, and repeat on generated Manor Stoker
(UI12.500,-18.500, inside the manor; **not outside Stoker_token_1**) and after normal
Toolkit restart. Do not rebuild or reinstall to perform these checks.

Evidence: `../2026-10-18/player-crypt-black.jpg`,
`player-crypt-settings.jpg`, `player-manor-manual-control-visible.jpg` and
`player-manor-manual-control-hidden.jpg`. The latter two show a manual token only.
`player-saved-settings.json` is an **intermediate saved-file snapshot** (Manor
width80 before final restoration), not runtime proof. Final read-only audit
`profile-runtime-file-audit.json` passes all ten generated token identities,
positions and hidden flags plus five Manor/19 Crypt room targets. Final Manor
SHA256 `c8ab18087c35cd35ca70e341472e3fbb716be5918032e94c156fa466927003e2`;
Crypt unchanged `d08058217fd719936d6a84ce88bbb7a61f331cacd67b9a80759fd2823217f87e`.
Native control SHA256 `91589bf6df3314a929e33416e23fa4730434dba46da982e60e60a1ab0034009a`.
Original generated package hashes unchanged. No automated suite rerun justified
by evidence/docs-only changes: latest144 run,140 passed,four symlink skips (not
passed safety checks). Labels off; bounded fog/PDF/GIF tests not repeated.

## Resume verification — 2026-10-18, after 982f23d

Read the entire validation history, latest STATUS milestones, README, token
source/IR/target code, profile/build interface and regression fixtures. The bounded
writer, fresh combined multi-token package, Size/movement semantics, all-five room
links/17 PDF pages, GIF restart and targeted wall/door/light checks are already
implemented or observed as scoped above. Do not restart that completed work.
Tracked tree clean on arrival; existing unrelated untracked assets preserved.

PASS (GM-only correction): fresh enumeration finds Toolkit1181284 and launcher722400.
Capture shows Toolkit0.5.1.18 on installed Profile Manor, projection disabled,
width27.51, fog on. Used Selection to choose **Stoker inside the manor**, not the
preserved outside manual **Stoker_token_1**. Transforms: X12.500,Y-18.500,
rotation0, horizontal/vertical.512. Customize → Content Link names Stoker; Activate
opens its native note with **Size1** and correct dog image. No field, hidden flag,
Size, coordinate or rotation changed. Closed note without editing; no map save,
rebuild, reinstall or restart needed for this identity correction. Evidence:
`../2026-10-18/resume-generated-stoker-transforms.jpg` and
`../2026-10-18/resume-generated-stoker-size.jpg`. This is not actual-player evidence.

PASS (automated regression):144 run,140 passed,four Windows symlink skips,
66.104s; `resume-full-tests.txt`. Existing tests cover deterministic token output,
padding/grid/calibration/Size, inherited fields, mixed rejection, shared textures,
unique references, preservation, dependency closure and two-scene isolation.
No conversion implementation changed, so no redundant tests were added. Skipped
Windows symlink tests remain DEFERRED safety coverage, never counted as passes.

PASS (read-only files): both existing real profiles pass input identity/hash,
control and dependency preflight again. `resume-manor-preflight.json` and
`resume-crypt-preflight.json` explicitly scope their result as preflight only.
Initial default-temp attempts hit sandbox WinError5 before completing input reads;
reran with TEMP/TMP pointing at workspace `.test-tmp`, as for the passing full
suite. No permission change or application elevation. This was an environment
access failure, not a conversion failure. Both preflights are read-only and build
no packages. Existing package hashes unchanged: Manor
`14943c23d112c6bc25fd5a09a1e545b310d89d7d2a957372a7d1d04f32ecdf1c`;
Crypt `3fdc4ba06e4d7469f9e8f51178e4e53e832c29663efd7b9df212263354b68b5c`.
Reran saved-map audit: all ten generated token identity/position/hidden states and
all24 room targets match; saved hashes remain Manor
`c8ab18087c35cd35ca70e341472e3fbb716be5918032e94c156fa466927003e2` and
Crypt `d08058217fd719936d6a84ce88bbb7a61f331cacd67b9a80759fd2823217f87e`.
`resume-verification.json` records compact scopes/hashes. File evidence does not
replace runtime behavior.

BLOCKED remains new profile generated-token actual-player visibility/restart.
The previous controlled pass explicitly ended diagnostic retries pending human
Crypt projection framing; no new human observation has been supplied. Preserved
that boundary instead of repeating black-output attempts. DEFERRED remains bounded
native fog: human erase-rectangle press/hold/drag/release, paint a smaller region,
then save/switch/reopen/restart and observe actual player output. These are separate
manual native controls; Foundry fog/vision conversion remains unsupported. Exact
handoffs above remain current. No PDF/GIF/blocking or inconclusive fog gestures
repeated. Accepted GM/profile and earlier Multi Scene player results retained.

Automatic scope now: source adapter → Token IR → target writer packages supported
static square tokens (identity/name/texture/calibrated center/footprint/rotation/
hidden; reported raster texture-scale approximation) with calibrated geometry,
room markers, linked notes/tables and supported image/PDF attachments. Native
import/export/calibration and reviewed installation are manual; GIF import/FPS,
ungrouping individual geometry and bounded native fog are manual too. Unsupported
actor/stat/vision/behavior and procedural animation stay retained/reported, source
table/media gaps explicit, labels off. UVTT is an interchange path, not a capability
ceiling. Next concrete gate is the two-profile visible/hidden player/restart check;
after that, portable native-control/dependency capture is the next implementation
milestone. No new converter defect was reproduced in this resume.

## Working player setup; generated Manor visibility — 2026-10-18, after a305efc

User supplied the follow-up instruction to inspect the working setup and finish
both profile player/restart checks. Enumerated Toolkit1181284, Waterfox68092,
launcher722400; Toolkit v0.5.1.18. Initial Toolkit capture succeeds: current map
is Profile Manor (not Crypt), generated Stoker already selected inside the lit
room, zoom80%, native fog off, projection active and displayed, width27.51,
blackout/freeze/overlay/link/filters/Mirror DM/Simulate off. The human-positioned
projection now encloses the room and both Stoker objects. No settings changed.

PASS (initial actual-player observation only): Waterfox was minimized; activated
its discovered window and captured it. Browser192.168.1.201 displays the Manor
room, small generated Stoker at its inside southwest corner, and larger manual
Stoker outside east. Explicitly activated Toolkit and used selected generated
Stoker's toolbar **Toggle hidden**. GM shows cyan eye on the small token. Activated
Waterfox for an unobstructed fresh capture: small generated Stoker is absent,
while larger manual Stoker and room remain visible. These identify the correct
scene and distinguish the generated token from the previous wrong manual control.
Evidence: `../2026-10-18/profile-manor-player-visible.jpg` and
`../2026-10-18/profile-manor-player-hidden.jpg`.

BLOCKED (capture, not conversion): while returning to Toolkit to restore the
selected token, activate/capture reports **FrameArrived timed out: timed out waiting
on channel**. One fresh `sky.list_windows()` succeeds with same Toolkit1181284,
Waterfox68092 and launcher722400. Reacquired Toolkit through discovered app/id;
`get_window_state` fails **window capture timed out: timed out waiting on channel**.
No additional diagnostic detail supplied. Stopped UI input under skill recovery
rules. An earlier occluded browser capture showed Toolkit, so only the explicitly
activated unobstructed browser captures are used as actual-player evidence.
No claim that another app currently captures after the second timeout.

**Live state requiring restoration:** generated Stoker inside Profile Manor is
now temporarily hidden, **not saved**. Human asked to use selected-token Toggle
hidden or deliberately click that token's cyan eye badge to restore visibility;
do not change outside manual Stoker. No automatic file-based restoration or stale
coordinate click attempted. Saved-file audit still passes original ten generated
token positions/hidden states and24 room targets; Manor hash remains c8ab1808...
(full hash above), Crypt d0805821... unchanged. This proves saved baseline only,
not restored live UI state. Human restoration was pending when this entry was
written. Do not save the temporary hidden state.

BLOCKED: visible→hidden→visible completion, Crypt generated-token checks and normal
Toolkit restart/player checks. User-provided working setup supersedes the earlier
human-framing wait, but capture recovery now blocks continuation. Leave Toolkit,
launcher and player browser running; no elevation, permission change, rebuild,
installation, bounded-fog gesture, PDF/GIF repeat or converter edit. Latest full
suite remains144 run/140 passed/four symlink skips. Next action: human restores
Stoker and confirms Toolkit responds, then one fresh enumeration/capture before
continuing Crypt and both-profile restart checks. No new runtime PASS inferred
from package hashes or GM hidden flags.

## Manor restoration observed — 2026-10-18, after ab6b339

After user state update, fresh enumeration/capture succeeds. Selected outside
manual Stoker_token_1 initially; explicitly selected the small inside **Stoker**
without toggling its state. No edit-history increment from selection. Fresh,
activated Waterfox capture shows generated Stoker visible again inside the room,
manual control still visible outside. **PASS restored actual-player visibility**,
closing the initial visible→hidden→visible observation across the preceding test
and this recovery. The exact intervening human action is not inferred. Evidence:
`../2026-10-18/profile-manor-player-restored.jpg`. Saved Manor normally, preserving
the current human-adjusted projection/fog setup and other existing edits. This
supersedes the prior warning that Stoker remains temporarily hidden/unsaved.
No token coordinate, Size or rotation changed by the agent.

Crypt selected through Map Browser and explicit Open map; success toast observed.
Zoomed GM out80→25 to inspect geometry, selected generated Cursed Cannibal without
changing its state. Inspected native linked-projection controls: Select an object
to link then clicking its location selected the existing UVTT group (+288 items),
not a validated token binding. No transform/group/content edit or Crypt save.
Escape issued to leave that selection; refresh then times out, so its selection
outcome is unknown. Temporary projection/framing state may remain in memory.
No Crypt token visibility/placement/Size/rotation changes performed.

Capture intermittently reports `window capture timed out: timed out waiting on
channel`. One fresh-enumeration recovery succeeded earlier in this follow-up,
but the failure recurred. Stop UI work; no reliable current capture for further
input. Crypt actual-player and both-profile restart checks remain BLOCKED; this
is not a conversion failure. No rebuild/reinstall/elevation/settings bypass.
Next human step is to leave the actual **Profile Crypt** room visibly framed in
the working browser (the working setup at start was Manor), then continue from
fresh capture. Manor token is restored and saved; do not hide it as a recovery
step. Labels off and bounded fog separately deferred. No automated rerun for
this evidence-only update;144 run/140 passed/four symlink skips remains latest.

## CPU-aware validation workflow — 2026-10-18, after 65c8c4c

UI phase separated from compute work as requested. No tests, package builds, PDF
rendering, compression or dependency scans ran while the helper/browser UI was
being queried. No native app input or screenshot request was issued this phase.
The CPU sampler finishes before UI requests; recovery sampling follows the failed
request. One request outstanding at a time, no rapid capture polling.

PASS (resource measurement, not runtime feature): host process-counter deltas
normalized over two logical CPUs show Toolkit70.8%,76.5%,75.4% before the UI attempt.
Toolkit is the dominant consumer. Earlier diagnostic measured roughly97% and total
host load100%; current lower load does not demonstrate any applied workaround.
`contention-baseline.json` records the pilot samples.

BLOCKED (native settings/control): one fresh native session setup/enumeration cell
returns `js execution timed out; kernel reset, rerun your request` at the30-second
execution deadline. No inventory returned; exact internal setup/enumeration stage
not isolated. Count **1 timeout/1 setup-enumeration attempt**, **0 screenshot
attempts**, not100% screenshot failures. No immediate native capture retry or stale
input. Original application cap/stream encoding settings cannot be read. Requested
30-FPS app cap and1280x720/15-FPS native stream remain **unapplied**; no guessed
settings-file edits. There is **no after-load-reduction reliability result**.

PASS (recovery measurement only): three separate samples show Toolkit73.66%,74.83%,
75.76%; browser processes7.56%,6.12%,4.09%. A counted confirmation sample shows
Toolkit72.28%, browsers6.22%, capture helper0.00% with one measured helper process;
zero matching compute-candidate processes (reported null rather than pretending
absence is a measured0%). Sampling names cannot prove arbitrary node processes
are/are not build workers; the agent ran no such compute work in the UI phase.
`contention-recovery.json` records the pilot, `contention-recovery-counted.json`
adds explicit category coverage. Toolkit is busy but these data alone neither prove
CPU starvation causes the helper failure nor rule out a separate capture stall.

PASS (browser state only): after recovery sampling finished, purpose-built browser
API inspects the existing in-app player tab. It displays **Start Streaming**, so
that page is stopped and not a duplicate active stream. Waterfox is the previously
observed active player browser; no complete current Waterfox tab inventory or
native Stop projecting action could be verified. No browser screenshot needed.
Do not claim all streams stopped or the native rendering load reduced.

Independent implementation completed while desktop validation stayed pending:
`validation/measure-desktop-load.ps1` provides bounded read-only CPU deltas,
Toolkit/browser/helper/launcher/client/possible-compute categories and measured
process counts. Absent categories are null, not measured zero. Reports refuse
overwrite, including exclusive creation against races. Protected/exited processes
may be omitted; no UI, process priority, global power/security, network or content
changes. `docs/DESKTOP-VALIDATION.md` defines sequential phases, original/changed
settings records, one active player tab, timeout recovery and count denominators.

PASS (targeted tooling checks): PowerShell syntax parser, existing-report overwrite
refusal, real host sampler runs and report structure/Toolkit coverage assertion.
No full conversion suite rerun: production converter unchanged; latest144 run,
140 passed,four Windows symlink skips retained, skips not safety passes. No native
package rebuild/install. Source assets, original content and saved token states
untouched. `contention-comparison.json` summarizes before/recovery/blocked-after
scopes. Capture diagnosis is in `CAPTURE-TIMEOUT-DIAGNOSIS.md`.

Current milestone remains generated-token Crypt player output and both-profile
player restart validation. Manor restoration already observed and saved; no new
visibility edits. Bounded fog deferred and labels off. Next UI opportunity: sample
load, obtain fresh reliable native capture, record existing FPS/stream settings,
apply one supported reduction at a time (30-FPS app,720p/15-FPS stream), stop stream
for GM-only checks, then compare the same bounded sequential capture sequence.
If access/load still fails, preserve pending checks and continue independent work;
no repeated human intervention request for this unchanged condition.


## Portable capture execution results (2026-10-18)

PASS (file-level): Manor/Crypt native bundles and relocated profiles, with original
bytes, source identity, hashes, calibration and namespaces retained. Controls stay
separate from geometry. Native bundles contain 8/12 files. Final targeted run: 6
passed. Initial full run: 148 total, 142 passed, 4 skipped,1 corrected safety failure
and1 inventory error subsequently passed. No clean full rerun claimed.
An initial Crypt source-reader failure passed controlled comparisons/retry;
cause unconfirmed. No conversion math changed.
See [execution details](../2026-10-18/PORTABLE-CAPTURE.md) and
[hashes](../2026-10-18/portable-capture-results.json).

BLOCKED/PENDING: desktop helper setup/enumeration after bounded recovery.
Full support diagnostic stays local; no new activation/capture/input/runtime pass.
Crypt actual-player visibility, profile player restart and bounded fog remain
pending independently of development. Accepted GM/earlier player evidence remains
accepted. Labels off. Manual import/export/calibration, reviewed installation,
GIF setup and conversion gaps remain explicit. No original assets, campaigns,
manually edited notes or installation changed.
