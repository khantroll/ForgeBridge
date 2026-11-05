# Native reference capture — 2026-11-03

Windows; Toolkit **0.5.1.18**, launched through Arkenforge Launcher 7.0.0.3.
Raw reference bytes are immutable examples, not converter-generated output.
`manifest.json` records exact MyAssets-relative source paths, sizes, SHA-256 and
inert NRBF class inventories. Copies were taken with Toolkit closed. Do not
install these fixtures automatically or modify their bytes to make tests pass.

## Clicks and observations

1. Saved a new isolated map **FB Native Reference 2026-11-03**. No original
   campaign/profile map was opened or edited. The blank map is not included:
   it provides no successful animation/spatial-audio placement reference.
2. Content → Library → User Content → Map assets → Import content → Select
   files: imported `sources/FBReference-motion.webm`, then separately
   `sources/FBReference-video.mp4`. Both completed and appeared with filmstrip
   thumbnails. Right-click → Set as selected failed for **each** with
   **“An issue occurred trying to load this tile”**. No map placement, playback
   on a map, positioning or restart persistence is claimed.
3. Both imports decode as `ArkenTileUpgrade` containing `ArkenVideo`, with
   `ArkenTilePresetVideo` in metadata (tile type 8/category 2). For these two
   imports, video is an asset subtype rather than a separately captured map
   object. This is file evidence, not proof of a supported conversion.
4. Library → Sound effects → Import content: imported the synthetic WAV.
   Audio → Ambience → New Ambience Preset → named
   **FB Native Reference Ambience 2026-11-03** → Add new SFX → From Content
   Library → Sound effects → FBReference-tone → Select content.
   The saved `.rwamb` contains one AmbienceTrack referencing
   `MyAssets/Audio/SFX/FBReference-tone.rwmeta`; both SFX files are included.
   Preset and track volume were 50%. Audible playback was not assessed.
5. Add to map returned **“This can only be done with one ambience preset at a
   time”** although one was shown. No spatial/map-attached sound reference
   was obtained. Expanded track controls showed timing, volume and effects;
   the SFX library menu had no direct placement action. This remains OPEN.

Sources are original synthetic test content: 64×64, two-second, 4-FPS testsrc2
videos (WEBM VP9; MP4 H.264/yuv420p; no audio), encoded with the separately
installed PySceneDetect ffmpeg, single-threaded while Toolkit was closed.
The WAV is two seconds, 22,050-Hz mono PCM16, 440-Hz sine, amplitude 1200,
generated with Python's standard `wave`/`struct` modules. No Toolkit encoder
is a ForgeBridge dependency. Native thumbnails and embedded bytes are retained
exactly as Toolkit wrote them; original source paths inside records are
provenance, not portable install instructions.

## Cleanup and preservation

With Jeffrey's explicit confirmation, deleted through Toolkit only:
FBCapture 5e Character, FBCapture 5e Item, FBCapture 5e Spell, and
`Playlists/ForgeBridgeCampaign-edfc87a75fc39f64264e/FBCapture Playlist`.
Existing tracked template/playlist fixture copies and uninstall receipts remain.
`session-file-diff.json` compares SHA-256 snapshots before/after capture:
only those eight files disappeared. Toolkit also wrote its FileIndex and
New Map pair automatically; these were not restored over native writes.
New isolated reference files remain in MyAssets for a possible human check.

`Retire-ForgeBridgeTestContent.ps1` could not be located in the repository,
AMD root, other checked clone, Desktop, Documents or Downloads; Jeffrey does
not know its path. Dry run and Apply are **BLOCKED**. No replacement script or
broad retirement move was improvised.

Other visible native menu capabilities not captured/converted here: SFX
palettes; asset text, shadows, flat colour and blur; per-asset effects; native
vision/movement/sound blocking and ambience timing. Menu presence alone is
not runtime validation of any ForgeBridge mapping.

## Later human observation — 2026-11-04

Jeffrey reports that these motion/video assets import, place and move correctly,
and that the WAV tone plays when attached to a map. These human results supersede
the open native-operation checks above, while retaining the earlier agent's
exact failed workflow as history. They do not establish automatic Foundry
animated-media/ambient-sound conversion, radius/falloff equivalence or restart
persistence. Jeffrey also confirmed the synthetic spell notes work. The remaining
audio failure is music playlists; MP3 and an explicitly selected OGG were silent.
