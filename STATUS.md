# Project Status

**Lifecycle:** UVTT DYNAMIC LIGHTING SLICE  
**Implementation started:** Inventory CLI, importable UVTT, loose scene assets, embedded Adventure scene discovery, ambient color, and deterministic AmbientLight range conversion  
**General converter started:** No

The zipped LevelDB scene is the previous state. This slice is the current state. One command writes scene `scene-vault` from `fixtures/synthetic-leveldb-scene.zip` as a UVTT file and copies that scene's PNG and WAV beside it. The unpacked LevelDB scene and the text scene `scene-crypt` still produce the same UVTT object. It is not a general Foundry-to-Arkenforge converter.

## What this slice does

`PYTHONPATH=src python3 -m forgebridge fixtures/synthetic-leveldb-scene.zip --uvtt-scene scene-vault --uvtt-out scene-vault.uvtt`

reads the LevelDB pack inside the zip, prints one JSON object with `uvtt` and `loss_report`, writes only the `uvtt` object to `--uvtt-out`, and writes `crypt.png` and `drip.wav` in the same directory. The UVTT file is the Arkenforge map import. The PNG and WAV are loose files from the import list in [docs/research/ARKENFORGE.md](docs/research/ARKENFORGE.md): JPG, PNG, WEBP, GIF, MP4, M4V, WEBM, MP3, OGG, and WAV. The envelope on stdout is the graded report and is not itself an import file.

Asset types that are not on that list are skipped and graded unsupported. Zip entries whose names leave the archive are not extracted and are not executed.

The current UVTT object follows the compatibility fixes below, based on the core fields on [Arkenforge's UVTT page](https://arkenforge.com/universal-vtt-files/), read 2026-10-03 (`dateModified` 2026-08-22). Notes are in [docs/compatibility/UVTT-SLICE.md](docs/compatibility/UVTT-SLICE.md).

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

## Real Foundry Adventure scene support

A real Foundry v13 Adventure pack exposed a storage shape the synthetic scene pack did not cover: the pack can contain one top-level `Adventure` document whose `scenes` array contains the actual Scene documents.

The inventory now keeps the parent Adventure and also promotes each embedded Scene into the normal scene inventory. Promoted scenes retain their containing Adventure id/name/source index under `retained_fields._forgebridge_parent_adventure`. `--uvtt-scene SCENE_ID` uses that provenance to reopen the parent Adventure and select the embedded Scene, then sends it through the same Scene -> UVTT path as ordinary scene packs.

Foundry virtual asset paths of the form `modules/<this-package>/...`, `worlds/<this-package>/...`, or `systems/<this-package>/...` may resolve to the corresponding package-local path when the virtual package name matches the package directory. Traversal and symlink protections remain in force.

A synthetic regression covers a two-scene Adventure, parent preservation, scene discovery, provenance, scene selection, wall/light conversion, and package-local virtual background resolution.

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

## Real Arkenforge compatibility validation (2026-10-08)

The user-supplied native UVTT reference and Count's Manor import exposed wire-shape errors. The exporter now writes format 1.0, named point objects, absolute door bounds, top-level lights, native-compatible colors/defaults, and embedded compatible PNGs. Canvas origins derive from scene padding or stored dimensions and apply consistently to walls, doors, and lights. Source-specific constants are not used.

The working test confirmed image compatibility, geometry alignment, editable lights, dynamic illumination, and door switches. Door light blocking required enabling Blocks Light in Arkenforge; this is now a per-portal manual compatibility warning with original restrictions/state recorded. Light movement remains unresolved. Defaults for light intensity/shadows are explicitly approximate.

The full selected scene is now saved in a `.forgebridge.json` companion and included in stdout, preserving skipped lights, restriction settings, and unknown data for future correlation. UVTT does not define the destination's capabilities. The supplied native package demonstrated notes, audio, ambience, and map metadata beyond this interchange subset.

Next: obtain the original Foundry ZIP, regenerate Count's Manor with this writer, verify padding from its actual source, investigate the 16 skipped lights, and compare native map fields for independent blocking/toggle semantics and light positioning. Do not claim those unresolved parts are automatic or verified.
