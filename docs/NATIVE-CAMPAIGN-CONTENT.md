# Campaign content beyond maps — formats and plan

Started 2026-11-02. Goal: move the adventure, not just the maps — stat blocks,
items, roll tables, music/ambience, map tiles and animated media — from Foundry
(and later Fantasy Grounds) into native Arkenforge content.

Source inventory, Count's Manor (adventure-5e): 18 NPC actors (dnd5e `npc`:
abilities, attributes.hp/ac, details, traits, skills, spells; embedded items
such as *Multiattack* (feat) and *Slam* (weapon)), 17 items (equipment 5, tool
4, consumable 4, weapon 2, loot 2), 3 roll tables (Despair 1d3/3, Lingering
Injuries 1d2/9, Nightmare 1d6/6), 1 playlist *Ambient* (3 MP3s), static map tiles
(e.g. Count's Crypt: 10 — pit trap, glyphs, buttons). No animated tiles/videos.

## Native formats read from shipped Arkenforge packs (no Toolkit needed)

Read from `ArkenforgeData\Packs` (Arkencore, Great British Care Pack) with
ForgeBridge's NRBF reader; not committed.

### Playlist — `*.rwpl` + `*.rwmeta`

```
ArkenPlaylist
  _name, _pack, _creator
  _songs: KVPOrderedList<ContentItem>
    _entries: List<KVPEntry<ContentItem>>  (each: _order, _value)
      ContentItem
        _filePath = 'Packs/<pack>/Audio/Songs/.../<song>.rwmeta'   (MyAssets/... for user content)
        _content  = MusicTrackInfo { _name, _artists, _songPath (same path),
                                     _pack, _creator, _trackVolumes: Dictionary<string,…> }
        _officialFlag = False
  _links: List<string>
```

### Song — `*.rwfile` + `*.rwmeta`

- `.rwmeta`: `ArkenAudioMeta { _artists, _album, _category, _duration (s),
  _isSong = True, _orderValue, _name, _pack, _creator, _genre, _subgenre, _tags,
  _starred, _hideFromView, _includedWorldPaths, _official, _links }`.
- `.rwfile`: `ArkenAudio { _name, _pack, _creator, _album, _category, _duration,
  _isSong, _orderValue, _tags, _artists, _tracks: List<AudioTrack> }`;
  `AudioTrack { _trackName = 'Master', _originalFile = '<name>.ogg',
  _clipRAW = byte[] (the whole OGG file), _parentName }`.
- Shipped sample embeds OGG. Whether the Toolkit plays MP3 bytes in `_clipRAW`
  is unverified → convert MP3 to OGG Vorbis (ffmpeg ships with the Toolkit,
  but ForgeBridge must not depend on it; use a Python-side encoder or report
  manual) or test MP3 bytes in the Toolkit first.

### Ambience preset — `*.rwamb`, SFX palette — `*.rwsfx`

700 ambience presets and 91 SFX palettes ship; layout to be read when Foundry
ambient sounds are mapped (Count's Manor has none placed).

### Roll tables

Already written as `ArkenNoteFieldRollableTable` fields inside notes (Toolkit
tested on synthetic content). Count's Lair showed 0 because its table was only
linked from text outside the selected scene's dependency set.

## 5e note templates — captured 2026-11-02 (Toolkit 0.5.1.18)

Created in the Toolkit from its built-in templates (New note → *5e Character*,
*5e Item*, *5e Spell*; there is no separate monster template — *5e Character*
is the creature stat block), saved untouched, copied to
`fixtures/arkenforge-5e-templates/` (`5e-Character`, `5e-Item`, `5e-Spell`,
`.rwnote` + `.rwmeta`). The originals stay in the owner's MyAssets as
`Encyclopedia/Notes/FBCapture 5e *.rwnote`.

Each note is an ordinary `ArkenNoteUpgrade` whose field category holds an
`ArkenNoteFieldMedia` (*Item image*, empty path; Character/Item only) followed
by one block field. Every visible value is an `ArkenTextString` (per-character
`ArkenTextCharacter` with `_size`, `_hexColour`, `_fontSettings` enum
**0 normal, 1 bold, 2 italic**, `_link`). Labels are bold runs inside the same
string (`Armor Class` bold + ` 10` normal), not separate fields.

### `ArkenNoteFieldStatBlock5e` (`_name = '5eStatBlock'`)

| Member | Template text / meaning |
|---|---|
| `_nameText` | size 90, colour 58180D — creature name |
| `_typeText` | italic — "Medium undead, lawful evil" |
| `_armorClassText` | **Armor Class** 10 |
| `_hitPointsText` | "(9d1 + 1)" — HP formula only |
| `_trackedHitPoints` | `ArkenNoteFieldStat` (statType 2): `_currentValueStr`, `_minValueStr` '0', `_maxValueStr`; float fields 0 in the template |
| `_speedText` | **Speed** 30 ft |
| `_strValNew` … `_chaValNew` | "10 (+0)" each |
| `_savingThrowsText` + `_savingThrowsFieldActive` | **Saving Throws** … |
| `_skillsText` | **Skills** … |
| `_damageVulnerabilitiesText` + `…FieldActive` (False in template) | |
| `_damageResistancesText` + `_damageResistanceFieldActive` | |
| `_damageImmunitiesText` + `…FieldActive` | |
| `_conditionImmunitiesText` + `…FieldActive` | |
| `_sensesText`, `_languagesText`, `_challengeText`, `_proficiencyBonusText` | bold label + value |
| `_abilities`, `_actions`, `_reactions`, `_legendaryActions` | `List<ArkenTextString>`, one string per entry, colour 000000: **Name.** description; attacks use *Attack type:* / *Hit:* italic runs |

Inactive optional lines are hidden by the `…FieldActive` flags; empty
action/reaction/legendary lists should be tested (template has one each).

### `ArkenNoteField5eItemBlock` (`_name = '5eItemBlock'`)

`_nameText` (90, 58180D), `_typeText` ("1st-level wonderous item"),
`_descriptionText` (plain description, colour 000000).

### `ArkenNoteField5eSpellBlock` (`_name = '5eSpellBlock'`)

Name; level/school line; *Casting time*, *Range*, *Components*, *Duration*,
description, *Attack/Save*, *Damage/Effect*, *At higher levels* — all
`ArkenTextString`.

Long item/spell/feature descriptions can also go in ordinary text fields below
the block, which already round-trip through `NoteBuilder`.

## Still needs the Toolkit

- Validation of every new writer on one installed scene (a filled stat block
  opening without the Toolkit rewriting or rejecting it).

## Implemented campaign-content path (file-level, 2026-11-02)

The normal Foundry `convert` path now reads the selected Adventure's entire
tables/actors/items/playlists collections, independent of scene note reachability.
Standalone world/compendium actors and items are included through the same bounded
readers. Other Adventures are excluded. The source adapter produces display IR;
native writers build fresh typed records from `campaign-schema.json` and
`audio-schema.json`, not byte patches or installed templates. The 5e field
schema comes from the captured fixtures; audio declarations have neutral defaults
with all shipped names, music and byte payloads removed.

Campaign identities include package, source pack and parent Adventure. Shared
campaign notes/media are identical across scene packages and deduplicate in the
combined MyAssets tree. Source objects stay inert in each package's supplemental
`campaign-source-<scope>.json`. The top-level `campaign_content` report counts each
scope once and lists native targets, rewritten link aliases and graded losses.
Scene reports separately list static tiles and omitted token-to-actor links.

- Roll tables: native range rows, including tables unreachable from scenes.
  Source formula, replacement, weight and drawn-state mismatches are reported,
  never repaired. Invalid/overlapping ranges produce a reference note and a
  manual loss. Journal links to converted tables/actors/items become native links.
- Actors: dnd5e NPC/character display stat blocks, tracked HP strings and values,
  active optional defense/save lines, six scores/modifiers, embedded features
  sorted into abilities/actions/reactions/legendary actions, portrait when local.
  Labels/name runs are bold; attack-type/Hit runs italic. No roll is evaluated.
  Effects, automation, resources, slots, actor deltas and ownership remain manual.
  Non-numeric bonuses/calculated AC remain explicit approximations.
- Token links: omitted after Claude's 2026-11-03 Toolkit check showed that adding
  a text/link field changes the map portrait into a note marker. The token
  note/icon/Size files remain identical to the v0.10 writer. Actor notes remain
  available separately; each omitted link is a manual loss. A safe separate
  native actor binding is still unproven.
- Items/spells: 5e block fields and local images; descriptions are inert text,
  rolls/enrichers become text and resolvable UUIDs become native note links.
- Playlists: schema-built `.rwpl`/metadata with reachable song pairs for supplied
  local MP3 or OGG Vorbis. Original encoded bytes and extensions are preserved;
  no encoder or Toolkit ffmpeg is needed. Native MP3/OGG controls were confirmed
  audible by Jeffrey on 2026-11-04 in Toolkit 0.5.1.18. Generated playlist entries
  initialize their Master stem at 80%. Missing, invalid or unsupported tracks
  remain explicit losses. Fades, mode, source volume, looping and channels
  remain manual. Each new playlist still needs its own listening check.
  The current Toolkit-made user playlist and user ArkenAudioMeta declarations
  drive metadata, including `_prevPathIfDeleted` and its inherited member.
  Playlists use `MyAssets/Playlists/<notes folder>/<display name>.rwpl`; songs
  use display-name files under `MyAssets/Audio/Songs/<notes folder>/`.
  Previous shipped-pack metadata was structurally readable but invisible in the
  user's Toolkit and is superseded. New listing/playback remains pending recheck.
- Tiles: static PNG/JPEG/WebP rectangles, calibrated padding/grid coordinates,
  rotation and hidden state. Animated/video, unsafe or missing media produce
  manual losses. Texture offsets/scale, tint/alpha, occlusion, elevation/levels,
  behavior and final display require review. Existing geometry math is unchanged.

All runtime behavior remains unvalidated for this new output. Labels stay off;
Foundry fog/vision and procedural animations remain separate conversion gaps.
Installation remains explicit, add-only and receipt-based; `.rwpl` is now an
accepted native extension and participates in dependency closure. No real
MyAssets installation was part of the original 2026-11-02 file-level check.

The 2026-11-03 corrected check was explicitly installed under new receipts;
see [the recheck evidence](archive/validation/2026-11-03-CAMPAIGN-RECHECK.md).
Generated campaign notes now have an explicit `Campaign-v2-` filename prefix,
allowing edited v1 notes retained by `--keep-changed` to remain untouched.

Stat derivation follows the package's dnd5e 4.3.5 source data: natural/flat AC
uses its stored flat value (natural may add explicit bonuses/shield), equipment
AC uses equipped armor and capped DEX, and attacks use the explicit activity
ability, proficiency and numeric bonuses. Dynamic formulas/effects are reported,
never executed. Boris explicitly specifies natural AC 10 and INT for Claws, so
10/+1 are retained rather than replacing source data with DEX-based guesses.
Languages deduplicate case-insensitively and walk speed appears first.

File-level evidence and per-scene package hashes are in
[the campaign validation report](archive/validation/2026-11-02-CAMPAIGN-CONTENT.md).
Captured heading/body fonts, stat colours and per-character font runs are
preserved structurally; this is not a rendering observation.

## Original staging plan

- **A (no capture needed):** all adventure roll tables → notes with rollable
  table fields; playlist → `ArkenPlaylist` + songs; static map tiles → image
  tiles on the map (same record family as the background); animated
  tiles/videos → loss line until a sample exists.
- **B (formats captured 2026-11-02):** actors → 5e monster notes (and token → stat-block note
  link); items → 5e item notes; actor-embedded attacks/features into the
  stat block.
