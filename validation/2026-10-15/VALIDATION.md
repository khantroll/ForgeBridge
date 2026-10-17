# ForgeBridge validation — 2026-10-15

## Scope and initial inspection

Branch: `cursor/dynamic-lighting-c6b0`. Tracked working tree was clean on arrival. Existing untracked manor module, images, token assets, companions, UVTT files, templates and prior ZIPs were preserved. No AGENTS.md was found in the workspace or its checked ancestors. Read README.md, STATUS.md, architecture, fixture notes, Arkenforge research and UVTT compatibility notes; inspected CLI, package/map/media code and tests before edits.

This log distinguishes **file-level checks** from **observations inside Arkenforge**. Current-build Arkenforge observations began after desktop and launcher permissions were repaired, as recorded below. The summary includes the 2026-10-17 profile follow-up; new profile runtime checks are blocked by a desktop recovery failure. Earlier user confirmations remain regression cases, not current PASS evidence.

## Results

| Status | Check | Evidence / limit |
|---|---|---|
| PASS | Automated checks | Latest full run: 144 tests, 140 passed, four Windows symlink checks skipped (168.925s); profile-full-tests.txt. Includes scene identity/calibration and isolation regression. |
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
| BLOCKED | New profile runtime switching/persistence | Launcher activation/capture recovery twice failed: foreground window did not report a process id. Neither new output observed open. |
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
