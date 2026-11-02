# Second scene: convert all + install Manor 1st Floor + Toolkit — 2026-11-01

Second end-to-end run of the new-user flow, on a different map size (3000×4000 vs
the Crypt's 4000×4200), from the same Count's Manor package. No manual UVTT
import, export or calibration.

## File-only conversion of every scene (Codex, Windows host, Toolkit closed)

`forgebridge convert` over the whole package, file-only, to
`C:\AMD\fb-convert-all-2026-11-01`. Exit 0. **All 34 scenes BUILT** (17 scenes in
each of the 5e and SA Adventures), **34 unique map names**, counts identical
between 5e and SA. Each scene reports approximate light rendering and manual
environment/fog/vision gaps; no defect needing a code change.

| Scene | Walls | Doors | Lights |
|---|---:|---:|---:|
| Manor - 1st Floor | 164 | 12 | 24 |
| Manor - 2nd Floor | 56 | 7 | 18 |
| Manor - 3rd Floor | 49 | 12 | 4 |
| Manor - 4th Floor | 41 | 6 | 1 |
| Count's Lair | 137 | 12 | 17 |
| Count's Crypt | 199 | 23 | 66 |
| Ritual Chamber - M | 4 | 0 | 13 |
| Crypt Tomb - M | 4 | 0 | 2 |
| Counts Lair - M | 4 | 0 | 2 |
| Dungeon Cell - M | 4 | 0 | 2 |
| Carriage - M | 4 | 0 | 2 |
| Crypt Hall - M | 4 | 0 | 3 |
| Crypt Stair Case - M | 4 | 0 | 2 |
| Main Hall - M | 4 | 0 | 8 |
| Dining Hall - M | 24 | 0 | 11 |
| Count's Manor - M | 4 | 0 | 5 |
| Conservatory - M | 10 | 0 | 7 |

Cross-checked against the Foundry source (adventure-5e): door and light counts
match for all 17 scenes. Source wall counts are a few higher on the large maps
(e.g. Manor 1st 171 non-door walls → 164), the same reduction the Toolkit's own
UVTT import showed for the Crypt (206 → 199, record-for-record identical in
2026-11-01-DIRECT-MAP.md). Source tokens/notes per scene: Crypt 10/19, Lair 11/12,
Manor 1st 0/6, 2nd 1/5, 3rd 2/5, 4th 3/6; the "- M" scenes 0–1 tokens.

## Install of Manor - 1st Floor (Codex)

`forgebridge convert … --scene-key 26fe7bc9460ca8562a8cf344 --out
C:\AMD\fb-convert-manor1-2026-11-01 --install --myassets "C:\Program Files
(x86)\ArkenforgeData\MyAssets" --backup-root C:\AMD\fb-backups`

Exit 0. PASS: **134 files added**, receipt COMPLETE, no refusals. Backup:
`C:\AMD\fb-backups\forgebridge-4a161e1c38c946e3817990db6ca73293\MyAssets`.
The Crypt receipt from the first install is preserved; both are needed for the
uninstall test (NEXT-STEPS step 4).

## Installed file check (Claude, read-only)

`Maps\ForgeBridge\ForgeBridge Manor - 1st Floor - 5945cbca77.rwmap` (223,721 B)
parsed with ForgeBridge's NRBF reader: **164 walls, 12 doors, 24 light sources,
1 background image tile, 6 content-link markers** (Foyer, Main Hall, Cloak Room,
Dining Room, Kitchen & Pantry, Den). The Foundry source scene has **0 tokens and
6 notes**, so 0 tokens / 6 markers is complete. (Stoker belongs to another scene.)

## Toolkit 0.5.1.18 runtime (Claude)

- Map Browser → ForgeBridge → **ForgeBridge Manor - 1st Floor - 5945cbca77**, with
  a real background thumbnail, creator ForgeBridge.
- Opens cleanly. Walls follow the drawn walls of every room and the outer garden
  wall; doors sit in each doorway, including the double front gate; lights sit on
  the drawn sconces/fireplaces and render warm pools. Alignment correct at a
  second map size → computed 2.56-units/grid upper-left calibration confirmed.
- Six room-marker icons present. Selecting one shows **Den**; double-clicking it
  opens the linked note **"2. Manor — Den"** with its Journal link and page text.
- Player view: stream 1280×720 / 15 FPS, built-in browser at `http://127.0.0.1/`.
  First shows "Fog of war is active!" (fresh manual fog, as documented). After
  session-only *Clear all fog* and **Mirror DM view**, players see the whole lit
  manor with no walls, door handles, lights or markers drawn. No ICE exception;
  the page logs its own `supportsSetCodecPreferences` reference error, which does
  not interrupt the stream.
- Stopped projecting, quit, answered **No** to "save before exiting". The
  installed `.rwmap`/`.rwmeta` sizes and modification times are unchanged
  afterwards.

## Notes

- "match player view to DM view" did not move the player camera this session;
  the Player screen panel's **Mirror DM view** checkbox did. Prefer it in docs.
- Selecting a marker then clicking the first toolbar icon selects the tile under
  it (background); it does not open the note. Double-click the marker instead.
- Door open/close blocking in the player view was not re-run on this map; it is
  the same record shape verified on the Crypt and the earlier direct Manor map.
