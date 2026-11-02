# ForgeBridge v0.10.0 — names you choose, PDF handouts, cleaner uninstall

Released 2026-11-02. Builds on [v0.9.0](RELEASE-NOTES-v0.9.0.md); everything
there still applies unless changed below. See [CHANGELOG](../CHANGELOG.md).

## New

- **Choose the names Arkenforge shows.** By default, maps go in a folder named
  after the Adventure (e.g. *The Count's Manor*) instead of *ForgeBridge*, and
  each map is called by its scene name (*Count's Lair*), with no prefix or hash.
  - GUI: **Map folder** and **Notes folder** fields (pre-filled after Discover),
    and **Rename selected maps** / double-click a scene to rename its map.
  - CLI: `--map-folder NAME`, `--notes-folder NAME`, `--map-name SCENE_KEY=NAME`.
  - Names are cleaned for Windows (no `<>:"/\|?*`, no reserved names, 1–80
    characters). Two maps with the same name, in one build or already in
    MyAssets, are reported as a conflict to rename; nothing is renamed silently.
- **PDF handouts become note pages.** Letters, journals and other PDF handouts
  are rendered into notes (Count's Lair: 10 PDFs → 17 pages). On by default
  when the PDF renderer is available; otherwise they stay references with a
  loss line. GUI checkbox *Convert PDF handouts into note pages*; CLI
  `--pdf pages|references`.
- **Uninstall removes the empty folders it created.** Folders that still hold
  kept or later files stay. Running `--uninstall` again on a receipt that was
  already uninstalled only tidies such empty folders (clears the leftover
  *ForgeBridge-…* note folders from v0.9.0 installs); it never deletes files.

## Fixed / improved

- The GUI no longer hides the build loss report after installing; it points to
  `conversion-report.json`.
- The PDF checkbox falls back to references instead of failing when the PDF
  renderer is missing.
- Clearer message when an output folder already exists.
- Quick start in the user guide rewritten after the first fresh-setup run
  (`cd` into the clone, `py -m venv`, `pip install .`, `forgebridge-gui`).

## Tested

In addition to v0.9.0's checks: Count's Lair installed with default names on
Arkenforge Toolkit 0.5.1.18 — map under *The Count's Manor → Count's Lair*,
notes under *The Count's Manor* with their journal names, and the *PDF
Handouts* notes showing the rendered pages (e.g. the Strahd letter). CI: Linux
and Windows suites, installed-package smoke test.

## Known limitations

Same as [v0.9.0](RELEASE-NOTES-v0.9.0.md#known-limitations), except that PDF
handouts and folder/map names are now handled as above. Unchanged: actor/NPC
stat blocks, items, roll tables, playlists/ambient sound, macros, Foundry
fog/vision and light animation are not converted; light colour/intensity uses
the Toolkit's UVTT-import defaults; links outside the selected scenes stay as
text; the Windows LevelDB `.dbtmp` quirk is accepted and documented.

## Upgrading from v0.9.0

```powershell
cd <your ForgeBridge folder>
git fetch
git checkout v0.10.0
python -m pip install .
```

Maps you installed with v0.9.0 keep their old *ForgeBridge* names; uninstall
them with their receipts if you want to reinstall under the new names.

## In progress (not in this release)

Fantasy Grounds Unity modules as a second input, on branch
`fantasy-grounds-adapter`: reads maps, walls, doors and lights into UVTT;
checked on one real FGU module.
