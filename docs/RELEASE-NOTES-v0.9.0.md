# ForgeBridge v0.9.0 — Foundry scenes to Arkenforge (candidate)

> Superseded by [v0.10.0](RELEASE-NOTES-v0.10.0.md).

Released 2026-11-02. First release candidate: a new user picks a Foundry VTT
package and gets native Arkenforge maps installed, or a ready MyAssets folder to
copy, with no manual UVTT import, export or calibration.

## What it does

- **One command or a small GUI.** `forgebridge-gui` (or `forgebridge convert
  PACKAGE --out DIR [--install ...]`): discover scenes, pick some, build, review
  the loss report, install.
- **Native maps written directly**: background image, walls, doors (toggleable,
  closed/open state), lights, at the Toolkit's own UVTT-import calibration
  (2.56 units per grid square, image top-left at the origin).
- **Notes and markers**: journals become native notes with images attached and
  internal links rewritten; Foundry map notes become room markers that open
  their note.
- **Tokens** with portrait, size, rotation and hidden state.
- **Safe installation**: refuses while the Toolkit is running, takes a full
  MyAssets backup, adds files only, refuses on any conflict, writes an
  uninstall receipt. `forgebridge install --uninstall RECEIPT [--keep-changed]`
  removes exactly what was added; `--keep-changed` keeps files you changed
  since (opening a note in the Toolkit rewrites it).
- **Graded loss report** for every scene: native / approximate / manual /
  unsupported, with nothing silently dropped.

## Tested

- Foundry v13, the Count's Manor Adventure package (17 scenes × 5e and SA
  Adventures: all 34 build). Arkenforge Toolkit 0.5.1.18, launcher 7.0.0.3,
  Windows 11, Python 3.13 (CI) and 3.14 (host).
- Checked in the Toolkit: Count's Crypt, Manor 1st Floor, Manor 2nd Floor
  (installed with the GUI) and Count's Lair (installed by the owner from a
  fresh clone using only the guide). Geometry alignment, doors and lights,
  tokens including hidden ones, room markers opening notes, player view over
  local streaming, and install → uninstall round trips leaving no original file
  missing.
- CI: Linux and Windows suites plus an installed-package smoke test.

## Known limitations

- Scope is what was tested above. Other Foundry versions, systems and modules
  need their own check; please report results.
- Not converted (reported as losses): actor/NPC stat blocks, items, roll tables,
  playlists and ambient sound, macros and region behaviors (never executed),
  Foundry fog/vision (native manual fog starts covered for players), light
  animation, GIF/FPS setup.
- PDF handouts are kept as references, not note pages (added in v0.10.0).
- Map and notes folders are always named "ForgeBridge…" (configurable from v0.10.0).
- Light colour/intensity uses the Toolkit's own UVTT-import defaults.
- Links to documents outside the selected scenes stay as text.
- Player streaming: use a Chromium-based browser at `http://127.0.0.1/` on the
  same machine if your browser shows a WebRTC "create candidate is failed"
  error.
- **Windows LevelDB quirk (accepted):** on one development PC the test suite
  intermittently failed replacing a LevelDB temp file (`.dbtmp`). It never
  reproduced on clean Windows CI runners or in later runs, and ForgeBridge only
  reads LevelDB from a copy. If you see a `.dbtmp` error, please open an issue
  with the log.

## Getting started

See [USER-GUIDE.md](USER-GUIDE.md) → *Quick start (Windows, new users)*.
