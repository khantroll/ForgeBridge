# GUI install by the maintainer — Manor 2nd Floor — 2026-11-01

First run of the GUI by the project owner (not an agent). `forgebridge-gui` on the
Windows host, Toolkit closed.

1. Choose folder → `C:/AMD/lob-counts_manor-pk-v13/ForgeBridge/lob-counts_manor-pk-v13`
2. Discover scenes → 34 rows (5e + SA); selected **Manor - 2nd Floor**
   (packs/adventure-5e, Adventure N63YevXMYeDZPCMh) only.
3. Choose output parent → `C:\AMD\ForgeBridge-output-7a35fcc2`
4. Build / export → PASS, 1 scene BUILT. Native package: 46 notes, 41 journal
   pages, 5 map-note references, 19 image attachments/assets, 1 native token,
   0 unsupported tokens; 2 unresolved UUID occurrences.
5. Install reviewed native outputs → MyAssets `C:\Program Files
   (x86)\ArkenforgeData\MyAssets`, backups `C:\AMD\fb-backups` →
   **status PASS, added 138**, receipt
   `C:\AMD\fb-backups\forgebridge-e379c4260f2943a1afcf264ff00a85b4\uninstall.json`.

No errors or terminal steps beyond starting the GUI.

## Installed file check (Claude, read-only)

`Maps\ForgeBridge\ForgeBridge Manor - 2nd Floor - 37d63c4388.rwmap` (101,775 B):
**56 walls, 7 doors, 18 light sources, 1 background, 6 content links** — markers
Upper Hall, Servant's Quarters, Library, Secret Room, Conservatory, and token
**Stoker**. Matches the source scene (7 doors, 18 lights, 1 token, 5 notes) and
Codex's all-scene build table.

## Toolkit 0.5.1.18 runtime (Claude, after the desktop app restarted)

- Map Browser → ForgeBridge → **ForgeBridge Manor - 2nd Floor - 37d63c4388**;
  opens with edit 0/0.
- Walls follow every room and the garden wall; all 7 doors sit in doorways; lights
  on the drawn fixtures. Third map size aligned by computed calibration.
- **Stoker** token present in the drawing room: portrait, one grid square,
  visible (source: hidden False, width 1).
- Five room markers present; selecting them shows Servant's Quarters and
  Conservatory. Double-click did **not** open the note window this session (it did
  on Manor 1st); repeated attempts only selected the marker/background and raised
  the edit counter. File check: every marker/token `_contentBasePath`
  (D000-P007…P011, ForgeBridgeTokens/07ddd1d8…) exists in MyAssets. Treat as a
  UI-input issue, not a link defect; re-check by hand when convenient.
- Player view (built-in browser, 1280×720/15): after session-only Clear all fog +
  Mirror DM view, players see the whole lit floor; no ICE exception.
- Stopped projecting; quit; **No** to save. Map files unchanged afterwards.

## UX notes for the GUI

- Discover selects all 34 rows by default; a new user must click one row to narrow
  it. Consider selecting none, or grouping by Adventure (5e vs SA).
- Rows show the Adventure id, not its name ("5e"/"SA"), so the two copies of each
  scene are only distinguishable by pack path.
