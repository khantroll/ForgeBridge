# Visible naming and PDF handouts — file-level checks, 2026-11-02

Branch: naming-and-pdf, based on main e5b9f2c. No Toolkit launch, real MyAssets
access, installation, or runtime acceptance in this work. Geometry formulas,
calibration, labels-off behavior, token/media scopes and uninstall receipt rules
are unchanged.

## Release checkpoint

Annotated tag v0.9.0 was pushed before implementation. Tag object:
35a0f3f53dbf4a2d04dc80254df8c3c0b3764d7c; peeled commit:
e5b9f2c9a24671e7395db35be1d59619965578cf. No content changes on main.
gh was unavailable on PATH, so no GitHub pre-release was created.

## Automated evidence

PASS: full local Windows/Python 3.14 suite: **244 run, 240 passed, four skipped**,
125.409s. Skips are Windows symlink-creation privilege checks, not passed checks.
Tests include defaults, stripped characters, reserved names and 81-character
rejection; keyed overrides; case-insensitive map clashes within builds/packages
and against a fake destination; matching map/metadata names; scene-scoped notes
in shared visible folders; unchanged media scopes; PDF import/default/fallback
selection; real bounded PDF pages through convert; and headless GUI fields,
renaming, PDF checkbox and review-before-install refusal.

Legacy export/profile rehearsals retain identical shared control-map deduplication.
Strict visible-name conflicts apply to named generated scene maps, without
weakening existing add-only conflicts or receipt checks. Names and actual paths
are reported. Shared notes folders use scene-scoped filenames, not renamed note
titles, to preserve independent marker/link targets. PDF rendering uses existing
page, image and byte limits. No new dependency is added.

The first development suite exposed legacy shared-control compatibility plus
an obsolete hard-coded folder assertion and the static dynamic-import guard;
these were corrected, targeted checks passed, and the final full suite passed.
No LevelDB investigation/retries or security changes.

## Real Count's Lair (5e)

PASS, exit 0:

```powershell
$env:PYTHONPATH='src'
python -m forgebridge convert "C:\AMD\lob-counts_manor-pk-v13\ForgeBridge\lob-counts_manor-pk-v13" --scene-key 28b08edf2e1148dd7e2e02c8 --out .test-tmp/counts-lair-naming-pdf-2026-11-02
```

Map: MyAssets/Maps/The Count's Manor/Count's Lair.rwmap. Both map and metadata
decode to the name Count's Lair. Visible notes folder: The Count's Manor.
10 original PDF documents produce **17 ordered PDF page-image attachments** in
notes. Output includes 49 notes, 12 room markers, 11 tokens, no rejected tokens;
229 native metadata references close. Seven unresolved source-link occurrences
remain explicit. Originals/reports are retained outside MyAssets. Output was
not installed and does not establish Toolkit rendering/readability behavior.

Hashes and PDF document/page counts are in
2026-11-02-naming-pdf-file-results.json. Claude still needs to check the new visible
folders/map naming and PDF page display/order in Toolkit. Existing runtime
acceptance belongs to the prior release evidence, not this build.

## Toolkit check (Claude, 2026-11-02 ~11:12, Toolkit 0.5.1.18)

Installed by Codex from `naming-and-pdf` with default names (exit 0, 244 files
added, receipt `C:\AMD\fb-backups\forgebridge-a76ddb8ad1d14cfb94d75a103e26689e\uninstall.json`).

- Map Browser: folder **The Count's Manor** → map **Count's Lair** (no
  "ForgeBridge" prefix, no hash); opens with edit counter 0/0, title bar
  "Count's Lair".
- Notes library: folder **The Count's Manor**; notes listed by their journal
  names ("Count's Lair — Start Here", "4. Lair & Dungeon — Steps to Lair", …);
  the hash prefix on note file names is not shown.
- **PDF handouts**: a "PDF Handouts" document with 10 notes (letters, Count's
  Journal, Court of Ravenloft, Arcane Tome, Night of Darkness, …). Opening
  "Letter - To Count from Strahd" shows the rendered page image (signature
  "Strahd von Zarovich", red wax seal).
- Found while looking: the Notes library still lists the `ForgeBridge-…` note
  folders from earlier installs. Uninstall removed their files but left the
  folders. Fixed: uninstall now removes folders the install created when they
  are empty, and re-running `--uninstall` on an already-uninstalled receipt
  tidies those folders without touching files (tests added).
- The Toolkit was left open (a desktop window covered its exit dialog); quit it
  with **No** to saving before uninstalling.
