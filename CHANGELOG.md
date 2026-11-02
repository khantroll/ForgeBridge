# Changelog

## Unreleased

- Added: Fantasy Grounds .mod/folder/unencrypted-vault detection in convert,
  discovery and GUI, with ART filtering, explicit per-map grids and module-based
  visible naming. Stored grids always win; fractional image resampling is reported.
- Added: FG UVTT geometry through the shared native map/background/thumbnail
  writer and existing reviewed add-only installer/receipts. Source counts,
  metadata source, resampling and graded losses appear in reports/GUI.
- FG pins, story and tokens remain manual; encrypted modules remain refused.
  Native FG runtime acceptance is pending Claude's Toolkit check.
- Fixed: rejected FG module initialization closes its archive immediately,
  including encrypted-input errors surfaced through the GUI.

## v0.10.0 — 2026-11-02

- Added: user-chosen map folder, notes folder and map names (GUI and CLI);
  defaults to the Adventure name and plain scene names; Windows-safe names;
  name clashes reported, never silently renamed.
- Added: PDF handouts rendered into note pages by default (`--pdf`).
- Added: uninstall removes empty folders the install created; re-running on an
  already-uninstalled receipt tidies leftover folders only.
- Fixed: GUI keeps a pointer to the build loss report after installing; PDF
  checkbox falls back to references; clearer "output folder exists" message.
- Docs: rewritten quick start from the first fresh-setup run.
- Details: [release notes](docs/RELEASE-NOTES-v0.10.0.md).

## v0.9.0 — 2026-11-02

First release candidate: Foundry VTT scenes to native Arkenforge maps, notes,
markers and tokens with one command or a GUI; backed-up add-only installer with
uninstall receipts; graded loss report. Details:
[release notes](docs/RELEASE-NOTES-v0.9.0.md).
