# Final trial check installation — 2026-11-05

Windows, native reference Toolkit 0.5.1.18. **File-level evidence only**; Toolkit
was closed and was not launched. Both installs completed by 10:28 AM Central.
Machine-readable hashes, paths, counts and receipts are in the adjacent JSON.

PR #25 merged after green CI. PR #24 remains unmerged: its folder-local map
clash rule conflicts with library-wide uniqueness. A comment records that decision.
PR #26 remains unmerged, awaiting Claude's Toolkit check.

## Music and campaign output

The maintainer confirms 2026-11-04 native MP3 embedded unchanged in a song is audible.
Production accepts MP3 and OGG Vorbis unchanged, preserving the extension and
initializing Master at 80%. MPEG Layer III frames supply a bounded duration
without any external encoder; invalid/unsupported audio remains an explicit loss.
URL-encoded local audio references are decoded once, then revalidated for safe
contained lookup. Encoded traversal is rejected.

Count's Lair uses dnd5e 6.0.6 `C:/AMD/dnd5e/packs/spells`, PDF references,
map/notes folder **FB Campaign Check**, map **Count's Lair**. Campaign content:
18 actors, 17 items, three spells, three tables, one playlist, three tracks.
Ambient has **Manor**, **Crypt And Lair**, **Forest**; none missing. In particular,
`Crypt%20and%20Lair.mp3` resolves to the existing `Crypt and Lair.mp3`.
Independent reads of all three native song payloads match source SHA-256 exactly.
This build's audible acceptance is still pending; native-control confirmation
is not substituted for hearing the final playlist.

## Uninstall and install

- Previous audio receipt `forgebridge-c1639eb8b99442919f5fe5c529d5d547`:
  exit 0, removed six, no changed files.
- Previous campaign receipt `forgebridge-034c85bacbe7477d8b4f76713e2b2072`:
  exit 0, removed 333, kept the edited Boris v2 note. Older receipts already
  marked uninstalled were not rerun; all receipts/backups remain.
- Read-only replacement review correctly blocked the v2 Boris path conflict.
  The final generated campaign set uses internal revision v3, leaving the edited
  v2 note unchanged. A fake-MyAssets regression proves coexistence and preservation;
  the installer and its refusal rules are unchanged. No manual file deletion.
- FG install: exit 0, **10 added**. Receipt:
  `C:/AMD/fb-backups/forgebridge-1acd031c51ab414e9fe08b43c8bae6bf/uninstall.json`.
- Count's Lair install: exit 0, **346 added**. Receipt:
  `C:/AMD/fb-backups/forgebridge-8237ff77aa114e42935c3eea5c98b63c/uninstall.json`.
- Every installed file matches its receipt hash; preserved Boris hash is unchanged.

Final suite: **312 run, 308 passed, four Windows symlink tests skipped**.
PR #26's focused campaign suite: **8 passed** in its isolated checkout.

## Exact Toolkit check targets for Claude

Start only through the launcher. No Toolkit runtime check was performed here.

1. Audio → Playlists → **FB Campaign Check → Ambient**. Play **Manor**,
   **Crypt And Lair**, **Forest** separately; confirm each audible and Master 80%.
2. Notes → **FB Campaign Check**: **Spell Scroll: Bless**,
   **Spell Scroll Spiritual Weapon**, **Spell Scroll Protection from Poison**.
   Follow each link to **Bless**, **Spiritual Weapon**, **Protection from Poison**.
   Map: Maps → **FB Campaign Check → Count's Lair**.
3. Notes → **FB FG Notes Check**: **FB FG Goblin** (portrait/stat block),
   **FB FG Potion** (item), **FB FG Light** (spell), **FB FG Room** (story image
   plus links to goblin and potion). Reopen representative links/images.

FG source is the owned synthetic `C:/AMD/fb-final-fg-2026-11-05/control.mod`,
written with a module display name matching the requested notes folder. The
package is `with-story-image/native-package.zip` below that folder, built by
PR #26 commit `683d1e4`, not a merge into main. One NPC, item, spell and story;
NPC and story each resolve an embedded synthetic PNG. No commercial assets are
included in this evidence. FG runtime remains pending until Claude checks it.
