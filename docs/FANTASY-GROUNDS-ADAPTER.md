# Fantasy Grounds → Arkenforge adapter (groundwork)

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
        └─ native map writer + installer (Phase 2; same code as Foundry)
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

## Assumptions to verify on a real module

Documented formats cover the per-image metadata XML; their use **inside
db.xml** comes from forum/uvtt2fgu knowledge, not a spec. Before claiming
anything, check on one real FGU module:

1. db.xml image nodes carry `<gridsize>`, `<occluders>`, `<lights>` with the
   same names and coordinate frame as the sidecar.
2. Centre-origin/y-up applies to db.xml (sidecar documented; db.xml assumed).
3. `<closed/>` on a non-toggleable occluder means a closed shape.
4. Doors drawn in FGU are rectangles (uvtt2fgu writes rectangles; FG's own
   drawn doors may be lines — the farthest-pair fallback handles that).
5. Pin `<x>,<y>` frame (same as occluders?) for Phase 3.
6. Encrypted/compiled commercial modules: if `db.xml` is not readable XML, the
   inventory reports it; we do not try to bypass any protection.

## Phases

1. **Reader + UVTT (this branch).** Done for synthetic data. Needs one real
   module to confirm the assumptions above. Output can be imported in the
   Toolkit via Quick Import today.
2. **Native output.** Feed `to_uvtt()` into the existing native map synthesis
   and installer (`convert` gains `--source fantasy-grounds`, GUI gains "Choose
   FG module"). Validate one map in the Toolkit (needs a Toolkit licence or
   trial).
3. **Pins and story → notes.** Map pins to Arkenforge note markers; FG
   `formattedtext` to native notes via the existing notes writer.
4. **Tokens / NPCs** — after 3, same as the Foundry M3 plan.

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
