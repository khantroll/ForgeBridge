# Arkenforge import, export, and automation notes

Retrieved 2026-10-03 from Arkenforge's public site and one vendor forum reply. No Arkenforge build was installed, and no Arkenforge content pack was downloaded. The sample UVTT map linked from their UVTT article was not fetched: it is their content, and this repository does not vendor it.

Capabilities below are only those the cited page actually states. "Not found" means this review did not find a public document, not that a private feature cannot exist.

## Sources

| Source | What was used | Date |
|---|---|---|
| [Universal VTT files](https://arkenforge.com/universal-vtt-files/) | UVTT import and export, field list, stated limits | `datePublished` 2022-03-05, `dateModified` 2026-08-22. Retrieved 2026-10-03. |
| [Toolkit v0.5.0.0 public release](https://arkenforge.com/v0-5release/) | Current public feature set used for this spike: import widget, export widget, Foundry module export, notes, tokens, rollable tables, hotkeys, pack export | `datePublished` 2026-01-13. Retrieved 2026-10-03. |
| [Toolkit v0.5.1 public update](https://arkenforge.com/the-arkenforge-toolkit-v0-5-1-public-update-has-released/) | Latest public release found: touch, fog, tokens, playlists. States the next series. | `datePublished` 2026-05-14, `dateModified` 2026-05-14. Retrieved 2026-10-03. |
| [Animated map builder FAQ](https://arkenforge.com/animated-maps/) | Import extensions, including audio | `dateModified` 2025-12-10. Retrieved 2026-10-03. |
| [Map builder](https://arkenforge.com/map-builder/) | Older import list and VTT export claim | `dateModified` 2024-02-16. Retrieved 2026-10-03. |
| [Campaign management / Encyclopedia](https://arkenforge.com/campaign-management/) | Older description of notes, tokens, playlists | `datePublished` 2022-02-17, `dateModified` 2022-03-03. Retrieved 2026-10-03. |
| [v0.4.2.0 update](https://arkenforge.com/arkenforge-v0-4-2-0-update/) | Earlier UVTT portal behavior (doors and windows) | Page text retrieved via search on 2026-10-03. A publication date was not on the extracted text. Treat the 2026 UVTT page plus the v0.5.0.0 notes as the newer statements. |
| Vendor reply on [Unable to Import Map/Image](https://www.reddit.com/r/Arkenforge/comments/1aon9bu/unable_to_import_mapimage/) | `.rwmap` as "Import map" for the public version at that time | Arkenforge account, 2024-02-12, as quoted in search results. |

No developer handbook, REST API, plugin SDK, or content-file schema was found in these pages or in a search for an Arkenforge API, CLI, or scripting surface on 2026-10-03.

## Import

The animated-map FAQ (`dateModified` 2025-12-10) lists:

- Images, maximum 16k pixels: JPG, PNG, WEBP
- Animation and video: GIF, MP4, M4V, WEBM
- Audio: MP3, OGG, WAV

The map-builder page (`dateModified` 2024-02-16) lists JPG, PNG, MP4, M4V, WEBM, GIF, and image sequences. It does not list WEBP or audio. The v0.5.0.0 notes (2026-01-13) say "Can now import WebP files". The 2024 page is older than both the FAQ and the v0.5.0.0 notes. This spike treats the FAQ plus the v0.5.0.0 notes as the current extension list, and the map-builder page as stale on WEBP and audio.

The v0.5.0.0 import widget lists: open import panel, import image/video, import PNG sequence, import token, import UVTT.

Dungeondraft asset packs can be imported as mapping assets only when the pack sets `allow_3rd_party_mapping_software_to_read`. The notes do not publish the rest of that pack format. This repository does not include a Dungeondraft pack.

UVTT import is native: Import Content, then UVTT, on the UVTT page (`dateModified` 2026-08-22). The same page says `.uvtt`, `.dd2vtt`, and `.df2vtt` are the same JSON file. It also says a UVTT map is one flat image, so it cannot carry animation or individually selectable tokens.

The documented core fields, in the page's own wording, are:

- `format` (a decimal version)
- `resolution.map_origin` `{x, y}`
- `resolution.map_size` `{x, y}` in squares
- `resolution.pixels_per_grid`
- `line_of_sight` and `objects_line_of_sight` (arrays of points)
- `portals` with `position`, `bounds`, `rotation` in radians, `closed`, `freestanding`
- `environment.baked_lighting`, `environment.ambient_light`, and `environment.lights` (`position`, `range`, `intensity`, `color`, `shadows`)
- `image`: base64 PNG or WEBP

The page says Arkenforge also writes its own `software` and `creator` tags and that extra tags are possible. It does not define a closed schema. Positions are in squares.

The v0.4.2.0 notes said UVTT portals import as toggleable barriers that block light and vision, and that windows import as toggleable barriers that block neither. The v0.5.0.0 notes say UVTT import offsets lights and barriers by map origin, and that a UVTT file with no image prompts instead of failing. Those notes are behavior reports, not a second field list. Where they disagree with the 2026 UVTT page, the UVTT page is the one that lists fields; the patch notes only describe import behavior.

A 2024-02-12 vendor reply said the then-current public "Import map" accepted `.rwmap` files, while images used "Import map asset". The 2026 release notes still list "Import map" separately from image import and from UVTT, but they do not name `.rwmap` and they do not publish its contents. `.rwmap` is not a confirmed current format specification.

## Export

From the v0.5.0.0 notes (2026-01-13), the export widget can write an image, a video, a PDF, or a UVTT file. Image export can be WebP. Video export can be WEBM. Map-export toggles named in those notes are grid, lights, hidden objects, tokens, "only export this level", and upper-level shadows.

Foundry-specific export in those notes:

- WebP for the Foundry VTT export type
- WEBM for the Foundry VTT export type
- "Foundry v11+ Module export (Windows only)"

That module export is Arkenforge writing a Foundry module. The note does not describe the module layout. It is not an API ForgeBridge can call, and it is the opposite direction from this project. The same notes also name Fantasy Grounds Unity, D&D Beyond, and Owlbear Rodeo exports. Those are out of scope here except as evidence that export is a UI action with several targets.

Other file outputs named in the same notes, without a schema:

- Pack export writes a "MyAssets-style folder" that can be copied into MyAssets on another machine. Linked content is included. The folder layout is not specified.
- A hotkey profile can be exported "as a text document". The text format is not specified.
- "Generate asset list" writes a CSV of assets on the current map.

The UVTT page says the Toolkit exports Universal VTT with a `.uvtt` extension. It also claims the Toolkit is the only platform that both imports and exports UVTT. The same page says Roll20 and Fantasy Grounds Unity accept UVTT files. The "only platform" sentence is Arkenforge's claim; this spike did not survey other tools.

The animated-map FAQ answers "can I use the maps in other VTTs?" with MP4 and WebM only. That answer is narrower than the v0.5.0.0 export widget, which also lists image, PDF, UVTT, and Foundry module export. The FAQ is the older, shorter statement (`dateModified` 2025-12-10, before the 2026-01-13 public release). The release notes are the better source for the export menu.

## Campaign features that exist in the product UI

These are confirmed as product features. None of them came with a file format.

v0.5.0.0 (2026-01-13):

- Notes can hold 5e 2014 and 5e 2024 stat, item, and spell blocks, a controllable field, a listener field, a rollable-table field, vision, a token identifier, media, and `@` content links. Several note templates exist (adventure, 5e character, item, spell).
- Rollable tables exist and can weight outcomes by a roll range.
- Tokens can be dragged onto a map. The notes say that creates a note with an icon and a size field. Placing a token as PC or NPC changes the default fields.
- Playlists and positional ambience exist. Tokens can have listeners.
- Hotkeys can be assigned to functions and to content. One hotkey can be dragged to the map or the Arkenbar.
- Dice in that release are a d20 system, with multiples and a modifier, with or without a 3D animation. The notes say more dice systems are future work.

v0.5.1 (2026-05-14) adds grouped token movement, box and polygon fog, and playlist UI fixes. It says the next series, v0.5.2, is hoped to include different token health-ring styles, tabbed windows, multi-image media fields, and condition markers. Those four items are not in the public build described by that post.

The encyclopedia marketing page (last modified 2022-03-03) still describes notes, custom fields, tokens, soundscapes, playlists, map links, and animated tokens. It does not mention rollable tables or the 5e blocks. It is older than the v0.5.0.0 notes, not a conflicting spec. It also says drag-and-drop from the operating system is Windows only. The v0.5 notes do not repeat that limit.

## Programmatic and automation surface

Confirmed, and thin:

- Hotkeys are a user-facing trigger. A profile can be exported as an unspecified text document.
- `SHOW|` prefixed to "a URI string that points to a map asset file" shows that content to players (v0.5.0.0). No grammar is published.
- Local player-screen streaming starts "a local webserver application" and is viewed at the computer's local IP in a browser (v0.5.0.0). No paths, messages, or authentication are documented.
- v0.5.1 can connect a touch client by IP address and can stream the player screen to it. That is a display connection.

Not found in the public pages reviewed on 2026-10-03:

- A documented HTTP or socket API for creating maps, notes, tokens, lights, barriers, or tables.
- A plugin or scripting SDK.
- A CLI.
- An on-disk schema for notes, tokens, playlists, rollable tables, hotkey files, or MyAssets.
- An MCP server or other agent surface.

The architecture note asked whether behavior compilation can target native files, a documented interface, hotkeys, or an integration layer. From public docs, the only structured native file Arkenforge both reads and writes is UVTT. Hotkeys exist, but only as a UI feature plus an unspecified text export. There is no documented control API.

## What that allows ForgeBridge to claim

| Foundry concept in the README | Arkenforge surface actually confirmed | Status |
|---|---|---|
| Scene background | UVTT `image`, or a loose image import (JPG, PNG, WEBP) | Confirmed as import, not as a campaign file we can author beyond UVTT JSON |
| Grid | UVTT `resolution` | Confirmed as UVTT fields. Square, hex, and isometric grids exist in the product (FAQ and v0.5.0.0 grid widget). UVTT's page defines squares only. |
| Walls, doors, windows | UVTT `line_of_sight` and `portals`. v0.4.2 notes map portals to toggleable barriers and windows to non-blocking toggleable barriers. | Field list confirmed. Door/window encoding is only described in older patch notes. |
| Lights | UVTT `environment.lights` and `ambient_light` | Confirmed |
| Tiles and individual tokens | UVTT page says the format cannot carry individually selectable tokens. Tokens exist in the Toolkit UI. | UI confirmed. No file format. |
| Ambient audio and playlists | Audio file import (MP3, OGG, WAV). Playlists exist in the UI. | File import confirmed. Playlist document format not found. |
| Journals and actors | Notes, including stat blocks and token attachment, exist in the UI. | No file format. |
| Items and spells | 5e item and spell blocks are note fields in v0.5.0.0. | No file format. Not a general item system. |
| Roll tables | Rollable tables exist in v0.5.0.0, including weighted ranges. | No file format. |
| Macros and active effects | No equivalent API. Hotkeys can trigger content or functions. | UI only. Text export format not published. |
| Regions and triggers | Not described as a user-scriptable region system. Double-click content links and hotkeys are the closest documented triggers. | No region-document format. |

UVTT cannot be the ceiling of ForgeBridge, which the README already says. It is the only documented structured target this spike can point at.
