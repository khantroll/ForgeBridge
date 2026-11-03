# Fantasy Grounds phase 2 — file-level evidence, 2026-11-02

Branch fantasy-grounds-adapter; main v0.10.0 (523cfcd) merged cleanly at 4de6c87.
No Toolkit or Fantasy Grounds launch, real MyAssets access, installation, system
changes, or runtime acceptance in this work. Native geometry math is unchanged;
target schema reference remains Toolkit 0.5.1.18, not a newly tested version.

| Check | Status | Evidence |
|---|---|---|
| Native module conversion, naming and dependency closure | PASS (synthetic/file) | tests/test_fg_convert.py; schema-built geometry/background helper shared with Foundry |
| NEEDS_GRID refusal, keyed/bare grid input, stored grid precedence | PASS (synthetic/file) | 2048px / 40 squares → 51.2px input → 2040px image at 51px; 3 native barriers |
| ART filter, folder/.mod/vault discovery and encrypted CLI/GUI refusal | PASS (synthetic/headless) | No desktop control or actual GUI window; protected content never opened |
| Existing installer/receipt/uninstall integration | PASS (fake MyAssets only) | 4 native files added and removed; original user file preserved |
| Foundry regressions and full suite | PASS | 264 run, 260 passed, 4 Windows symlink-privilege skips; 196.382s |
| (a) MFE 91 real module native build | BLOCKED | C:\AMD\MFE_91_Files.zip is absent; no replacement asset or real-module result invented |
| (b) Independent Arkenforge FGU export → FG module → native package | PASS (file only) | Exact 199 barriers, 23 door records, 66 lights; see below and results JSON |
| New native output rendering and geometry in the Toolkit | PASS (Claude, 2026-11-02) | Installed by Codex with the add-only installer; opened in Toolkit 0.5.1.18 — see below |
| Player view/fog for FG-sourced maps | NOT RE-CHECKED | Same shared native writer as the Foundry maps already checked over the player stream |

## Implementation boundaries

convert/discover detect .mod, definition.xml folders and unencrypted vault ZIPs;
existing Foundry manifests win over incidental FG assets. FG to_uvtt produces
the existing UVTT intermediate; the shared schema-native helper synthesizes
geometry, background and map thumbnail at 2.56 units/grid, origin (0,0).
Foundry note/token stages are not run for FG. Naming/conflict rules, native
dependency closure, add-only installer and receipts are reused unchanged.
FG source polylines may become several native straight barrier records; both
counts are reported. FG windows become open native door portals.

GUI checks are headless: module/file selection, ART checkbox, status and known
pixels-per-square labels, per-map grid prompts, named output and FG loss summary.
Story, pins, tokens, unsupported occluders, ambient/vision and light-fidelity
limits remain explicit. Labels remain off. No imported scripts are executed.

The encrypted-error integration test reproduced a ZIP handle left open when
ModuleSource initialization failed. The constructor now closes on errors.
Additional synthetic guards reject a stored grid rounding to zero or resampling
beyond the existing 64 MP bound, and keep sidecar geometry without a grid visible
as NEEDS_GRID. These do not change coordinate/geometry formulas.

## Real check (b)

Original read-only input pair:
C:\AMD\Fb-fg-export\ForgeBridge Direct Crypt 2026-11-01.png and .xml.
Minimal wrapper created only in the new directory
C:\AMD\fb-fg-phase2-export-module-2026-11-02: definition.xml, one db.xml image
record with grid on, and images/Crypt FGU Export.png plus matching XML sidecar.
Copied image/sidecar hashes match the originals.

```powershell
$env:PYTHONPATH='src'
python -m forgebridge convert C:\AMD\fb-fg-phase2-export-module-2026-11-02 --out C:\AMD\fb-fg-phase2-export-native-2026-11-02
```

Exit **0**, PASS. Module/map defaults:

- Map: MyAssets/Maps/ForgeBridge FG Export Check/Crypt FGU Export.rwmap
- Name: Crypt FGU Export; visible notes folder: ForgeBridge FG Export Check
  (reserved only; no FG notes are fabricated).
- FG: 199 wall polylines, 20 doors, 3 windows, 66 lights, 0 off lights, 0 terrain.
- Native: 199 barriers, 23 doors (20 doors + 3 windows), 66 lights, 1 background.
- Metadata: images/Crypt FGU Export.xml; 100 px/square; 5000×4800 unchanged.
- Exactly 4 native files; 1 closed metadata reference (map → background metadata).
- Losses: 0,50px grid offset; windows as open portals; door centre lines;
  bright/dim falloff reduced to one radius; native import light defaults;
  tokens/story/ambient/vision manual. No pins in this source record.

Hashes and full graded losses: 2026-11-02-fg-native-phase2-results.json.
Ready package for Claude's separate reviewed install/Toolkit check:
C:\AMD\fb-fg-phase2-export-native-2026-11-02\scene-001\native-package.zip.
No real installation was performed. Prior reader/UVTT and prior Foundry runtime
evidence remain separate from this new native-package result.

## Toolkit check (Claude, 2026-11-02)

Package installed into the real MyAssets by Codex
(`MyAssets/Maps/ForgeBridge FG Export Check/Crypt FGU Export.rwmap` + background).
Toolkit 0.5.1.18 started from the launcher; opened from the Map Browser
(folder *ForgeBridge FG Export Check*, creator ForgeBridge, user content).

- Loads without error; 5000×4800 background at the expected size on the grid.
- Wall barriers sit on the drawn stone edges throughout (checked zoomed).
- 23 door markers visible, matching 20 FG doors + 3 windows, each in a
  doorway.
- Light glows along corridors and in rooms, matching the source export.
- Not re-checked here: player-stream fog/vision for this map (same writer as
  the Foundry maps already checked). Map not saved; nothing edited.
