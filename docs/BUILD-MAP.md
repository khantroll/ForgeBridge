# Remaining feature build map

As of 2026-11-03, after v0.11.0. File-level implementation and native runtime
acceptance are separate. Native captures used Windows / Toolkit 0.5.1.18.

| Feature | Status | Reference capture | What proves it in Toolkit |
|---|---|---|---|
| Spell notes | Available world spells implemented; optional system-pack resolution next | `fixtures/arkenforge-5e-templates/5e-Spell.*`; README confirms complete UI | Open generated spell, compare all fields and follow the actor's rewritten spell link |
| FG NPCs/items/story | OPEN, FG phase 3 | 5e Character/Item controls in `fixtures/arkenforge-5e-templates/`; no FG story control yet | Convert controlled FG module; compare notes and links to source, reopen |
| Missing Foundry Data art | OPEN; external references remain losses | No new native schema needed; existing image/token controls | Resolve only explicitly supplied Data root; show correct portrait/tile and persist |
| Animated tiles/video | PARTIAL references; native placement FAILED for both synthetic codecs | `fixtures/arkenforge-native-controls-2026-11-03/MyAssets/Media/Cartographer/` | Successful native placement, observable playback/position and save/restart; library import alone is insufficient |
| Ambient sounds / presets | Preset + SFX captured; spatial/map attachment OPEN | Same capture folder, `AmbiencePresets/` and `Audio/SFX/` | Place a source, verify radius/falloff and attachment, save/restart; confirm sound by ear |
| Music by ear | BLOCKED on Jeffrey's listening result | `fixtures/arkenforge-user-playlist/`; installed FB MP3 Test | Hear original MP3 and OGG separately; report any exact error |
| More systems | NOT STARTED | No system-specific captures beyond dnd5e | Source-specific field mapping and representative native acceptance |
| Other native menu capabilities | OPEN inventory only | Capture README lists SFX palettes, text/shadow/blur/effects/blocking | Capture minimal controls before implementing each mapping |

Jeffrey: please open **Audio → Playlists → FB Campaign Check → FB MP3 Test**,
play the MP3 entry and the OGG entry separately, and record **audible / silent /
error (exact message)** for each. Neither waveform bytes nor a changing play
button constitutes audible acceptance. Answer is pending; no default audio
encoding policy is inferred.

Capture/cleanup details and exact failures: see
`fixtures/arkenforge-native-controls-2026-11-03/README.md` and its manifests.
The four specifically approved FBCapture test objects were deleted. Retirement
script dry run/Apply is BLOCKED because the existing script is unavailable;
uninstall receipts and unrelated content were retained. No broad cleanup was
substituted. Bounded fog/profile-player checks retain their prior pending status.
