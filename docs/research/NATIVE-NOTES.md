# Native Arkenforge notes: observed structure

## Evidence, 2026-10-08

The user supplied a Town MyAssets export. It is private test input, not a repository fixture. `forgebridge.nrbf.inspect_nrbf` successfully consumed all 30 native binary files (`.rwmap`, `.rwnote`, `.rwmeta`, `.rwamb`) in that archive. The map yielded 4,835 object records. Seven note files yielded 27 records each, except one with listener/vision fields yielding 34. All seven map note references matched both note metadata and note files in the archive.

This is successful structural inspection, not proof that newly generated files import into Arkenforge. No native writer exists yet. Existing UVTT conversion is unchanged.

## Format reader

The framing and record grammar follow [Microsoft MS-NRBF](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nrbf/954a0657-b901-4813-9398-4ec732fe8b32). Class metadata follows [ClassWithMembersAndTypes](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nrbf/847b0b6a-86af-4203-8ed0-f84345f845b9).

The reader returns an inert graph: root ID, object table, and library names. Classes are dictionaries with names and members; references retain object IDs; byte arrays remain bytes. No CLR assembly is loaded, no constructor or callback is invoked, and graph cycles are not recursively expanded. Input bytes, records, item counts, and nesting depth are bounded. Truncated input, invalid IDs/counts/null runs, unsupported records, missing references, and trailing bytes fail explicitly. This is a deliberately limited research reader, not a complete NRBF implementation or a serialization API.

Example, using a local file already exported by the user:

```python
from pathlib import Path
from forgebridge.nrbf import inspect_nrbf

graph = inspect_nrbf(Path('example.rwnote').read_bytes())
root = graph['objects'][graph['root_id']]
print(root['class'], list(root['members']))
```

## Observed objects

| Purpose | Observed representation | Limits of evidence |
| --- | --- | --- |
| Note contents | `ArkenNoteUpgrade`, including `_name`, `_aliases`, `_tags`, `_tooltipSummary`, `_noteIcon`, `_noteFields`, `nextUID` | Seven token notes; no prose or table field |
| Note field hierarchy | `ArkenNoteFieldCategory._content` → `KVPOrderedList<ArkenNoteField>` entries with `_order` and `_value` | Field inheritance repeats base members; do not discard them |
| Field visibility/identity | `_visibleToPlayers`, `_UID`, and inherited `ArkenNoteField+...` members | Defaults observed, permission conversion not established |
| Observed field classes | Icon, Size; Listener and Vision on one note | No text, internal-link, or roll-table class observed |
| Map marker | `ArkenTilePresetContentLink` | Seven note markers and two ambience markers |
| Marker target | `_contentType == 'note'`, `_contentBasePath` pointing to note `.rwmeta` | Target is metadata, not directly `.rwnote` |
| Marker location | `_position` → `SVector2(x,y)`, `_mapLevel`, `_hidden`, `_uID` | Coordinate units/origin relative to imported UVTT not calibrated |
| Marker appearance | `_tilePath` points to media metadata, plus scale/pivot/tint | Appearance references separate media assets |

The note files and their metadata share a base path. The map root is `ArkenMapUpgrade`; placements are associated with its tile graph. `_embeddedLinks` exists but contained no `EmbeddedLink` instances in this sample; it is not the demonstrated mechanism for these seven map markers.

## Required controlled sample

Create a small new test map and export its pack with linked content included. Add:

1. Two notes named `FB Test A` and `FB Test B`, each with a text field containing distinctive text.
2. A native content link from A to B inside A's text field.
3. A rollable-table field with three outcomes: `FB result one`, `FB result two`, `FB result three`, using unequal ranges/weights if the UI allows.
4. Put A and B on the map, one grid square apart horizontally, and record which note is to the right. This permits position-scale/sign calibration without assuming native units.
5. Leave notes GM-only if the UI allows, and include that setting in the test report.

Upload the exported pack ZIP. The purpose is to establish exact field types, IDs, link encoding, table representation, and a known position delta. Only then implement a native writer and request an Arkenforge import test. Do not copy unknown token fields into a prose note or infer table serialization from field names alone.

## Foundry reference preservation verified

The user's new Crypt companions contain 19 resolved placed notes and 29 resolved discovered dependency references, with no source read errors or traversal truncation. The retained graph contains five journals (76 pages total) and two tables: Despair (`1d3`, three outcomes) and Nightmare (`1d6`, six outcomes). The readable notes match `render_notes_text` exactly after newline normalization. Every reference source path and target ID was checked, all documents belong to the selected adventure, and the original scene/root journal payloads are unchanged. This verifies the supported traversal, not every possible Foundry link syntax or native import.
