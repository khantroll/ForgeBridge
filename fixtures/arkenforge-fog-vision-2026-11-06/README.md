# Fog, vision and light animation capture — 2026-11-06 (Claude, Toolkit 0.5.1.18)

Raw files stay on Xenos (adventure geometry is not committed):
`MyAssets/Maps/FB Capture Base.rwmap|.rwmeta` (Count's Lair, saved unchanged with
Save as new) and `MyAssets/Maps/FB Capture Effects.rwmap|.rwmeta` (same map, then the
edits below, then Save map). `base-vs-effects.decoded.diff` is the decoded NRBF diff
(ForgeBridge `nrbf.inspect_nrbf`). Read the raw files from MyAssets for byte-level schema.

## Edits made in the Toolkit and what they wrote

| UI action | Saved fields |
|---|---|
| Light A: **Torch preset** (Customize → Lighting → presets) | `TileLightingProperties._lightRadius[0]` 4.096 → 11.52 (UI radius 1.42 → 4.00); `_flicker = True`; adds `_effectsNew[0] = ObjectEffectLightFlicker { _intensity 1.0, _name 'Light Flicker', _enabled True }` |
| Light A: **Light reveals fog of war** | `_visibleThroughFog = True` |
| Light A: Customize → Effects **Enable/Disable all effects** ticked | (effects list enabled; see effect `_enabled`) |
| Light B: **Emits darkness** | `_darkness = True` (darkness light) |
| Light B: Effects → **Add new effect → Light - Blink** | `_effectsNew[0] = ObjectEffectLightBlink { _timeBetweenBlinks 0.075, _maxBlinkCount 5, _waitTime 4.0, _waitTimeVariance 0.25, _name 'Light Blink', _enabled True }` |
| Live Play → Tokens, place as **Player**, drag "Chris" onto map | New `ArkenTilePresetContentLink` tile (`_tileType 8`, `_contentType 'note'`), auto-created note `MyAssets/Encyclopedia/Notes/Map Notes/FB Capture Effects/Chris.rwmeta`, `_placementType 14` |
| Token: Customize → Lighting **Light enabled** + **reveals fog** + radius | token `_lighting { _hasLight True, _lightRadius[0] 13.248, _visibleThroughFog True, _fov 360, _lightIntensity 1.0 }` — **this is Arkenforge's token vision**: a token light that reveals fog |
| Fog of war: **Manual → Dynamic** | map `_fogMode` 1 → **2** (`FogOfWarOptions+FogMode`; 1 = Manual, 2 = Dynamic); `_fogEnabled True`; `_fogPersists True` (*Hide already seen areas*, already on); `_fogColour` None → (0,0,0) |
| Fog: **Simulate darkness** ticked | **Not saved in the map or rwmeta** (Toolkit-wide setting) |

Other UI facts:
- Light presets: candle, campfire, lantern, torch, lamp/spot, bulb. Advanced: update type (Dynamic), light quality (Global).
- Object effects menu: Float, Pulse, Rotate (regular/pivot), Shake, **Light - Flicker**, **Light - Blink**; universal: Blink, Sound Trigger, Double Click.
- Dynamic fog options: *Hide already seen areas*, *Simulate darkness* ("everything black unless a character has darkvision, nightvision, or a light source is in view"). No per-token darkvision field was found in token Customize panels (Colour, Ambience, Content Link, Lighting, Blocking, Drop Shadow, Transforms, Grid Scaler, Effects).
- Map-level ambience fields present: `_useCustomAmbienceColour`, `_customAmbientColour`, `_useCustomLightIntensity`, `_customLightIntensity` (0.5) — candidates for Foundry scene darkness/global illumination (not exercised here).
- Walls already carry `TileBlockingProperties._vision` (true on converted walls).

## Suggested Foundry → native mapping (to implement, then verify)

- Scene `tokenVision` / fog exploration → `_fogEnabled True`, `_fogMode 2` (Dynamic), `_fogPersists = fog.exploration`.
- Token `sight.enabled` + `sight.range` (and darkvision) on player-owned tokens → token light `_hasLight True`, `_visibleThroughFog True`, radius = range in squares × the same light-radius scale as converted lights, `_lightIntensity` low for darkvision-only (approximation; report it).
- Light animation `torch`/`flame`/`flicker`/`fairy`… → `ObjectEffectLightFlicker` (+ `_flicker True`), intensity from animation intensity/10; `pulse`/`chroma`… → `ObjectEffectLightBlink` or Pulse where reasonable; others → loss.
- Foundry negative/darkness lights → `_darkness True`.
- Scene darkness level → `_useCustomLightIntensity`/`_customLightIntensity` (verify direction in Toolkit).
- Fantasy Grounds: FG LOS/vision flags → the same fog/token-light mapping; FG light animation where present.
