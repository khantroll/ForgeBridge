# GUI install by Jeffrey — Manor 2nd Floor — 2026-11-01

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

## Toolkit runtime

Pending: the connection to the PC dropped while the Toolkit was launching.
Remaining: open the map, check alignment, Stoker token, a marker note, player view;
quit without saving.

## UX notes for the GUI

- Discover selects all 34 rows by default; a new user must click one row to narrow
  it. Consider selecting none, or grouping by Adventure (5e vs SA).
- Rows show the Adventure id, not its name ("5e"/"SA"), so the two copies of each
  scene are only distinguishable by pack path.
