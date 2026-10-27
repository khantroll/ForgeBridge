# Fantasy Grounds to Arkenforge map conversion notes

Retrieved 2026-10-27 from public search results. No Fantasy Grounds or Arkenforge build was installed, no FG module was opened, and no tool listed below was run. Several sources were read through search-result text or Reddit mirror pages rather than the original page, and are marked that way.

The question for this spike: is there an existing tool that converts Fantasy Grounds (FG / FGU) maps into Arkenforge? This is a possible second input path for ForgeBridge. The Foundry path in [FOUNDRY.md](FOUNDRY.md) is unchanged.

"Not found" below means this search did not find a public tool, not that a private or unpublished one cannot exist.

## Sources

| Source | What was used | Date |
|---|---|---|
| Arkenforge account on r/VTT, "native Fantasy Grounds Unity export can now handle toggleable doors and windows" ([mirror](https://lr.ggtyler.dev/r/VTT/comments/13erexx/hey_folks_with_our_new_blocking_upgrades_our)) | Arkenforge writes FGU XML (walls, lights, grid, doors, windows); UVTT import plus FGU export is described as a UVTT-to-FGU converter. Also says public FGU format documentation that existed at FGU launch has since disappeared. | Post 2023-05-11. Read via mirror 2026-10-27. |
| [uvtt2fgu README](https://github.com/Imagix/uvtt2fgu/blob/cc9ede6f81dea755656a03f2d65ba5b3fcef7025/README.md) (GitHub, Imagix) | Python 3 tool: Dungeondraft `.dd2vtt` to FGU `.png`/`.jpg` + `.xml` line-of-sight and lighting. Requires FGU 4.1+. | Commit `cc9ede6`. Retrieved 2026-10-27. |
| Trenloe, [FVTT to Fantasy Grounds map export/import](https://www.fantasygrounds.com/forums/archive/index.php/t-85659.html) (FG forums; [Forge item 2340](https://forge.fantasygrounds.com/shop/items/2340/view)) | FG extension importing Foundry-exported scenes into FG, including LoS and lighting. | Thread 2025-08-21. Retrieved 2026-10-27. |
| Arkenforge account on r/VTT, "Use your Arkenforge maps in Foundry with Universal VTT Export" ([mirror](https://redlib.ssps.io/r/VTT/comments/oaueke/use_your_arkenforge_maps_in_foundry_with)) | Arkenforge imports UVTT from Wonderdraft, Dungeondraft and Dungeon Fog. | Reply 2021-07-06. Read via mirror 2026-10-27. |
| Arkenforge account on r/Arkenforge, "Importing UVTT files in layers" ([mirror](https://lr.ggtyler.dev/r/Arkenforge/comments/1fgcvre/importing_uvtt_files_in_layers)) | Quick import puts a UVTT file onto a chosen level of an existing map. | Undated on the mirror ("7d ago"). Read 2026-10-27. |
| ProFantasy forum, [Export lights to Foundry](https://forum.profantasy.com/discussion/comment/120632) | User reports that UVTT walls are consistent across tools but lights are not. | Retrieved 2026-10-27. Forum opinion, not a spec. |
| Arkenforge account on r/VTT ([mirror](https://lr.ggtyler.dev/r/VTT/comments/1aipqe6/another_mapmaking_app_that_might_be_getting_uvtt)) | Arkenforge states Fantasy Grounds now supports UVTT. | Reply 2024-02-05. Read via mirror 2026-10-27. |

The UVTT field list itself is in [ARKENFORGE.md](ARKENFORGE.md) and is not repeated here.

## Finding

No FG → Arkenforge converter was found. Every tool found moves maps **into** Fantasy Grounds:

| Tool | Direction | Notes |
|---|---|---|
| Arkenforge Toolkit FGU export | UVTT / Arkenforge → FGU XML | Native. Walls, lights, grid, toggleable doors, windows. |
| uvtt2fgu | `.dd2vtt` → FGU image + XML | Open source Python. Effectively a written-down UVTT-to-FGU field mapping. |
| Trenloe's FVTT-to-FG extension | Foundry scene → FG map | FG-side extension. Not Arkenforge-related. |
| FG UVTT import | UVTT → FG | Per Arkenforge's 2024 reply. Not confirmed against an FG page in this spike. |

No FG → UVTT exporter was found either. That is the missing piece: once a map is UVTT, Arkenforge already imports it.

## Routes into Arkenforge today

1. **Find the original UVTT.** If an FG map came from a cartographer or a tool that also ships `.dd2vtt` / `.df2vtt` / `.uvtt`, import that file. Arkenforge reads all three.
2. **Image only.** Take the map image out of the FG campaign or module, import it as an image, and re-block walls, doors and lights by hand.
3. **Write FG XML → UVTT.** Not started. See below.

## FG XML → UVTT as a ForgeBridge input

An FGU map is an image plus XML holding occluders (LoS), lights and grid. UVTT is JSON with `line_of_sight`, `portals`, `environment.lights` and `resolution`. uvtt2fgu already performs UVTT → FGU, so reading its source would give the field mapping to invert.

This fits the existing architecture (`Source -> IR -> Arkenforge`): an FG reader would populate the same scene IR the Foundry reader does, and the existing UVTT writer and loss report would be reused.

Expected grades, not yet verified against any file:

| FG element | UVTT target | Expected grade |
|---|---|---|
| Map image | `image` | Native |
| Grid size / offset | `resolution` | Native, if FG grid is square |
| Occluders (walls) | `line_of_sight` | Native |
| Doors, windows | `portals` | Approximate; FG door state and window type need checking |
| Lights | `environment.lights` | Approximate; lighting models differ and UVTT lights are inconsistent across tools |
| Tokens, pins, story links | none | Unsupported in UVTT |

Open questions before any code:

- No public FGU map XML specification was found. Arkenforge said in 2023 that the launch-era documentation was gone. The format would have to be read from uvtt2fgu's writer, Arkenforge's export, and real FG campaign files.
- FG module packaging (`.mod` archives, `db.xml`, image references) has not been reviewed here.
- A test FG map is needed. It should be synthetic or self-made, not a commercial module, matching the fixture policy for Foundry.

## Status

Research only. Parked behind the Foundry path. No FG code, fixtures, or schema changes.
