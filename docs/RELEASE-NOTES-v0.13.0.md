# ForgeBridge v0.13.0 — combined adventures, motion and reported limits

Release date: 2026-11-07. Builds on [v0.12.0](https://github.com/khantroll/ForgeBridge/blob/v0.13.0/docs/RELEASE-NOTES-v0.12.0.md).
Download **ForgeBridge-0.13.0-windows-x64.zip** from
[GitHub Releases](https://github.com/khantroll/ForgeBridge/releases/tag/v0.13.0).
The existing workflow publishes an experimental **pre-release**. Unzip the whole
folder outside Program Files/MyAssets. Run **ForgeBridge.exe**; keep
**forgebridge-cli.exe** and `_internal` beside it. No Python is required.

The Arkenforge trial has ended. **No v0.13.0 build was opened in Toolkit.** The
observations below belong to earlier check builds on Windows / Toolkit 0.5.1.18;
a successful file build, source hash or executable smoke test is not native runtime validation.

## Checked in Arkenforge Toolkit

- **Animated/video tiles:** the generated FB Motion Check WEBM timer and GIF
  animation played. Native video/motion controls had previously imported, placed
  and moved; this is not a claim that every codec/container was tested.
- **Map-attached ambient sounds:** Jeffrey heard the generated OGG/WAV controls
  at their placed map objects. Exact source wall occlusion/easing is approximate.
- **FG combined-adventure workflow:** real Well Met Blood Priest (legacy 3.5E
  display data) and a full story note were inspected. In the distinctly owned FG
  control, a map pin opened its story note and placed tokens showed portraits,
  size and rotation controls rather than cyan pins. **Well Met itself has no
  source pins or placed tokens**; the owned controls are not real-module evidence.
  Token-to-NPC automatic binding remains omitted to preserve portraits.
- **Display fixes from v0.12.0:** Protection from Poison reads “poisoned” without
  the Reference enricher; the scroll link is dark/readable; Boris has Proficiency
  Bonus +2 and no empty labelled rows; FG Goblin has no Unknown proficiency or
  empty labels; FG Light reads “Evocation cantrip”. This did not pass blank-gap collapse.
- Earlier checked MP3/OGG music and the three external dnd5e scroll-to-spell links
  remain accepted observations; they were not repeated for this release.

Evidence: [2026-11-06 Toolkit check](https://github.com/khantroll/ForgeBridge/blob/v0.13.0/validation/2026-11-06-TOOLKIT-CHECK.md),
[v0.12 display check](https://github.com/khantroll/ForgeBridge/blob/v0.13.0/validation/2026-11-05-V0120-TOOLKIT-CHECK.md), and
[earlier campaign/music/spell check](https://github.com/khantroll/ForgeBridge/blob/v0.13.0/validation/2026-11-05-FINAL-TOOLKIT-CHECK.md).

## File-level only (not yet seen in the Toolkit)

- **Fog/vision/light animation (#33):** schema-built Dynamic fog/persistence,
  bounded revealing sight lights for owned characters (never NPCs), approximate
  darkvision, Flicker/Blink effects and negative-light flags. Stored FG LOS/sight
  and supported light effects use the same native path after placements. Duplicate
  token identities cannot redirect PC sight onto an NPC. Historical explored
  masks, complete per-user vision and unsupported modes are not migrated.
- **Foundry Data folder art (#30):** optional read-only lookup for missing
  portraits/tiles inside an explicitly supplied Data root. Unsafe paths/links are
  refused; absent art stays an explicit loss. No images are invented.
- **FG text display fixes (#32):** carriage-return/newline escapes become real
  breaks; ordinary notes share explicit white text and paragraph spacing with
  Foundry journals. Native active flags and zero-size empty text request compact
  stat rows. **Visual gap removal remains unverified.**
- The merged FG path builds maps + NPC/item/spell/story notes, tables, manuals,
  parcels, quests, image handouts, pins and portrait tokens together. Real
  notes-only rebuilds retained all prior counts: Well Met 50 notes, SRD Bestiary
  351 and SRD Magic Items 1728 (including 29 tables). **2129 notes / 13925 decoded
  text strings** contained no literal newline escapes or raw CR. Source hashes
  were unchanged. Counts do not imply lossless conversion or runtime acceptance.
- All remaining source gaps and graded losses stay in conversion-report.json.
  Labels stay off. No imported scripts, roll expressions or active effects execute.

Evidence: [fog/vision/effects](https://github.com/khantroll/ForgeBridge/blob/v0.13.0/validation/2026-11-06-FOG-VISION-ANIMATION.md),
[FG rebuild/display audit](https://github.com/khantroll/ForgeBridge/blob/v0.13.0/validation/2026-11-06-FG-DISPLAY-FIXES.md), and
[Foundry Data implementation/tests](https://github.com/khantroll/ForgeBridge/blob/v0.13.0/tests/test_foundry_data.py).
The release updates version metadata, GUI/CLI fallback and Windows build metadata;
CI checks the built executables. See the [user guide](https://github.com/khantroll/ForgeBridge/blob/v0.13.0/docs/USER-GUIDE.md) for both inputs.

## Known limitations

- **Ghost and other light animations:** unmapped types remain static with losses;
  supported flicker/blink timing/intensity is approximate, not shader equivalence.
- **Scene darkness:** source darkness level is manual because native intensity
  direction was not calibrated. Negative-light mapping does not prove suppression equivalence.
- **Simulate darkness is a Toolkit-wide setting**, not stored in the exported map;
  ForgeBridge does not change that global setting.
- **Encrypted FG modules are refused**, including protected purchases/vault data.
  Unencrypted vault-style packages containing one module are supported.
- **dnd5e only** is the supported semantic target. The sampled legacy Well Met
  3.5E strings are display-only in a 5e template, not a 3.5E mechanics conversion.
- **Foundry v13 only** is the supported Foundry version; other versions/systems
  are not a compatibility promise. Square-grid/token and media limits still apply.
- Fog history, detection/vision permissions, actor automation, FG terrain and
  source environment/layer/grid-offset details remain incomplete. Source-compendium
  monsters/items beyond the optional dnd5e spell pack remain unresolved references.
- Playlist loop/fade/channel/volume/mode and weighted/formula table behavior need
  manual review. Missing art remains manual without a matching supplied Data root.
- **Unsigned .exe:** SmartScreen may warn. Code signing is not done; download only
  from the project release, then use More info → Run anyway if you choose to proceed.
- Install is add-only, refuses conflicts, backs up MyAssets and writes a receipt.
  Keep Toolkit closed. Uninstall with `--keep-changed` preserves edited notes.

Remaining engineering/cleanup scope is tracked in
[SCOPE-CHECK-2026-11-05.md](https://github.com/khantroll/ForgeBridge/blob/v0.13.0/docs/SCOPE-CHECK-2026-11-05.md), section B.
