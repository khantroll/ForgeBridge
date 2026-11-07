# Fog, vision and light animation — 2026-11-06

File-level implementation; runtime validation NOT PERFORMED. The requested 5 PM Central installation target was missed; work continued after the stated 7 PM trial expiry. No Toolkit was launched and no existing campaign was edited.

## Captured schema evidence

Windows, Toolkit 0.5.1.18. Read-only FB Capture Base SHA-256 `a0d7726a70b21a48e42bb3b5dc564a896560ca828d42e0084b45b332e30b964c`; Effects `809c7bee195fbf52e0c32528093b743282343fece340d323d3b5da2685314aa9`. Both remained unchanged. Schema-built Flicker/Blink members and defaults equal decoded controls. An in-memory persistence edit changed one byte without changing opaque saved fog masks. Only payload-free field definitions are committed.

## Mapping and limits

Foundry tokenVision enables Dynamic fog (mode 2); fog exploration sets persistence. This converts configuration, not historical reveal masks, per-user exploration or complete vision rules. Native darkness/global Simulate Darkness settings still require review. Source darkness level 0.5 remains manual: the capture did not demonstrate the direction of custom intensity.

An explicitly OWNER-owned character with sight enabled can carry a revealing light; NPCs never receive vision lights. User roles are unavailable, so ownership is approximate. Basic sight uses the converted-light scale; darkvision uses approximate intensity 0.15. Zero/unlimited ranges and unsupported vision modes are losses. Missing native token targets never create stray revealing lights.

Torch/flame/flicker uses captured typed Flicker and flag; pulse/blink uses captured Blink defaults. Unmapped animation remains static with a loss. Negative lights use darkness. Only explicit vision-granting lights reveal fog. Radius uses calibrated native units per grid, not source pixels or the capture UI's displayed radius.

FG explicit LOS or stored occluders and recognized animation are mapped. PC vision requires explicit square units and an existing generated native token target; missing placements are reported, never invented. This main-based branch does not integrate the separate pending FG token-placement work.

## Count's Lair targets

Map folder **FB Fog Check**, map **Count's Lair Fog**. Source has 17 lights: **11 torch flickers**, **6 ghost animations retained static with losses**. No blink or negative lights. All 11 tokens are NPCs with sight disabled: **zero token vision lights**, intentionally. Fog Dynamic, persistence enabled. A synthetic owned PC tests basic/darkvision mapping at file level only.

Runtime: BLOCKED / not observed. Bounded reveal/hide, actual player visibility, save/restart persistence and visual animation appearance require a licensed Toolkit check. Historical accepted runtime results are unchanged.

## File-level evidence

Package SHA-256 `2b16964352216e2369ce463e9522d223092e3c10368abf006400279ed9981b1e`. Complete source IDs and calibrated native positions are in the adjacent JSON. Example flicker: source M5Vqp8O3f2EsHU95, native UID 151 at (27.9808, -19.4304); source 9su7Mx1lBvNcLZ12, UID 152 at (6.4, -7.68).

| Check | Result | Evidence |
|---|---|---|
| Captured effect schema/default equality | PASS | Read-only raw control comparison |
| Preserve saved opaque mask bytes | PASS | One-byte in-memory persistence edit |
| Focused synthetic fog/vision/effects regression | PASS | 9 tests; no runtime claim |
| Real Count’s Lair file-only build | PASS | Exit 0; 243 closed metadata references |
| Generated native player vision/effects and restart | BLOCKED | No runtime observation; trial deadline missed |

Full Windows suite: PASS, 335 run, 331 passed, four skipped (Windows symlink tests). Final run exit 0 in 667.834 seconds; no skipped test counted as a passed safety check.

## Installation

Exit 0; **190 files added**, 156 identical dependencies left untouched. Receipt state COMPLETE; all 190 installed added-file SHA-256 values match the receipt. No conflicts refused, no previous checks uninstalled. Toolkit closed; not launched.

Receipt: `C:\AMD\fb-backups\forgebridge-d450b8d1618b4e42897dced0f2bdb97a\uninstall.json`

Backup: `C:\AMD\fb-backups\forgebridge-d450b8d1618b4e42897dced0f2bdb97a\MyAssets`

Open **Maps → FB Fog Check → Count's Lair Fog** for any later licensed runtime check. Eleven lights should flicker; six ghost lights stay static. No lights blink, no negative lights and no NPC vision lights. Dynamic fog with persistence enabled is configuration evidence only, not proof of player reveal/restart behavior.
