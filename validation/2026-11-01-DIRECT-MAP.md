# Direct native map synthesis (no Toolkit import) — 2026-11-01

Goal (docs/NEXT-STEPS.md A0): write the Arkenforge `.rwmap` straight from the
Foundry scene, removing the manual UVTT import → export → calibration step.

## Result: PASS for Count's Crypt (first scene)

`forgebridge.native_scene.synthesize_map` generated
**ForgeBridge Direct Crypt 2026-11-01** from ForgeBridge's UVTT for Foundry scene
`fP7VKkP46gQPED6X` (Count's Crypt, 4000×4200, 100 px grid). No Toolkit import.

File-level, compared record-by-record with the Toolkit's own import of the same
scene (`ForgeBridge Profile Crypt 2026-10-16`):

| Records | Generated | Toolkit import | Mismatches |
|---|---:|---:|---:|
| Walls (position, endpoints, light/vision/movement blocking) | 199 | 199 | 0 |
| Doors (endpoints, toggleable, closed/open state) | 23 | 23 | 0 |
| Lights (position, radius, intensity, on) | 66 | 66 | 0 |
| Background tile (centre, scale, sprite width) | 1 | 1 | 0 |

Runtime (Toolkit 0.5.1.18): installed as 4 new files (add-only; no existing
file touched), launched Toolkit normally. The map appears in the Map Browser,
opens with edit counter 0/0, background correctly placed, walls on the drawn
walls, door markers in doorways (red closed / green open), lights rendering.
One door toggled closed → open. Closed without saving.

## Calibration is computed

2.56 native units per grid square; image upper-left at (0, 0); y up. Image tile
centre = (W·2.56/2, −H·2.56/2) in squares; tile scale = 256 / pixels_per_grid;
sprite width = longer side in px. Toolkit stores light intensity 1.0 and its own
default light colour regardless of UVTT values; the writer does the same.

## How it works

Blank container: the user's own empty map (`New Map.rwmap`). Record shapes
(Barrier wall, Barrier door, Light Source, image tile) are cloned from any map in
the user's MyAssets that was created by a Toolkit UVTT import — no Arkenforge
files ship with ForgeBridge. Background asset = PNG in a cloned
`ArkenTileUpgrade` pair under `MyAssets/Media/Cartographer/Quick Import/<map>/`
(16 MP note-image cap raised to 64 MP for backgrounds). The NRBF writer gained
primitive-array and extra primitive types needed for new class definitions.

## Installed files (remove these four to uninstall)

- `MyAssets/Maps/ForgeBridge Direct Crypt 2026-11-01.rwmap` / `.rwmeta`
- `MyAssets/Media/Cartographer/Quick Import/ForgeBridge Direct Crypt 2026-11-01/Counts_Crypt_40x42.rwfile` / `.rwmeta`

## Not yet done

- Second scene with a different size (Manor 1st floor) — required by A0.
- Map-browser thumbnail is blank (copied from the empty map's metadata).
- Notes, room markers and tokens are not yet added to a synthesized map (the
  existing marker/token writers should apply unchanged; untested).
- A new user with **no** UVTT-imported map in MyAssets has no record templates.
  Next: generate the four record shapes from a schema in code instead of cloning.
- Tests: geometry/transform unit tests only; an end-to-end fixture test needs a
  synthetic template map.
