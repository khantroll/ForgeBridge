# Arkenforge UVTT compatibility slice

ForgeBridge exports one selected Foundry scene to UVTT, copies its referenced loose media beside the output, and saves the complete selected source scene in a `.forgebridge.json` companion. UVTT is a useful compatibility layer, not the ceiling of the converter's intended feature support.

```bash
python3 -m pip install -r requirements.txt
PYTHONPATH=src python3 -m forgebridge fixtures/synthetic-module --uvtt-scene scene-crypt --uvtt-out scene-crypt.uvtt
PYTHONPATH=src python3 -m unittest discover -s tests
```

Stdout contains `uvtt`, `loss_report`, `source_scene`, and `scene_notes`. Import the `.uvtt` file into Arkenforge. The companion JSON is ForgeBridge preservation data, not an Arkenforge import file. It retains full wall restrictions, light configurations (including skipped lights), notes/tokens/audio references, flags, and other selected scene data without inventory truncation. Script strings may be retained as inert JSON; they are never executed. Linked journal data is now correlated as described below; actor document correlation remains future work.

## Evidence from the real import, 2026-10-08

The original Count's Manor export used numeric point arrays, relative door bounds, nested lights, and a format placeholder. The map image was WEBP. A user-supplied native Arkenforge `Town.uvtt` provided concrete wire examples; the accompanying native package contains notes, audio, ambience, and map metadata beyond UVTT. Neither reference establishes a feature ceiling.

The corrected test used an RGBA PNG, translated coordinates, named points, absolute portal bounds, top-level lights, opaque ARGB colors, and native-export lighting defaults. In Arkenforge v0.5.1.17, the user confirmed successful image import, aligned walls and doors, selectable/editable lights after ungrouping, visible dynamic illumination, and responsive door switches. Enabling a door's **Blocks Light** property made it block the light. The tested entrance portals had that property disabled, matching their source light=0 setting; enabling it was an override of the original behavior.

This verifies the test's geometry and rendering structure, not every source setting. The subsequent fresh export test confirmed that illumination moves with its light source. The subsequent full source report confirmed padding 0.25 and identified all 16 skipped lights as valid unset-tint lights; these now export as neutral white with an approximation warning. The two entrance portals have source light=0 and sight=0, so their lack of blocking was intentional.

## Emitted structure

| Field | Writer behavior |
|---|---|
| `format` | `1.0`, as in the native reference |
| `resolution` | Unpadded scene width/height in squares, origin zero, grid pixels per square |
| `line_of_sight` | Arrays of named `{x, y}` points; non-door walls explicitly transparent to both light and vision are omitted |
| `portals.bounds` | Absolute named endpoints; never rotated a second time |
| `portals.position` | Unsigned endpoint deltas, following the native Arkenforge exporter |
| `portals.rotation` | Zero because bounds already supply orientation |
| `portals.closed` | Source door state; locked becomes closed with an approximation warning |
| `environment` | `baked_lighting: false`, optional directly stored ambient hex color |
| `lights` | Top-level array, normalized positions, outer range in squares, opaque eight-digit ARGB color |
| Light rendering defaults | Intensity `0.5`, shadows `true`, explicitly graded approximate; not equivalents of Foundry luminosity/numeric shadows |
| `image` | Compatible RGB/RGBA PNG; WEBP/palette/grayscale sources decoded with Pillow and converted without resizing |

Already compatible RGB/RGBA PNG bytes are preserved. Invalid images and images larger than 16000 pixels on an axis fail with a clear error. The observed compatibility failure was resolved by conversion to PNG; this does not mean all WEBP imports fail in Arkenforge.

For geometry, stored `dimensions.sceneX/sceneY` are used if present. Otherwise each padding offset is derived from scene dimensions and rounded up to grid spaces. Missing padding assumes zero and is reported. Background translation offsets are included; rotation and scale transforms are currently rejected rather than producing misleading alignment. The real test required an 800/1000 pixel translation, matching a 3000 by 4000 scene at 100 pixels/grid with 0.25 padding, and the source report now confirms padding 0.25. No manor-specific constant is embedded in the writer.

## Door blocking limitation

UVTT's single `closed` boolean does not independently express Arkenforge's light/vision blocking capabilities and the current toggle state. Preserve the source state and record each portal index, wall id, and original `light`, `sight`, `move`, `sound`, `dir`, `threshold`, and `ds` settings in the report and companion. After import, set the appropriate properties in **Customise -> Blocking**. Do not enable light blocking indiscriminately on transparent windows. No unverified custom UVTT tags or automatic source-state changes are introduced.

This importer behavior needs a native map representation or a verified extension to become automatic. The current writer corrects compatibility but does not claim full blocking-semantic fidelity.

## Ordinary wall blocking

The fireplace test confirmed that importing every source wall as opaque traps lights behind Foundry movement-only barriers. Non-door walls with explicit `light=0` and `sight=0` now stay out of UVTT `line_of_sight`. Their source records remain intact in the companion; `wall-transparent-omitted` reports identify their normalized endpoints and movement/sound settings for recreation if needed. This avoids inventing optical blocking at the cost of requiring separate movement/sound setup. Missing restriction fields are not assumed to be zero.

Mixed light/vision modes remain as geometry because UVTT has no independently verified per-segment blocking flags. `wall-blocking-properties` reports give the emitted segment index, normalized endpoints, source wall id and restrictions, and explicit instructions to disable Blocks Light or Blocks Vision when the source value is zero. Limited/proximity/directional/threshold modes require inspection rather than an invented Boolean equivalent. Both-light-and-vision-normal walls retain ordinary LOS geometry. Doors are handled first, so transparent doors remain portals and retain their source open/closed state.

The user confirmed that disabling light blocking on the fireplace-front barrier lets the lights illuminate the room. No light relocation, radius cap, blanket shadow disabling, or invented custom UVTT properties are used as a workaround.

## Lighting limitations

Outer dim/bright radii divide by `grid.distance`; separate bright/dim zones remain approximate. Negative-radius darkness sources have no translated range. Unset/blank tint is a valid Foundry light and becomes neutral white in UVTT with an approximation warning. Invalid non-empty colors and invalid positions remain rejected. The complete source configuration remains in the companion for later work. Painted illumination in the background image cannot be removed by changing imported dynamic lights.

## Reports and validation

Both UVTT and loss report are checked against bundled schemas. Counts currently include package inventory in addition to the selected scene. `unsupported` means not translated by this slice, not proof that Arkenforge lacks the capability. The UVTT schema rejects legacy point arrays and nested lights. Regression cases cover padding, independent scene origins, reversed door endpoints, image decoding/conversion, unsupported background transforms, preserved skipped-light data, and companion output. Existing text, LevelDB, Adventure, ZIP, asset containment, and non-execution checks remain.

References: [Arkenforge UVTT](https://arkenforge.com/universal-vtt-files/), [Foundry Scene dimensions](https://foundryvtt.com/api/v12/classes/client.Scene.html#getDimensions), [Arkenforge blocking controls](https://arkenforge.com/arkenforge-v0-4-2-0-update/), [Arkenforge 0.5 light controls](https://arkenforge.com/v0-5release/). The private native samples and real map are not checked into this repository.

## Full source report follow-up

The Count's Manor report contains 24 AmbientLights: eight tinted and sixteen with `config.color: null`. Foundry's [lighting documentation](https://foundryvtt.com/article/lighting/) says new lights start with a blank color and clearing that field removes tint. UVTT neutral white is an approximation of untinted illumination; it does not recover torch/ghost animation. All sixteen have valid positions and positive ranges. Fifteen have outer range one square; one ghost light has outer range forty squares. Do not cap the large radius or drop the light merely because its tint is unset.

The twelve portals comprise ten light/vision-blocking door segments (`light=20`, `sight=20`) and two transparent entrance segments (`light=0`, `sight=0`, `move=20`). Nine are initially open and three closed. The entrance test correctly passed light in both states; the earlier interpretation of that as a missing blocking setting was mistaken. Portal warnings now distinguish source blocking settings, and transparent portals are not made opaque.

## Map note and journal correlation

Each export now includes `scene_notes` in stdout and the `.forgebridge.json` companion, plus a `.notes.txt` GM reference. These are preservation/reference outputs, not native Arkenforge note files. No new fields are added to the importable UVTT.

For embedded Adventure scenes, journal lookup first uses the selected parent Adventure's `journal` collection. Standalone JournalEntry packs are fallback sources; matches in the scene's own pack take priority over other packs. The other Adventure variants are never searched implicitly. Bare entry IDs and `JournalEntry.ID` references are supported; other UUID namespaces remain explicit unresolved references rather than guessed suffix matches.

Each note records its full source settings, normalized map position in grid squares, status, and indexes into deduplicated linked journals/pages. Linked journal objects, all their pages, raw rich text, media references, permissions, flags, and unknown fields are retained without inventory truncation. A requested page must match exactly once; missing/duplicate entries or pages stay unresolved. Whole-entry notes and legacy journal content are supported. The readable reference strips HTML tags and script/style content without rendering, fetching media, or executing anything. Markdown page text stays text; rich formatting and original links remain in JSON. Permissions are retained but not enforced by this GM-only reference; do not distribute it as player material without review.

Re-export a scene using the existing CLI command, then open its `.notes.txt` and inspect `scene_notes.counts` and `read_errors` in the companion. JSON, NeDB, LevelDB, parent Adventure scoping, zipped CLI output, missing/ambiguous references, legacy text, path containment, and inert HTML are covered by regression tests. The subsequent real export resolved all 19 Crypt notes with no read errors, retaining the complete 21-page 3. Crypt journal from adventure-5e.

The first-floor fresh export now passes fireplace illumination and light movement. Count's Crypt (4000 by 4200 pixels, padding 0.25) passes wall/door alignment, movable interior illumination, and door occlusion in the user's manual test. Its report records 66 exported lights, 23 portals, 199 LOS segments, and seven omitted optically transparent barriers.

## Linked-content dependencies

`scene_notes.dependencies` now retains a bounded graph of referenced JournalEntry and RollTable source objects. Recognized `@UUID[...]` links resolve exact journal/page IDs or table IDs. Relative `.PAGE_ID` links are resolved against their containing journal, following the form observed in the real Crypt. Explicit compendium pack namespaces must match a package-local standalone pack; unresolved external namespaces never fall back to a document with the same ID. References to unsupported types or syntax remain explicit rather than being executed.

Recursive lookup stays within the current source Adventure or standalone pack first, then unambiguous standalone sources. It never silently crosses to another Adventure variant. Complete raw objects are retained once per scoped identity, while reference records track origin paths, labels, exact target/page indexes, anchors, and missing/ambiguous/unsupported statuses. Cycles terminate through visited document/page contexts. Limits of 256 documents and 4096 references set `truncated` and are reported instead of pretending the graph is complete.

RollTable source formulas, results, ranges, weights, replacement/drawn state, permissions, flags, and unknown fields remain in JSON. Legacy `documentCollection`/`documentId` result links are followed as document or explicit compendium references. No formula is evaluated and no table draw or macro is executed. The readable `.notes.txt` includes a link-status list, additional referenced journal pages (including unplaced pages), and table outcomes with original ranges/weights. It does not recreate Arkenforge native tables or notes.

Verification includes JSON/NeDB/LevelDB Adventure journal-to-table chains, cycles, exact pages, relative links, same-ID variant isolation, compendium namespaces, legacy table-result pointers, missing/ambiguous targets, bounded traversal, and inert formulas. The uploaded Crypt journal's 11 relative links all resolve. References to other journals/tables require a fresh original-package export; the previous companion only contained the directly linked Crypt journal.

Sources: [Foundry UUID parser and relative context](https://foundryvtt.com/api/functions/foundry.utils.parseUuid.html), [Foundry TableResult data](https://foundryvtt.com/api/v12/interfaces/foundry.types.TableResultData.html). Source links and scripts are preserved as data; no Foundry runtime is invoked.

## Fog and vision (2026-10-31)

Foundry `tokenVision`, `fog.exploration` (v10: `fogExploration`) and
`environment.globalLight.enabled` (v10: `globalLight`) now produce one `manual`
`fog-vision` line instead of generic unknown-scene-field lines. ForgeBridge does
not write Toolkit fog state, explored-fog history or per-token vision. Arkenforge
manual fog starts fully covered, so a converted map's player screen shows only fog
until areas are revealed or fog is disabled (observed 2026-10-31 on both profile
maps). With `tokenVision=false` the line tells the GM to disable or clear Toolkit
fog to match Foundry. All 17 Count's Manor scenes store `tokenVision=true`.
