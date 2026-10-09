# Native Arkenforge notes: observed structure

## Evidence, 2026-10-08

The user supplied a Town MyAssets export. It is private test input, not a repository fixture. `forgebridge.nrbf.inspect_nrbf` successfully consumed all 30 native binary files (`.rwmap`, `.rwnote`, `.rwmeta`, `.rwamb`) in that archive. The map yielded 4,835 object records. Seven note files yielded 27 records each, except one with listener/vision fields yielding 34. All seven map note references matched both note metadata and note files in the archive.

This is successful structural inspection, not proof that arbitrary newly generated files import into Arkenforge. The synthetic writer subsequently passed the user's text/link/table Toolkit test; source conversion still needs runtime validation. Existing UVTT conversion is unchanged.

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

## Controlled sample request (fulfilled)

Create a small new test map and export its pack with linked content included. Add:

1. Two notes named `FB Test A` and `FB Test B`, each with a text field containing distinctive text.
2. A native content link from A to B inside A's text field.
3. A rollable-table field with three outcomes: `FB result one`, `FB result two`, `FB result three`, using unequal ranges/weights if the UI allows.
4. Put A and B on the map, one grid square apart horizontally, and record which note is to the right. This permits position-scale/sign calibration without assuming native units.
5. Leave notes GM-only if the UI allows, and include that setting in the test report.

Upload the exported pack ZIP. The purpose is to establish exact field types, IDs, link encoding, table representation, and a known position delta. That sample has since been supplied; the first native writer/import test is described below. Do not copy unknown token fields into a prose note or infer table serialization from field names alone.

## Foundry reference preservation verified

The user's new Crypt companions contain 19 resolved placed notes and 29 resolved discovered dependency references, with no source read errors or traversal truncation. The retained graph contains five journals (76 pages total) and two tables: Despair (`1d3`, three outcomes) and Nightmare (`1d6`, six outcomes). The readable notes match `render_notes_text` exactly after newline normalization. Every reference source path and target ID was checked, all documents belong to the selected adventure, and the original scene/root journal payloads are unchanged. This verifies the supported traversal, not every possible Foundry link syntax or native import.

## Controlled sample received and first generated files

The later MyAssets ZIP contains native FB Test A/B notes and metadata. A has a text field linking to B and a three-result table (ranges 1–1, 2–2, 3–3); B links back to A. Text is an ArkenTextString wrapping an active List<ArkenTextCharacter>. Each character stores size/alignment/font settings/color and an optional `_link` metadata path. An empty `_visibleToPlayers` list is observed, but its runtime meaning is not yet tested. Rollable rows are `ArkenNoteFieldRollableTableRow` objects with `_from`, `_to`, and `_data` rich text.

The second ZIP includes the note placements in `Maps/Autosave/New Map.rwmap`, while the manually saved map has no test markers. A is at native (13.1831483841, 2.1409082413), B at (17.2942581177, 2.2149820328). B is to A's right; this arbitrary delta does not establish grid scale/sign calibration. Both notes point to their matching metadata files.

`forgebridge.native` uses only fixed observed class/member metadata. It constructs fresh objects, unique field IDs, empty visibility lists matching the sample, and unique test-folder paths. It emits typed NRBF records directly, preserving inherited members, reference identities, typed arrays, and active list sizes. Font-settings value records are inline with negative object IDs, as in the sample. Text is currently plain, with explicit native links, rather than a general HTML conversion. Supported text is limited to 64,000 BMP characters per field; unsupported characters/ranges fail explicitly. No source macros, user assembly code, dice formulas, or HTML are executed.

The first generated artifact contains four files: two `.rwnote`/`.rwmeta` pairs under `MyAssets/Encyclopedia/Notes/ForgeBridgeTests`. A and B link to one another. A has three table outcomes on ranges 1–1, 2–2, 3–3. Metadata has no stale map reference. Empty player lists mirror the exported sample and do not establish a GM-only guarantee. This command does not accept a Foundry package or emit a native map.

All files reparse with the inert inspector and tests verify recovered content, target closure, ranges, repeated inherited members, and archive paths. The user verified text rendering, A/B clicks once the install path matched, and a table roll displaying both Value: 1 and its corresponding text. Permission meanings and save/reload behavior remain unverified. Startup recovery logs showed denied writes under Program Files, not evidence that every installed pack was corrupt.

## Retained source conversion

`forgebridge.native --companion SOURCE.forgebridge.json --out NEW.zip` compiles only retained source documents. Each journal page gets its own target; a journal index links its pages, and a scene index links the 19 source placements. A content-derived folder name and fixed generated basenames are used consistently by files, navigation, rewritten UUIDs and the installation instructions. Map grid positions remain in a report; no `.rwmap` is emitted.

Known dependency statuses are preserved. Pages beyond the original traversal can resolve additional UUIDs against the same retained scoped documents; missing/unsupported references stay literal and are reported. HTML is flattened without executing it; images/PDFs and external HTML links remain explicit references, and non-BMP characters are replaced with reported losses. The original full companion is packaged unchanged. Visibility lists mirror the sample and must be reviewed before player use.

Only replacement tables with `1dN`, contiguous one-value ranges, unit weights and text outcomes become native rollable fields. Titles plus descriptions are preserved; unsupported dice, weights, document draws and without-replacement behavior become reference text. Despair and Nightmare meet this narrow rule. Source-content conversion is not runtime-verified by the synthetic smoke test; manual import/rendering/links/rolls are the next gate.

## Crypt runtime check and calibrated native map copy

The user subsequently verified actual Crypt room/note links, rules links and
table rolls. Missing handout assets remain a known limitation.

The manually saved map export includes three named calibration markers near
the upper-left image corner. The background's centre is (51.2, -53.76); its
4000×4200 PNG represents 40×42 grid squares at 2.56 native units per square.
Thus a source grid point (x, y) maps to (2.56x, -2.56y). The manual markers
approximately confirm this transform; their small placement jitter is not
treated as a scale or shear correction.

`forgebridge.native_map` copies all original binary records except map name,
tile-list array/size/version and next UID. It appends fresh marker wrappers and
preset graphs using source metadata, with unique IDs and preserved inherited
reference identities. Removed calibration markers remain harmless unreachable
records. A reparse comparison verifies all other original objects are unchanged.
Map metadata is renamed separately while retaining shared string definitions.
Exported media and generated notes accompany the separately named copy.

This experiment needs an explicit calibrated transform and a supplied native
marker; it does not create maps from source geometry. The generated Crypt copy
has 19 exact note targets. The user confirmed the markers open their linked descriptions and survive
saving, switching maps and reopening. Source coordinates are preserved.
Visibility is still a manual review, and handout files are still not embedded.

## Label behavior and optional native text

Foundry's core map-note label is a hover label, while always-visible labels are
an optional module enhancement. Arkenforge's v0.5 notes explicitly removed its
older Hover Text field and added map text. The supplied native marker presets
already contain correct `_name`/`_tileName` values, and generated note metadata
contains correct room names. At that stage no native map text object was present in the supplied
archives. The user's lack of a hover tooltip therefore does not prove a missing
marker-name field in our conversion.

Preserve names and source positions by default; persistent labels should be an
opt-in feature. Before implementing native text labels, obtain one current
Map Builder -> Text object in a saved-map export, and compare a freshly placed
native note marker's hover behavior to a converted marker. Do not rely on the
legacy `_tooltipSummary` field as a current label API without runtime evidence.
See STATUS.md for public sources.

## Native map text sample and optional labels

The next saved-map export provides `ArkenTilePresetText`: `_text` is a String,
`_font` is nullable String, `_fontSize` is Single, and outline/style properties
are ordinary primitive/vector members. It shares its position/scale/tint,
blocking and other references with inherited base members, like content links.
The manual sample has `_hidden=True` in both own/inherited fields.

The native map exporter now supports opt-in labels, default off. It clones
this text wrapper/preset graph, changes only title/name, position, UID, sorting
order, level and relevant light/visibility settings, and preserves style/font
size. It uses the same byte-preserving append approach as markers. Labels
remain independent native text objects. Hidden flags are explicitly set, but
Player View is not yet runtime-verified.

Room markers already present by exact note target remain unchanged, including
user-adjusted positions. Duplicate target placements fail explicitly.
Exported native notes are preserved rather than regenerated over user edits.
Re-exporting identifies generated labels by their `ForgeBridge label: ` names;
it replaces them when on and removes them when off, retaining unrelated text.
The export switch is not a new in-Toolkit setting. The supplied sample yielded
19 original markers and 19 generated labels in the separate test map; visual
appearance, editing and save/reload tests are pending.
