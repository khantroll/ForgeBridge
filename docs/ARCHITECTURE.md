# Architecture Notes

## Boundary model

ForgeBridge should separate five concerns:

1. **Source adapters** — read Foundry module/world/export structures without executing imported code.
2. **Inventory/provenance** — track every source document, asset, relationship, ID, and warning.
3. **ForgeBridge IR** — platform-neutral representation of content and behavior.
4. **Target adapters** — emit the best available Arkenforge representation.
5. **Compatibility/reporting** — explain fidelity, approximations, manual work, and unsupported features.

## Suggested IR domains

- `assets`: image, animation, audio, font/reference metadata
- `maps`: dimensions, grid, background, layers
- `geometry`: walls, doors, windows, barriers, regions
- `presentation`: lights, darkness, visibility, effects
- `entities`: tokens, actors, NPCs, items, spells
- `knowledge`: journals, pages, notes, links
- `audio`: ambient emitters, playlists, soundscapes
- `tables`: roll tables and random content
- `behaviors`: triggers, conditions, actions
- `provenance`: source IDs, package/system/module/version
- `diagnostics`: confidence, lossiness, unsupported fields

## Behavior IR

Behavior conversion is the feature that differentiates ForgeBridge from a file converter.

A behavior should describe:
- trigger;
- optional conditions;
- ordered/parallel actions;
- referenced entities/assets;
- state changes;
- source provenance;
- confidence;
- target capability requirements.

The behavior engine should never require arbitrary source-code execution.

## LLM safety boundary

If AI analysis is enabled, feed it:
- extracted macro text or relevant fragments;
- statically resolved references;
- a strict ForgeBridge behavior schema;
- a finite catalog of target capabilities.

Do not give the model authority to directly manipulate the target campaign. Its output becomes a *proposal* that must pass schema validation and deterministic compilation.

## Adapter strategy

Core IR must not know that a particular Foundry module exists. Module/system peculiarities belong in adapters:

```text
Foundry Core Adapter
  +-- dnd5e adapter
  +-- pf2e adapter
  +-- module-X adapter
  +-- module-Y adapter
```

Unknown flags/data should be retained as source metadata where practical so future adapters can recover information without requiring a fresh import.

## Fidelity

Use explicit conversion grades rather than a single success/failure bit:

- native
- approximate
- manual-trigger
- gm-assisted
- unsupported

Each output object should be traceable to its source object(s), and each lossy conversion should generate a diagnostic.

## Security

Foundry script macros and third-party module code are untrusted input. Parse; do not execute. Treat paths, archives, HTML, URLs, and generated filenames as hostile input. Enforce extraction boundaries and sanitize generated target content.

## Future question

The major research question is not whether Foundry data can be parsed. It is how much of Arkenforge can be created or controlled programmatically in the version current when development starts. The answer determines whether behavior compilation targets native content files, documented interfaces, user-facing hotkeys/actions, an integration/MCP layer, or some combination.
