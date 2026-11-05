# Remaining feature build map

As of 2026-11-04 (Jeffrey's Toolkit checks that day), after v0.11.0. File-level implementation and native runtime
acceptance are separate. Native captures used Windows / Toolkit 0.5.1.18.

| Feature | Status | Reference capture | What proves it in Toolkit |
|---|---|---|---|
| Spell notes | Synthetic Toolkit check **PASS** (2026-11-04: links open Spell notes, fields render). Real Count's Manor three spells (Bless, Spiritual Weapon, Protection from Poison) **PASS at file level** with dnd5e 6.0.6 unzipped folder/`packs/spells` (`validation/2026-11-04-SPELLPACK-REAL-RUN.md`); ZIP input refused by read budget; **real three in Toolkit: NEEDS IN-TOOLKIT EVIDENCE** | `fixtures/arkenforge-5e-templates/5e-Spell.*` | Install real Count's Manor build with the pack; open each of the three scroll links, compare fields |
| FG NPCs/items/story | File-level only, Toolkit check pending | 5e Character/Item/Spell controls in `fixtures/arkenforge-5e-templates/`; story is an ordinary text note because no FG story control was captured | `python -m forgebridge.fantasy_grounds MODULE --campaign-out DIR` on a module you control; compare notes, links and images with the source, then reopen. Map conversion is unchanged and still does not write these notes |
| Missing Foundry Data art | OPEN; external references remain losses | No new native schema needed; existing image/token controls | Resolve only explicitly supplied Data root; show correct portrait/tile and persist |
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
