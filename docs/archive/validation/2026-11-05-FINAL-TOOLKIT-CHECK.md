# Final Toolkit check — 2026-11-05 (Claude + Jeffrey)

Toolkit 0.5.1.18 started from the launcher (trial: 1 d 4 h remaining at 14:29 CT).
Checks the installs in [2026-11-05-FINAL-TRIAL-BUILD.md](2026-11-05-FINAL-TRIAL-BUILD.md).
Nothing edited or saved; quit with Yes to exit, no save prompt.

| Check | Result | Notes |
|---|---|---|
| Ambient playlist listed (FB Campaign Check) | PASS | 3 songs, 03:01: Manor 01:00, Crypt And Lair 01:01, Forest 01:00 |
| Manor audible | PASS | Jeffrey heard it; timer advanced |
| Crypt And Lair audible | PASS | Jeffrey heard it (URL-encoded source path resolved) |
| Forest audible | PASS | Jeffrey heard it |
| Spell Scroll: Bless → Bless | PASS | Link opens the 5e Spell note (1st-level enchantment, fields filled) |
| Spell Scroll Spiritual Weapon → Spiritual Weapon | PASS | Opens; 2nd-level evocation |
| Spell Scroll Protection from Poison → Protection from Poison | PASS with defect | Opens; text shows raw `&Reference[poisoned apply=false]` |
| FB FG Goblin | PASS | Portrait image, AC 15, HP 7 (2d6) tracker, speed, six scores |
| FB FG Potion | PASS | 5e item card, type and description |
| FB FG Light | PASS | 5e spell card, all fields |
| FB FG Room | PASS | Story image + text; *goblin* link opens FB FG Goblin |

## Defects to fix (non-blocking)

1. Foundry `&Reference[...]` enrichers are not stripped (Protection from Poison).
   Render the reference's label (`poisoned`).
2. Scroll → spell links are pale blue on parchment and hard to see.
3. FG stat block: empty Skills/Senses/Languages labels still shown;
   Proficiency Bonus "Unknown" when CR missing; type line empty.
4. Cantrip level shows "0-level evocation" (should be "Evocation cantrip").

Not checked here: Count's Lair map/tokens in this build (unchanged map writer;
checked 2026-11-03), Master 80% mixer value (mixer panel did not expand).
