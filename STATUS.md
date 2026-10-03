# Project Status

**Lifecycle:** UVTT DYNAMIC LIGHTING SLICE  
**Implementation started:** Inventory CLI, importable UVTT, loose scene assets, ambient color, and deterministic AmbientLight range conversion  
**General converter started:** No

The zipped LevelDB scene is the previous state. This slice is the current state. One command writes scene `scene-vault` from `fixtures/synthetic-leveldb-scene.zip` as a UVTT file and copies that scene's PNG and WAV beside it. The unpacked LevelDB scene and the text scene `scene-crypt` still produce the same UVTT object. It is not a general Foundry-to-Arkenforge converter.

## What this slice does

`PYTHONPATH=src python3 -m forgebridge fixtures/synthetic-leveldb-scene.zip --uvtt-scene scene-vault --uvtt-out scene-vault.uvtt`

reads the LevelDB pack inside the zip, prints one JSON object with `uvtt` and `loss_report`, writes only the `uvtt` object to `--uvtt-out`, and writes `crypt.png` and `drip.wav` in the same directory. The UVTT file is the Arkenforge map import. The PNG and WAV are loose files from the import list in [docs/research/ARKENFORGE.md](docs/research/ARKENFORGE.md): JPG, PNG, WEBP, GIF, MP4, M4V, WEBM, MP3, OGG, and WAV. The envelope on stdout is the graded report and is not itself an import file.

Asset types that are not on that list are skipped and graded unsupported. Zip entries whose names leave the archive are not extracted and are not executed.

The UVTT object is unchanged: the core fields on [Arkenforge's UVTT page](https://arkenforge.com/universal-vtt-files/), read 2026-10-03 (`dateModified` 2026-08-22). Notes are in [docs/compatibility/UVTT-SLICE.md](docs/compatibility/UVTT-SLICE.md).

These commands still write a UVTT file. They also write loose image and audio files for the scene they read:

`PYTHONPATH=src python3 -m forgebridge fixtures/synthetic-leveldb-scene --uvtt-scene scene-vault --uvtt-out scene-vault.uvtt`

`PYTHONPATH=src python3 -m forgebridge fixtures/synthetic-module --uvtt-scene scene-crypt --uvtt-out scene-crypt.uvtt`

No `.uvtt` file is stored as a hand-written artifact. Tests run the writer. LevelDB values and scripts are not executed.

## What the earlier work established

Public docs were re-read on 2026-10-03 and written up with citations:

- [docs/research/FOUNDRY.md](docs/research/FOUNDRY.md) — Version 14 document lists, package layout, and the LevelDB key layout used here.
- [docs/research/ARKENFORGE.md](docs/research/ARKENFORGE.md) — import extensions, UVTT fields, v0.5.0.0 / v0.5.1 UI features, and the automation surface that was not found.
- [docs/compatibility/INVENTORY-SPIKE.md](docs/compatibility/INVENTORY-SPIKE.md) — synthetic inventory results, including the LevelDB actor pack.
- [docs/compatibility/UVTT-SLICE.md](docs/compatibility/UVTT-SLICE.md) — the importable UVTT file, the four grades, the LevelDB scene, and the loose image and audio files.

The inventory IR is `schema/inventory-0.1.schema.json`. `fixtures/synthetic-leveldb` is still decoded into the inventory. `fixtures/leveldb-pointer` still fails closed. Unknown fields are retained. Imported JavaScript, macros, HTML, and YAML are not executed.

## Dynamic lighting slice

The current branch translates the deterministic UVTT lighting subset:

- scene ambient hex color -> `environment.ambient_light` when the source stores a hex value directly;
- AmbientLight x/y -> UVTT position in squares;
- AmbientLight color -> UVTT color;
- outer Foundry dim/bright radius -> UVTT range in squares using `grid.distance`;
- separate Foundry bright/dim radii are explicitly graded approximate because UVTT has one range;
- negative Foundry radii (darkness/blackness sources) are reported unsupported and do not receive a fabricated positive range;
- Foundry animation, attenuation, coloration, contrast, luminosity, saturation, and numeric shadow controls remain in the loss report rather than being guessed into UVTT intensity/shadows.

Walls and portals remain the collision/line-of-sight geometry consumed by the target lighting engine.

## Next step

**Validate this lighting slice against a real, legally usable Foundry scene imported into Arkenforge.** Synthetic tests establish the transformation rules; the next useful evidence is whether Arkenforge renders the emitted ambient color, ranges, walls, and portals as expected. Do not add token vision until this scene-lighting validation is complete.

