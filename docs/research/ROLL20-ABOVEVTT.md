# Roll20 and AboveVTT → Arkenforge: inbound-adapter research
Date: 2026-11-02. Research only; **not** a promise of compatibility.

## Scope
ForgeBridge's goal is to bring foreign maps, scenes and structured adventure material **into Arkenforge**. Foundry is the active source; Fantasy Grounds is under separate investigation. This file evaluates *additional inbound sources*, not reverse exports. Keep work independent of the unmerged native scene branch and completion PR.

## Roll20 — feasible parsing, uncertain legal/export route
- Official **Transmogrifier** moves items between Roll20 games, not a portable general campaign export. It also supports map pins, with handout links that need migration-order care: https://help.roll20.net/hc/en-us/articles/36271267343639-Map-Pins
- Open-source https://github.com/kakaroto/R20Exporter exports a campaign/assets ZIP using a browser extension; its authors warn of potential Roll20 EULA/marketplace license violations and account consequences. **Do not embed, automate, require or recommend third-party extraction as default**.
- https://github.com/kakaroto/R20Converter consumes R20Exporter ZIP/JSON and generates Foundry worlds/modules. This establishes prior art for an offline parser. Converter warns that macros are not behaviorally converted and character sheet conversion is limited (5e OGL/Shaped).
- Alternative https://github.com/ooshhub/r20Exporter notes image CORS failures, access-dependent GM notes and blobs, and image/audio assets potentially split into ZIPs.
- Roll20 official mod scripts exist but are subscription/creator-feature dependent; not an official bulk export API: https://help.roll20.net/hc/en-us/articles/360037256714-Introduction-to-Mod-Scripts
- Terms: https://help.roll20.net/hc/en-us/articles/360037770793-Terms-of-Service-and-Privacy-Policy . Review licensing and avoid redistribution or bypassing access controls. User-authorized local files only.
**Assessment:** High potential payoff, **conditional feasibility** until rights-cleared sample export and source formats validated.

## AboveVTT — concrete export path; priority for prototype investigation
- Open source: https://github.com/cyruzzo/AboveVTT
- Scene exports are real and actively maintained; release 1.61-beta16 (2026-10-22) fixes export of newly added tokens/drawings; 1.61-beta18 (2026-10-25) fixes scenes/folders omitted in large campaigns lacking parentId: https://github.com/cyruzzo/AboveVTT/releases
- UVTT import is supported (historical issue): https://github.com/cyruzzo/AboveVTT/issues/754 . **UVTT input support is not equivalent to native scene export schema**; inspect actual export code and fixtures before specifying field names.
- Source data references D&D Beyond content; no assumption of downloadable licensed map images, token art or monster/stat data. Require local content rights, preserve unresolved references in loss report.
**Assessment:** Potentially cheaper first parser than Roll20, provided native exported scene JSON/archives are verified with fixtures.

## Comparative feasibility questions
| Criterion | Roll20 | AboveVTT |
| --- | --- | --- |
| Demonstrated portable export | Third-party exporter ZIP/JSON | Native scene exports reported in release history |
| Documented official complete export | Not established | Exact schema still unverified |
| Main implementation risk | Legitimate data acquisition, version drift, asset rights | Scene schema/versioning, remote assets, DDB references |
| Reuse of ForgeBridge | Geometry/token/notes IR and Arkenforge native packager | Same; possibly direct export records |
| First phase | Offline inventory of a rights-cleared export | Inspect export code and parse sample exported scene |
| Ready to code production adapter? | No | No |

## Proposed read-only feasibility spikes
1. **AboveVTT first**: find export entry points and version metadata; obtain small scene export (simple map, wall/door, light, token, note); build a table of observed source fields and media references, with evidence. Do not guess schema.
2. **Roll20 next**: identify a legally obtained sample ZIP/JSON (prefer self-created/test campaigns), inspect and inventory offline without running embedded scripts or fetching protected assets. Compare export variants and explicitly label unknowns.
3. Map both **observed** structures to ForgeBridge IR and existing native package builder; grade native/approximate/manual/unsupported. Avoid routing rich token/notes material through UVTT, which cannot represent it.
4. Make a read-only adapter proof of concept: source validation, normalized scene + loss report, no installer; then geometry-first integration against disposable Arkenforge fixture.
5. Decide build/no-build after reproducible representative examples, acceptable legal route, and stable identity/path resolution. Keep this separate from M0–M2 completion.

## Required tests and guardrails
- Decode JSON/ZIP offline with bounded archive sizes; reject traversal, symlinks, colliding paths and embedded executable content.
- No cookies, password capture, session extraction, live account automation or marketplace asset redistribution.
- Explicit source provenance, scene and object identities, grid/origin conversion, hidden flags, door semantics, note links, media dependencies.
- Asset missing/remote/link-only cases must remain visible in loss report.
- Document versioned schema, license assumptions, sample provenance, fixture hashes, deterministic outputs and non-destructive acceptance.
