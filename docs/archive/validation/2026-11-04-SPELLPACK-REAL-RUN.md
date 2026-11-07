# Real dnd5e 6.0.6 spell pack: file-level run

Date 2026-11-04. Linux box, Python 3.13.5, ForgeBridge 0.11.0 (main `8908a7d`
plus branch `docs/spell-pack-and-real-run`). **File-level evidence only.**
Nothing was installed into the Arkenforge Toolkit, and no runtime validation
was done. Machine-readable result: `2026-11-04-spellpack-real-run.json`.

## Inputs

- dnd5e system **6.0.6** (latest full release; 6.1.0 is a pre-release and was
  not used): `dnd5e-release-6.0.6.zip`, SHA-256 `88c4013a5fb9aaaae18405b6a7eda69fd72c4f0b74920906c899c6df6b617595`, from
  https://github.com/foundryvtt/dnd5e/releases/tag/release-6.0.6.
- Source: the real Count's Manor package lives only on the Windows PC and wasn't
  available on this host. Instead, `fixtures/synthetic-module` with
  `packs/items.db` replaced by three scroll Items. Each scroll links exactly
  one Count's Manor UUID, the same link form the real scrolls use:
  Bless `Compendium.dnd5e.spells.8dzaICjGy6mTUaUr`, Spiritual Weapon
  `...JbxsYXxSOTZbf9I0`, Protection from Poison `...MAxM77CDUu8dgIRQ`.
  This proves the real pack resolves those IDs. A real-package rerun on Windows
  is still recommended.

## Commands

```
forgebridge convert source --out out-none   --pdf references
forgebridge convert source --out out-zip    --pdf references --dnd5e-system dnd5e-6.0.6.zip
forgebridge convert source --out out-folder --pdf references --dnd5e-system dnd5e-606        # unzipped
forgebridge convert source --out out-bare   --pdf references --dnd5e-system dnd5e-606/packs/spells
```

## Results

| Input | Exit | Spell notes | external-spell losses | dnd5e link losses | Campaign losses |
|---|---|---|---|---|---|
| none, main `8908a7d` (before fix) | 0 | 0 | 3 | 3 (duplicate) | 13 |
| none, this branch | 0 | 0 | 3 | 0 | 10 |
| system **ZIP** | **2** | none, refused | n/a | n/a | n/a |
| unzipped system folder | 0 | **3** | 0 | 0 | 13 |
| bare `packs/spells` | 0 | **3** | 0 | 0 | 13 |

The ZIP was refused with `zip entry exceeds the read budget:
packs/actors24/000005.ldb` (8,626,555 bytes, over the per-entry budget).
The user docs say to unzip first. Raising the budget is a separate decision
and wasn't made here.

With the pack, the three `external-spell` (manual) losses are gone. Three
`spell` (approximate: display only, no automation) and three `portrait`
(manual: Foundry core `icons/...` aren't in the system download) losses are
added. Each scroll note's link targets its spell note (3/3). Provenance:
system dnd5e, version 6.0.6, layout "system package".

Spell block fields (unzipped folder run):

| Field | Bless | Spiritual Weapon | Protection from Poison |
|---|---|---|---|
| Type | 1-level enc | 2-level evo | 2-level abj |
| Casting time | 1 action | 1 bonus | 1 action |
| Range | 30 ft | 60 ft | touch |
| Components | vocal, somatic, material, concentration (A sprinkling of holy water) | vocal, somatic | vocal, somatic |
| Duration | 1 minute | 1 minute | 1 hour |
| Description | SRD 5.1 text, present | present | present |
| At Higher Levels | empty | empty | empty |

Cosmetic follow-ups, not fixed here: abbreviated school and ordinal ("1-level
enc" should read "1st-level enchantment"), "1 bonus" should read "1 bonus
action", concentration is listed under components rather than duration, and
higher-level text is empty because 6.0.6 keeps scaling in activities.

## Not proven

- Rendering in the Toolkit and link-following for the real three spells. The
  Toolkit check of the synthetic Spell notes passed on 2026-11-04, and the same
  writer and schema are used here.
- The real Count's Manor package end to end with the pack (Windows host).
