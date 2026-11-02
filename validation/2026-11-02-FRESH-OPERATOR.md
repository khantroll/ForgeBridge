# Fresh-operator run by Jeffrey — 2026-11-02 (in progress)

Fresh clone to `C:\AMD\fb-fresh`, following docs/USER-GUIDE.md without help.

## Findings so far (all fixed in the guide unless noted)

1. `git clone` creates a `ForgeBridge` subfolder; the guide never said to `cd`
   into it, so `git checkout` failed ("not a git repository").
2. The guide hard-coded `py -3.13`; the host has only Python 3.14, so the venv was
   never created and activation then failed. Now `py -m venv .venv`, with a
   `py --list` fallback.
3. The guide led new users down the developer path (`PYTHONPATH`, raw JSON
   report) instead of `pip install .` + `forgebridge-gui`. Split into
   *Quick start* and *Developer setup*.
4. Re-running the self-check failed with "Choose a new output directory under an
   existing parent" because the folder already existed. Message now says the
   folder exists and ForgeBridge never overwrites (`convert.py`).
5. Pasting the ```powershell fence line into PowerShell errors. Guide now says to
   type each line, not the fences.
6. The synthetic self-check prints ~900 lines of JSON. Left as is (CI and tests
   parse it); the guide now tells users to look for "status": "PASS".

## After the guide fixes (4672afa)

`git pull`, `py -m venv .venv` (Python 3.14), `Activate.ps1`, `python -m pip
install .` (built and installed forgebridge 0.9.0.dev0 with cp314 wheels), then
`forgebridge-gui`: all worked first time, no help.

GUI: Count's Lair (adventure-5e) → build → install: **status PASS, added 210**,
receipt `C:\AMD\fb-backups\forgebridge-ffad50b2d54c457f9b65d790473d38cb\uninstall.json`.

7. The install result replaced the build loss report in the GUI text box, so the
   operator lost sight of it. It is still in the output folder's
   `conversion-report.json`; the GUI now says so after installing.

## Build report (conversion-report.json from the operator's output folder)

Count's Lair (adventure-5e): PASS / BUILT. 137 walls, 12 doors, 17 lights, 1
background; **11 tokens converted, 0 rejected** (hidden flags carried); **12 room
markers placed, 0 unplaced**; 49 notes (45 journal pages, 3 documents); 36 image
attachments; 26 internal links rewritten.

Reported gaps, all listed in the report:
- 7 links point to journal pages / a roll table outside this scene's dependency
  set (`missing_document`): left as text, not invented.
- 10 PDF handouts (letters, the Count's journal, etc.) are reference-only: the
  default `convert`/GUI path has no PDF-page option, so they are not rendered
  into notes. Follow-up: expose PDF pages in convert/GUI (pypdfium2 is already a
  dependency).

## Toolkit check (operator, Toolkit 0.5.1.18)

Map "ForgeBridge Count's Lair - eb6e39d18d": walls follow the drawn stonework,
doors in doorways (red closed markers), lights on braziers, hidden tokens shown
with the hidden (eye-slash) badge. **Marker → note works**: the marker opened
"4. Lair & Dungeon — Steps to Lair" with its journal link, page text and an
internal link ("Stairs to the Count's Lair"). This closes the marker→note
re-check from Manor 2nd Floor (an input problem on the agent side, not a
conversion defect). Quit without saving (edit counter 4/0).

Remaining: uninstall with `--keep-changed` following only the guide.
