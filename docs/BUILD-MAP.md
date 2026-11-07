# Remaining feature build map

As of 2026-11-04 (Jeffrey's Toolkit checks that day), after v0.11.0. File-level implementation and native runtime
acceptance are separate. Native captures used Windows / Toolkit 0.5.1.18.

| Feature | Status | Reference capture | What proves it in Toolkit |
|---|---|---|---|
| Spell notes | Synthetic Toolkit check **PASS** (2026-11-04: links open Spell notes, fields render). Real Count's Manor three spells (Bless, Spiritual Weapon, Protection from Poison) **PASS at file level** with dnd5e 6.0.6 unzipped folder/`packs/spells` (`validation/2026-11-04-SPELLPACK-REAL-RUN.md`); ZIP input refused by read budget; **real three in Toolkit PASS** in `validation/2026-11-05-FINAL-TOOLKIT-CHECK.md` | `fixtures/arkenforge-5e-templates/5e-Spell.*` | Install real Count's Manor build with the pack; open each of the three scroll links, compare fields |
| FG NPCs/items/story | Representative Toolkit PASS 2026-11-05; latest display check PASS, blank-gap follow-up pending | 5e Character/Item/Spell controls in `fixtures/arkenforge-5e-templates/`; story is an ordinary text note because no FG story control was captured | `python -m forgebridge.fantasy_grounds MODULE --campaign-out DIR [--install --myassets … --backup-root …]` on a module you control; install uses the same add-only receipt path as Foundry. Compare notes, links and images with the source in Toolkit, then reopen. Map conversion is unchanged and still does not write these notes |
| Missing Foundry Data art | OPEN; external references remain losses | No new native schema needed; existing image/token controls | Resolve only explicitly supplied Data root; show correct portrait/tile and persist |
| Animated tiles/video | Toolkit **PASS** 2026-11-04 (Jeffrey): captured WEBM and MP4 import, place on a map and move. Schema writer now emits captured WEBM VP9/MP4 H.264 and decoded animated-image frames at file level; FB Motion Check runtime pending | `fixtures/arkenforge-native-controls-2026-11-03/MyAssets/Media/Cartographer/` | Converter-written animated tile places and plays after save/restart: NEEDS IN-TOOLKIT EVIDENCE |
| Ambient sounds / presets | Toolkit **PASS** 2026-11-04 (Jeffrey): WAV tone added to a new ambience preset, saved, attached to a map, tone audible. Schema writer now emits map-attached OGG/MP3/PCM-WAV presets at file level; native radius/easing acceptance pending | Same capture folder, `AmbiencePresets/` and `Audio/SFX/` | Converter-written ambience attaches and plays; radius/falloff: NEEDS IN-TOOLKIT EVIDENCE |
| Music by ear | Native embedded MP3/OGG controls **PASS** 2026-11-04 (Jeffrey). Production embeds MP3 and OGG unchanged with Master 80%; Ambient three-track playback PASS 2026-11-05 (`validation/2026-11-05-FINAL-TOOLKIT-CHECK.md`) | `fixtures/arkenforge-user-playlist/toolkit-made-music-playlist/`; `validation/2026-11-05-MUSIC.md` | Hear each of the three rebuilt Ambient tracks separately |
| Spell notes | Synthetic Toolkit check **PASS** (2026-11-04: links open Spell notes, fields render). Real Count's Manor three spells (Bless, Spiritual Weapon, Protection from Poison) **PASS at file level** with dnd5e 6.0.6 unzipped folder/`packs/spells` (`validation/2026-11-04-SPELLPACK-REAL-RUN.md`); ZIP input refused by read budget; **real three in Toolkit: NEEDS IN-TOOLKIT EVIDENCE** | `fixtures/arkenforge-5e-templates/5e-Spell.*` | Install real Count's Manor build with the pack; open each of the three scroll links, compare fields |
| FG NPCs/items/story | File-level only, Toolkit check pending | 5e Character/Item/Spell controls in `fixtures/arkenforge-5e-templates/`; story is an ordinary text note because no FG story control was captured | `python -m forgebridge.fantasy_grounds MODULE --campaign-out DIR [--install --myassets … --backup-root …]` on a module you control; install uses the same add-only receipt path as Foundry. Compare notes, links and images with the source in Toolkit, then reopen. Map conversion is unchanged and still does not write these notes |
| Missing Foundry Data art | File-level only, Toolkit check pending | No new native schema; existing portrait and tile writers | `--foundry-data DIR` or the GUI folder picker. Resolve only inside that folder; a missing file stays a loss. Show the portrait and tile in Toolkit and confirm they persist |
| Animated tiles/video | Toolkit **PASS** 2026-11-04 (Jeffrey): captured WEBM and MP4 import, place on a map and move. ForgeBridge does not yet *write* them (converter mapping OPEN) | `fixtures/arkenforge-native-controls-2026-11-03/MyAssets/Media/Cartographer/` | Converter-written animated tile places and plays after save/restart: NEEDS IN-TOOLKIT EVIDENCE |
| Ambient sounds / presets | Toolkit **PASS** 2026-11-04 (Jeffrey): WAV tone added to a new ambience preset, saved, attached to a map, tone audible. Converter mapping from Foundry ambient sounds OPEN | Same capture folder, `AmbiencePresets/` and `Audio/SFX/` | Converter-written ambience attaches and plays; radius/falloff: NEEDS IN-TOOLKIT EVIDENCE |
| Music by ear | Native embedded MP3/OGG controls **PASS** 2026-11-04 (Jeffrey). Production embeds MP3 and OGG unchanged with Master 80%; final Ambient package check pending | `fixtures/arkenforge-user-playlist/toolkit-made-music-playlist/`; `validation/2026-11-05-MUSIC.md` | Hear each of the three rebuilt Ambient tracks separately |
| More systems | NOT STARTED | No system-specific captures beyond dnd5e | Source-specific field mapping and representative native acceptance |
| Other native menu capabilities | OPEN inventory only | Capture README lists SFX palettes, text/shadow/blur/effects/blocking | Capture minimal controls before implementing each mapping |

Audio result recorded 2026-11-04: original ForgeBridge MP3 and explicitly selected OGG were silent. Jeffrey subsequently confirmed all three Toolkit-imported native controls (WAV, MP3, OGG) audible. This does not pass the repaired ForgeBridge playlist; that remains a separate recheck. See the populated music fixture and repair validation.

Capture/cleanup details and exact failures: see
`fixtures/arkenforge-native-controls-2026-11-03/README.md` and its manifests.
The four specifically approved FBCapture test objects were deleted. Retirement
script dry run/Apply is BLOCKED because the existing script is unavailable;
uninstall receipts and unrelated content were retained. No broad cleanup was
substituted. Bounded fog/profile-player checks retain their prior pending status.

## Final trial audio build — 2026-11-05

Jeffrey confirms MP3 embedded unchanged in a native song is audible in Toolkit 0.5.1.18 (2026-11-04). Production now embeds MP3 and OGG Vorbis bytes directly, retaining each extension and initializing Master at 80%. URL-encoded package audio paths are decoded and revalidated before contained lookup. No Toolkit encoder is required. The rebuilt Ambient playlist still needs its own Toolkit check; missing package tracks remain explicit losses.

## Motion / spatial sound slice (feature/animated-tiles-ambience)

Owned fixture: `fixtures/synthetic-motion-adventure/`; final native installation
and exact targets: `validation/2026-11-05-MOTION-AMBIENCE.md`.
Prior human native controls remain separate from this generated output's pending
Toolkit check. Animated frames have bounded fixed-FPS timing; video bytes remain
unchanged and muted. Spatial sound uses source distance/grid conversion and
2.56 target units/square; easing, occlusion and scheduling remain approximations.
Missing-CR Challenge labels are omitted. Empty nongated stat rows request zero-size
zero-width text; whether that removes Toolkit layout gaps remains pending.
Labels off; source procedural light animation, fog/vision and unrelated profile
player-output checks remain explicit gaps, unaffected by this work.
## Fog/vision/animation implementation — 2026-11-06

Captured-schema configuration mapping is implemented at file level; native runtime acceptance remains pending. Dynamic fog/persistence, bounded owned-character vision and supported light effects are described in `../validation/2026-11-06-FOG-VISION-ANIMATION.md`. Historical exploration masks, full vision rules, unsupported animations and scene darkness intensity remain explicit gaps.
