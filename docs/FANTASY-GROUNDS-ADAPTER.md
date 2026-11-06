# Fantasy Grounds → Arkenforge adapter (reader and native output)

Branch `fantasy-grounds-adapter`, started 2026-11-01. Kept off PR #8 so the
Foundry v0.9 release is unaffected. Builds on the research in PR #9
(`docs/research/FANTASY-GROUNDS.md`): no Fantasy Grounds (FG) → Arkenforge or
FG → UVTT converter exists; every public tool goes the other way.

## Approach

ForgeBridge already turns a UVTT-shaped scene (grid, walls, doors, lights,
image) into a native Arkenforge map and installs it with backup, conflict
review and receipts — proven end to end in the Toolkit on 2026-11-01. So the
Fantasy Grounds path only needs a **reader** that produces that same scene:

```
FG module (.mod or folder)
  └─ fantasy_grounds.py  (read-only)  →  UVTT-shaped scene + loss lines
        ├─ write scene.uvtt           →  Arkenforge Quick Import (works today)
        └─ native map writer + installer (Phase 2; shared geometry writer with Foundry)
```

## What exists now (`src/forgebridge/fantasy_grounds.py`)

- `ModuleSource`: bounded, read-only access to a `.mod` ZIP or unpacked folder;
  requires `definition.xml`; ignores absolute/`..`/symlink entries; refuses
  case-aliased duplicates; size and entry limits.
- XML is parsed with DTD/entity declarations refused.
- `definition()`: module name, display name, author, rulesets.
- `list_images()`: every `type="image"` node in `db.xml`, with record path
  (e.g. `image.id-00001`), record name, bitmap (FGU `<layers><layer><bitmap>`
  first, then classic `<bitmap>`), layer count, pin count.
- `to_uvtt()`: one map → schema-valid UVTT dict + counts + graded losses.
  LoS/lights come from the db.xml image node, else the per-image sidecar
  (`images/<name>.xml`).
- `inventory()` and CLI:
  `python -m forgebridge.fantasy_grounds MODULE` (JSON inventory) or
  `python -m forgebridge.fantasy_grounds MODULE --map image.id-00001 --out map.uvtt`.
- Tests (`tests/test_fantasy_grounds.py`, synthetic module only): geometry
  checked against uvtt2fgu's own grid→FG transform; output validated against
  `schema/uvtt-core.schema.json`; sidecar == db.xml; folder == ZIP; DTD,
  traversal, missing definition, >64 MP and missing grid refused/blocked.

## Field mapping

| FG element | UVTT / Arkenforge | Grade | Notes |
|---|---|---|---|
| Image bitmap (first layer) | `image` / background tile | Native | Extra layers reported, not merged. |
| `<gridsize>w,h` (px) | `pixels_per_grid` | Native | Non-square or fractional → approximate. |
| `<gridoffset>` | — | Approximate | UVTT/Arkenforge grid starts at the image corner; offset reported. |
| Hex/iso grid | — | Unsupported | Reported. |
| Occluder (plain) | `line_of_sight` polyline | Native | `<closed/>` on a wall closes the shape (assumption, see below). |
| Occluder `toggleable` | `portals` (door) | Approximate | Centre line from FG's door rectangle; closed state as saved. |
| `toggleable` + `allow_vision` | `portals`, open | Approximate | Window = see-through portal. |
| `terrain` | — | Unsupported | Movement-only; reported. |
| Light `position` | light position | Native | |
| Light `range b,bf,d,df` (squares) | `range` | Approximate | Larger (dim) radius used; falloff dropped. Arkenforge stores intensity 1.0 anyway. |
| Light `color #AARRGGBB` / `#RRGGBB` | `color` | Native | |
| Light without `<on/>` | written on | Approximate | Reported. |
| Map pins (`<shortcuts>`) | Arkenforge note markers | Manual (Phase 3) | Counted now. |
| Story / encounter text | Arkenforge notes | Manual (Phase 3) | |
| Tokens on maps, NPCs, items | tokens / notes | Manual (Phase 3+) | |

Coordinate transform: FG pixels, origin at the image centre, y up →
UVTT grid units, origin top-left, y down:
`gx = (x + W/2) / ppg`, `gy = (H/2 − y) / ppg`.

## Checked on a real module (2026-11-02)

*Mike's Free Encounters 91 — Gufuhvalur and Isfiskur* (free FGU module,
`definition.xml` version 4.3, release 8.1|CoreRPG:6; supplied by Jeffrey, not
committed). Findings:

- **Coordinates confirmed**: pixels, origin at the image centre, **y up**.
  Drawing the occluders over Ice Caverns matches the cave walls exactly with
  y-up and clearly fails with y-down.
- **Occluders live inside the layer** (`image/layers/layer/occluders`), not on
  the image node. The reader now reads the node and every layer.
- **No `<gridsize>` is stored**, only `<grid>on</grid>`. The grid is 51.2 px
  (40 squares across 2048 px), measured from the "Grid" map images shipped
  beside the module. The reader now accepts `--grid-size PX` or `--squares N`
  and reports a manual loss line; status `NEEDS_GRID` until given.
- Fractional squares: the image is resampled (2048 → 2040 px) so each square is
  a whole 51 px; wall coordinates in squares are unchanged. Checked by drawing
  the generated UVTT's walls over its own image.
- The sidecar `images/Ice Caverns.xml` holds the same occluders clipped to the
  image edge.
- Not every `image` record is a map: five 1024 px creature pictures have grid
  off and no LoS; the inventory labels them `ART`.
- The module also carries encounters (`battle` with `npclist`, FG built-in
  letter tokens) and full 5e NPC stat blocks (`npc`) — Phase 3/4 material.
- No doors or lights in this module, so door/window/light mapping is still
  checked only against uvtt2fgu's writer and the synthetic tests.

## Module locations and protection (2026-11-02)

- FG Unity data folder (default): `%APPDATA%\SmiteWorks\Fantasy Grounds`
  (AppData is hidden in Explorer). Plain modules: `modules\*.mod`.
- Forge/store downloads go to `vault\<guid>.dat`: ZIPs holding one module
  under `modules/<name>/`, with **encrypted entries**. ForgeBridge refuses
  encrypted modules with a clear message and does not attempt to read them.
  It can read the unprotected vault layout (module one folder down).
- Checked on the host: Aladar's Assets Battle Maps Pack 1 and Eldritch Runes:
  Ruins of Zlargkon (vault, encrypted → refused); FG Battle Maps
  (Combat_Battlemaps.mod, v3.1, 41 images) and Well Met in Kith'takharos
  (v2.06, 17 images) are readable but have no LoS/lights (all reported ART).
- Best route for doors/lights test data: draw them on a map in your own FG
  campaign and export it as a module (exported modules are unencrypted).

## Doors, windows and lights checked (2026-11-02)

Arkenforge's own Fantasy Grounds Unity export of a known map read back exactly:
199/199 walls, 23/23 doors (20 doors + 3 open doors as windows, endpoints and
state exact), 66/66 light positions. Arkenforge's exporter shrinks light radius
≈0.88×. See validation/2026-11-02-FG-ARKENFORGE-EXPORT.md.

## Assumptions still to verify

Documented formats cover the per-image metadata XML; their use **inside
db.xml** comes from forum/uvtt2fgu knowledge, not a spec. Before claiming
anything, check on one real FGU module:

1. ~~db.xml frame~~ confirmed (see above). Lights inside layers: assumed like occluders.
2. Doors/windows/lights in a module drawn by hand in FG (checked against Arkenforge's export and uvtt2fgu only).
3. `<closed/>` on a non-toggleable occluder means a closed shape.
4. Doors drawn in FGU are rectangles (uvtt2fgu writes rectangles; FG's own
   drawn doors may be lines — the farthest-pair fallback handles that).
5. Pin `<x>,<y>` frame (same as occluders?) for Phase 3.
6. Encrypted/compiled commercial modules: if `db.xml` is not readable XML, the
   inventory reports it; we do not try to bypass any protection.

## Phases

1. **Reader + UVTT.** Implemented with synthetic tests, the real MFE 91 wall
   layout and Arkenforge's independent FGU door/window/light export. Remaining
   hand-drawn FGU assumptions are listed above; this is not universal format
   compatibility. UVTT remains an available interchange artifact.
2. **Native output — implemented, file-level validation.** Automatic detection
   in convert/discover for .mod, definition.xml folders and unencrypted vault
   ZIPs; shared geometry/background/thumbnail synthesis at 2.56 units/grid.
   Foundry notes/tokens stages are skipped. Existing native install review,
   backups, receipts and uninstall are reused unchanged. GUI includes Choose FG
   module, ART filter, statuses/known pixels per square, per-map grid prompts,
   module-based naming and FG count/loss summaries. CLI supports keyed or
   single-selection --grid-size/--squares; stored grids win. No source-type flag
   is required. Pins/story/tokens remain phase 3+ losses. Synthetic integration
   includes encrypted refusal, fractional resampling, fake install/uninstall
   and native segment counts. Validate one new native output in Toolkit before
   claiming runtime acceptance (Claude owns this; no desktop work by Codex).
3. **Pins and story → notes.** Implemented for the bounded FGU shortcut slice and
   category/reference story records; see Phase 4 below for losses and evidence.
4. **Tokens / NPCs.** Display NPC notes and bounded portrait token placement are
   implemented at file level. Native NPC bindings remain omitted for portrait
   safety; source dialect/alignment and actual token behavior need runtime review.

## What is needed from Jeffrey

- One Fantasy Grounds Unity module you own (ideally one map with line of sight
  and lights drawn in FGU), as a `.mod` file or exported module folder. Not
  committed to the repo; used only to confirm the assumptions list.
- Whether FG Classic modules matter, or FGU only.

## Sources

- FG wiki, [Module - Data Files](https://fantasygroundsunity.atlassian.net/wiki/spaces/FGCP/pages/996644362/Module+Data+File+Overview)
- FG wiki, [Module - Image Line of Sight Data](https://fantasygroundsunity.atlassian.net/wiki/spaces/FGCP/pages/996645681)
- [uvtt2fgu](https://github.com/Imagix/uvtt2fgu) (BSD-3) writer and its
  [FGU XML format wiki page](https://github-wiki-see.page/m/Imagix/uvtt2fgu/wiki/Fantasy-Grounds-Unity-XML-File-Format)

## Phase 4: combined real-module path (2026-11-05, file-level)

`forgebridge convert MODULE --out NEW_DIR` now builds campaign notes and all
selected calibrated maps in one root `native-package.zip`. The GUI uses the same
command path and install review. No selected GUI maps means notes only; CLI can
request this explicitly with `--notes-only`. Maps still need a stored grid or an
explicit `--grid-size KEY=PX` / `--squares KEY=N`; artwork is hidden by default.
Uncalibrated image records remain linked image notes, not arbitrarily scaled maps.

Readers handle transparent repeated category containers and `reference.npcdata`,
`equipmentdata`, `magicrefitemdata`, `magicitemdata`, `spelldata` and reference-page
text blocks. Paragraph/list/frame text and local record links survive as native
note text and links. Typography/table/frame layout is flattened and reported.
Module-qualified references resolve only to that module; external art and links
remain explicit losses. NPC source AC/HP/speed strings, stored saves/skills,
actions/traits/legendary actions and CR/XP are retained. Non-5e NPCs use the native
5e template for display only: their source attacks/saves are preserved, with no
5e proficiency calculation. This is not ruleset automation.

The bounded FGU image shortcut/token slice uses centre-origin, y-up pixels,
converted through the actual source grid to 2.56 native units per square.
Supported pins open converted note targets with labels off. Token portraits,
square size, rotation and hidden state use the existing native token writer.
Duplicate/malformed/missing/external placements are losses. Layer transforms,
combat tracker behavior and unobserved dialects require review. Coordinate
placement is synthetic/file-level evidence until compared inside Toolkit.
A token's NPC-note association is reported but **not embedded**: earlier native
linked-text tests changed portraits into cyan pins. Open the separate NPC note
by name; do not claim an automatic actor binding.

Real inputs are read-only and never committed. The local Well Met module is
**3.5E**, with 17 images (16 ART and one NEEDS_GRID) but no stored grid, pins or placed tokens. Therefore it
cannot supply the requested real pin/token map acceptance case without a new
FG export containing those records and calibrated grids. Its image and story
links can be checked as notes. See the new real-adventure validation report for
counts, graded losses, hashes and the isolated install receipt.
