# Optional compendium spell notes — file validation

Windows, Python 3.14; native schema reference Toolkit **0.5.1.18**. Toolkit was
closed for all builds/tests/installation below. No new native runtime PASS.

| Check | Result | Evidence |
|---|---|---|
| Exact legacy and Item-qualified UUIDs; shared/cyclic closure | PASS, synthetic file level | `tests/test_spell_source.py`: three reference IDs, exactly three imported spells, unused spell excluded |
| Actor prose links to native Spell notes | PASS, synthetic file level | Rich-text targets close; external IDs do not claim unqualified world Item aliases |
| Captured Spell schema and styles | PASS, file level | Compare emitted class/member/types and font against `fixtures/arkenforge-5e-templates/5e-Spell.rwnote`; library IDs are stream-local |
| System ZIP/image root and standalone JSON/NeDB/LevelDB | PASS, synthetic file level | Same test module; snapshots leave source hashes unchanged; bare packs grant no neighboring-media access |
| Missing ID/input, ambiguous IDs, unsafe archive, changed input, output containment | PASS, synthetic file level | Explicit losses/refusal; changed input never publishes destination |
| CLI and GUI optional input | PASS, headless/file level | Public convert and GUI callback regression tests |
| Real Count's Lair without optional pack | PASS, file level only | Exit 0; counts and three exact unresolved UUIDs below |
| New synthetic Spell notes in Toolkit | NOT CHECKED | Installed for Jeffrey's short check below |
| Real three compendium spells in Toolkit | BLOCKED | Matching dnd5e source pack not located/supplied; no replacement rules invented |

Full Windows suite: **301 run, 297 passed, four Windows symlink tests skipped**.
Those skipped tests are not counted as passed safety coverage. Linux/Windows
and standalone CI outcomes are tracked on the feature PR, not inferred here.

## Real package build (not installed)

Input: `C:\AMD\lob-counts_manor-pk-v13\ForgeBridge\lob-counts_manor-pk-v13`.
Count's Lair adventure-5e scoped key `28b08edf2e1148dd7e2e02c8`;
`--pdf references`, no optional system input. Output:
`C:\AMD\lob-counts_manor-pk-v13\ForgeBridge\.test-tmp\spell-notes-lair-no-system-2026-11-03`.
Map `MyAssets/Maps/The Count's Manor/Count's Lair.rwmap`.
Native counts: 18 actors, 17 items, 3 tables, 0 spells, 1 playlist,
3 manual audio tracks, 11 tokens, 12 room markers, 2 static tiles.
Native package SHA-256:
`ee20d123d0f8989505c959e7ad0eb4bfb4b38d447575d1a3b30571d51ce37e8e`.

Missing exact external targets, retained as graded `external-spell` losses:

- Bless: `Compendium.dnd5e.spells.8dzaICjGy6mTUaUr`
- Spiritual Weapon: `Compendium.dnd5e.spells.JbxsYXxSOTZbf9I0`
- Protection from Poison: `Compendium.dnd5e.spells.MAxM77CDUu8dgIRQ`

These links occur on the three corresponding scroll Item notes. The package
does not supply the target spell payloads. The usual local Foundry AppData
system locations and repository did not contain a dnd5e source pack. The
optional-path question remains open; the implementation does not depend on an
answer. This is not a claim that a different-edition spell with the same name
is equivalent.

## Installed synthetic check — deliberately not real spell rules

While trial was active and Toolkit closed, the normal installer added **8**
files, exit **0**. No existing files were overwritten or uninstalled.
The package contains three synthetic spell payloads with the reference IDs,
obvious synthetic names/descriptions, and a synthetic caster linking them.
It tests schema/link rendering only, not the real spell contents.

Package:
`C:\AMD\lob-counts_manor-pk-v13\ForgeBridge\.test-tmp\spell-notes-toolkit-check-2026-11-03\native-package.zip`.
SHA-256: `5bf8c83b8c62b9f922daa36393efa3b1a8483857e3fa3316719d77f2fbc70ea5`.
Backup:
`C:\AMD\fb-backups\forgebridge-0dfc37eda81046f983a866b594833dfb\MyAssets`.
Receipt (retain):
`C:\AMD\fb-backups\forgebridge-0dfc37eda81046f983a866b594833dfb\uninstall.json`.

Jeffrey's five-minute check, starting Toolkit from the launcher:

1. Notes → **FB Spell Notes Synthetic Check** → **FB Spell Notes Synthetic Caster**.
2. In Biography, follow each of its three links. Confirm each reaches its
   matching **FB Spell Notes Synthetic Bless / Spiritual Weapon / Protection
   from Poison** note, not another campaign's note.
3. Confirm the 5e Spell block displays name, type, casting time, range,
   components, duration, description and higher-level text. The descriptions
   explicitly say synthetic and are not game rules.
4. Report rendering/link failures exactly. Quit without changing/saving user
   campaign content. This is separate from the still-pending FB MP3 Test
   by-ear listening result and real compendium-content acceptance.

Labels remain off; fog/vision, animation and actor/slot/effect behavior retain
their prior limits. Nothing in this check upgrades those capabilities.
