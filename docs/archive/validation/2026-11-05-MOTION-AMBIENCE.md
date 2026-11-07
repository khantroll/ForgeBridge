# Foundry motion tiles and map ambience — 2026-11-05

Branch **feature/animated-tiles-ambience**, based on main `1d6102c`.
Windows; native reference Toolkit **0.5.1.18**. **Generated-output Toolkit checks
are PENDING**, not inferred from native controls or package bytes. Prior human
native import/place/move and WAV map-audio results (2026-11-04) remain separate.
Prior synthetic GIF playback/movement/restart (2026-10-16) remains scoped to its
original control. Latest v0.12.0 note/music acceptance is separately recorded in
2026-11-05-V0120-TOOLKIT-CHECK.md; it does not validate these new record writers.

## Implemented slice and file-level evidence

- Foundry source adapter emits square-based tile/sound IR, then native writers
  apply 2.56 target units/square. Padding/explicit scene origin is included;
  source pixels are never copied directly to native coordinates.
- WEBM **VP9** and MP4 **H.264/AVC**, one video track: original encoded bytes and
  extension preserved with content-unique native filenames. Native video asset,
  metadata and video-preset declarations come from owned captured controls.
  Playback/loop defaults are enabled, video audio muted, play-symbol thumbnail.
  Container/header inspection is bounded; it is not a full video decode proof.
- Animated GIF/PNG/WebP: composed 8-bit RGBA PNG frames in native ArkenImage lists;
  native asset **and map preset** category 1, FPS/frame count, position, footprint,
  clockwise rotation and hidden state. GIF timing in the fixture is four 250-ms
  frames, mapped to 4 FPS. Variable/very short source timings are reported as
  approximations (mean duration / 60-FPS cap). At most 128 frames / 16 million
  total frame pixels. Missing frame timing follows the documented default;
  source loop/effect behavior still needs review. Static tiles remain supported.
- AmbientSound → SFX .rwfile/.rwmeta, ambience preset .rwamb/.rwmeta and native
  map content-link anchors. Audio is OGG Vorbis, MP3 or mono/stereo PCM WAV,
  byte-for-byte preserved; source byte limit 16 MiB (tiles have the same limit).
  No Toolkit/external encoder is required by production. Unsupported/unsafe/
  missing inputs are explicit losses with no substitute.
- Source radius / positive grid distance → squares → ×2.56. Native full-volume
  and falloff fields are explicit in the JSON. Easing approximates linear
  attenuation, or a 0.1% edge when easing is off; walls, precise falloff, timing,
  darkness, channels/levels and effects remain approximations. Preset/track gain
  is 1; attachment holds source volume. Source hidden disables sound; hidden
  anchor icon with playWhenHidden is a separate native control setting.
- Dependency capture/review now follows .rwamb, its metadata and SFX pair. The
  installer allows only the additional known native extension; add-only,
  no-overwrite, backup and receipt protections are unchanged. The map-reachable
  closure has **16 files**; the NPC/index note pairs add **4 independent files**.
- Missing CR omits the Challenge label. Existing active flags are respected;
  rows without such flags request zero-size zero-width text. Whether native
  layout gaps collapse is **PENDING**; a specific approximation loss records it.
  No unknown schema flags are invented.

Definitions/payload-free defaults: `src/forgebridge/motion-schema.json`.
Immutable raw references and provenance:
`fixtures/arkenforge-native-controls-2026-11-03/` including `gif-control/`.
The observed map ambience field shape was read from a saved native map while
Toolkit was closed; no original map/media content was copied or modified.
Production needs no installed/exported templates or locally patched dependency.

## Automated checks

Windows full suite **338 run, 334 passed, four Windows symlink privilege skips**.
Twelve new motion tests cover typed controls, exact embedded bytes, codec refusal,
frames/timing, category, rotation/hidden/size, different grid/origin, radius/volume,
repeated texture deduplication and unique placements, dependency closure, fake
MyAssets install/uninstall, opt-in bounded opaque-byte serialization, and saved-map
capture retaining both preset metadata and all original bytes with three closed-
Toolkit checks (mocked only for the synthetic test).

The native GIF placement comparison caught a static-category mismatch not caught
by the first asset-only test; it was corrected to the observed category 1 and the
regression now asserts it. The preliminary isolated candidate was removed only
through its own receipt (exit 0, 20 removed, no changes retained); its backup and
receipt `forgebridge-16ac0a878b644d3a9b4019ce647689dc` remain. This was a file-level
correction, not an observed Toolkit conversion failure. Nothing was deleted by hand.

## Isolated installation

Owned source Adventure: **fixtures/synthetic-motion-adventure/**. No commercial
assets, imported scripts, external art or original user campaigns are involved.
Final build: `C:/AMD/fb-motion-check-handoff-2026-11-05/scene-001/native-package.zip`.
Package SHA-256:
`ab061dae455eaa9455901821e5338fbe44c20869260ece6da4d9c7f3405e7437`.

Toolkit was closed for install and verification; never launched or killed.
Install exit **0**, **20 files added**, all hashes match receipt and package.
The two embedded audio payloads independently match source hashes. Rebuilding
the current owned fixture regenerates all 20 installed native files byte-for-byte.
Receipt:
`C:/AMD/fb-backups/forgebridge-0ff050e03cc0426dbe69e04be3cb438c/uninstall.json`.
Backup:
`C:/AMD/fb-backups/forgebridge-0ff050e03cc0426dbe69e04be3cb438c/MyAssets`.
Machine-readable values, native coordinates and remaining losses are in the
adjacent JSON. Existing check packages and user content were not uninstalled.

## Exact Toolkit targets for Claude / Jeffrey

Start Toolkit only through the launcher. Keep the established 30-FPS setting;
player output is not required to begin these GM/map checks.

1. **Maps → FB Motion Check → FB Motion Check.** Grid is 16×12 squares,
   100 source px/square, 5 ft/square; upper-left native origin (0,0).
2. **Upper-left WEBM tile**, footprint x250–450/y200–400 source px, centre
   **(3.5, 3) squares**, native **(8.96, -7.68)**: moving test pattern should
   play/loop. It is 2×2 squares and has no embedded-video sound.
3. **Upper-middle GIF tile**, footprint x700–900/y200–400 px, centre
   **(8, 3) squares**, native **(20.48, -7.68)**: four coloured moving frames
   should play at **4 FPS**, **15° clockwise**, 2×2 squares. Check movement and
   placement independently for each tile, then representative save/reopen.
4. **Green lower-left cross / FB Left OGG 440Hz**, centre **(3.5, 8.5) squares**,
   native **(8.96, -21.76)**, source position (350,850) px. Volume **60%**;
   intended outer hearing radius **10 ft = 2 squares = 5.12 native units**.
   Approximate linear falloff starts at the centre. It embeds the known synthetic
   two-second 440-Hz OGG. Establish which native listener/camera/projection is
   driving spatial audio; verify audible inside and quiet beyond the green ring.
5. **Blue lower-right cross / FB Right WAV 660Hz**, centre **(11.5, 8.5) squares**,
   native **(29.44, -21.76)**, source position (1150,850) px. Volume **50%**;
   intended outer hearing radius **15 ft = 3 squares = 7.68 native units**.
   Almost uniform gain until the final 0.1% edge. Synthetic eight-second 660-Hz
   PCM WAV; test separately from the OGG. Rings do not overlap. Actual carry,
   native attenuation/scheduling and sound persistence remain runtime checks.
6. **Notes → FB Motion Check → FB Motion Watcher (no CR)**: no Challenge label,
   no unknown proficiency, and empty Skills/Senses/Languages rows should leave
   no gap. The zero-size layout encoding is still a candidate until observed.

Do not mark player visibility, fog, procedural light animation or actor automation
passed from these checks. Labels remain off; background words/rings are baked
fixture art, not native labels. Do not merge this PR before the requested review.

Final metadata review also found blank video variant names; the writer now initializes both inherited names and tile names, with a regression assertion. This file-level correction refreshed only the isolated candidate through its receipt (20 removed, no changed files retained). All 20 final installed files match both receipt hashes and package bytes. Generated playback remains pending.
