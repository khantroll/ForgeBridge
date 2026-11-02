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

## Still needs the Toolkit (capture before the trial ends)

- **5e monster/character note**: the 5e templates are compiled into the Toolkit
  (not files). Create one note from the 5e monster template, fill HP, AC,
  abilities and one attack, save, read the `.rwnote`.
- **5e item note**: same with the item template.
- Validation of every new writer on one installed scene.

## Plan

- **A (no capture needed):** all adventure roll tables → notes with rollable
  table fields; playlist → `ArkenPlaylist` + songs; static map tiles → image
  tiles on the map (same record family as the background); animated
  tiles/videos → loss line until a sample exists.
- **B (after capture):** actors → 5e monster notes (and token → stat-block note
  link); items → 5e item notes; actor-embedded attacks/features into the
  stat block.
