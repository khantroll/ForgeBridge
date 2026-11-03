# Campaign runtime findings: fixes and prepared recheck — 2026-11-03

User/Claude reported invisible playlists/songs, note-marker token appearances after linking, duplicate languages, movement order and suspect stat values. These are user-reported runtime observations; this agent did not launch Toolkit.

## Fixes and file-level validation

- Metadata comes from the Toolkit-created user playlist. Complete song ArkenAudioMeta declarations also match a Toolkit-created user audio/SFX control from a consistent closed-Toolkit backup. The SFX control uses the same class, with _isSong false; generated songs set it true. Both previous-path members are present.
- Ambient is now MyAssets/Playlists/FB Campaign Check/Ambient.rwpl, with matching metadata. FB MP3 Test is in the same folder and its two song filenames match their display names. Listing/playback is PENDING recheck.
- Token links are omitted and reported as manual. Token note/icon/Size bytes are unchanged by the campaign writer; the previous static icon/Size assertion did not establish map appearance. Portrait rendering is PENDING recheck.
- Equipped-armor AC and structured attack bonuses are derived statically. Natural AC uses its stored flat value; flat AC does not add DEX. Explicit activity abilities are honored. Languages deduplicate case-insensitively and walk speed comes first. No Foundry roll, hook, script or effect executes.
- Current display IR in the built package was compared against the final implementation and original actor records for all 18 actors. Source-companion JSON sorts dictionary keys, so reconstruction uses the original records to preserve senses/activity order. Full before/after details are in the JSON.

| Actor | Previous AC | Corrected AC | Other changes |
| --- | --- | --- | --- |
| Animated Armor | 18 | 18 | no display change |
| Boris the Vampire | 10 | 10 | language deduplication; walk first |
| Count Lugosi | 15 | 15 | walk first |
| Cursed Cannibal | 12 | 12 | no display change |
| Dark Soul | 12 | 12 | Soul Drain +2 to hit → +3 to hit |
| Elizabeth | 13 | 13 | Bite +3 to hit → +5 to hit |
| Giant Spider | 14 | 14 | walk first |
| Igor | 11 | 11 | no display change |
| Margret the Ghost | 11 | 11 | no display change |
| Monster | 9 | 9 | language deduplication |
| Rahadin | Unknown (source AC calculated by Foundry) | 18 | no display change |
| Skeleton | 13 | 13 | no display change |
| Stoker | 12 | 12 | walk first |
| Swarm of Rats | 10 | 10 | no display change |
| Swarm of Spiders | 12 | 12 | walk first |
| Wight | Unknown (source AC calculated by Foundry) | 14 | no display change |
| Willa | 10 | 10 | no display change |
| Zombie | 8 | 8 | no display change |

**Boris source discrepancy:** he explicitly specifies ac.calc=natural, ac.flat=10 and Claws attack.ability=int (INT 8, modifier −1, proficiency +2). AC 10 / Claws +1 therefore remain. DEX 16 is not silently substituted. Languages now show common once; speed is 30 ft, climb 30 ft.

Rules verified against the package’s dnd5e 4.3.5: [AC configuration](https://github.com/foundryvtt/dnd5e/blob/release-4.3.5/module/config.mjs), [armor preparation](https://github.com/foundryvtt/dnd5e/blob/release-4.3.5/module/data/actor/templates/attributes.mjs), [attack calculation](https://github.com/foundryvtt/dnd5e/blob/release-4.3.5/module/data/activity/attack-data.mjs). Dice, effects and dynamic formula terms remain explicit limits.

## Recheck installation

Toolkit was confirmed closed before guarded operations. Old audio receipt: exit 0, six removed, none kept. Old campaign receipt: exit 0, 331 removed, three changed notes kept. All three retained files matched the new full backup after reinstall; none was overwritten or manually deleted.
Corrected generated notes use an explicit Campaign-v2- filename prefix to coexist with those edited v1 files; source identities and display names remain intact.

- Count’s Lair rebuild/install: exit 0, 334 added. Map and notes folder: FB Campaign Check. Receipt: `C:\AMD\fb-backups\forgebridge-034c85bacbe7477d8b4f76713e2b2072\uninstall.json`.
- FB MP3 Test rebuild/install: exit 0, 6 added. Receipt: `C:\AMD\fb-backups\forgebridge-0c74d4820ef94387863b38923f695505\uninstall.json`.
- MP3 and OGG bytes are unchanged from the first experiment (external PySceneDetect encoder; no Toolkit ffmpeg). MP3 original filename ends .mp3. This is an experiment only, not production MP3-support acceptance.
- Recheck notes: Boris the Vampire, Stoker, Amber Shard, Despair. New files have Campaign-v2- prefixes. Playlists: Ambient (empty; normal MP3 tracks remain manual) and FB MP3 Test (MP3 original / OGG Vorbis converted).

Windows suite: 291 run, 287 passed, four symlink-privilege skips, zero failures. Focused metadata/token and derivation regressions also passed. No new runtime check is marked passed.

[Curated results, receipts, package hashes and 18-actor audit](2026-11-03-campaign-recheck-results.json).
