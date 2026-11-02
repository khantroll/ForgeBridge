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

## Plan

- **A (no capture needed):** all adventure roll tables → notes with rollable
  table fields; playlist → `ArkenPlaylist` + songs; static map tiles → image
  tiles on the map (same record family as the background); animated
  tiles/videos → loss line until a sample exists.
- **B (formats captured 2026-11-02):** actors → 5e monster notes (and token → stat-block note
  link); items → 5e item notes; actor-embedded attacks/features into the
  stat block.
