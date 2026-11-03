# Campaign content: file-level validation, 2026-11-02

Superseded limits: Claude's 2026-11-03 Toolkit check found invisible playlists
and note-marker rendering after token links. Those behaviors were never passed
by this file-level report. See [fix/recheck evidence](2026-11-03-CAMPAIGN-RECHECK.md).

PASS: schema/serialization/dependency/source-preservation checks. Runtime remains PENDING Claude.
Toolkit was not launched, and real MyAssets was neither read nor installed into. Captured schema reference: Toolkit 0.5.1.18.

Implementation: `4b86358dd889568c647475dec068508a29a63815`. Platform: Windows-11-10.0.26200-SP0; Python 3.14.2.

Follow-up `98e979e` makes the neutral OGG track-volume dictionary defaults internally consistent (empty HashSize/Version with no key/value entries), with a synthetic regression. It does not affect this real case, whose tracks are all MP3/manual and whose playlists contain no song entries. Its Windows/Linux suites and frozen-EXE smoke passed; the existing repeat job was still finishing when this evidence was recorded.

Fresh output: `C:\AMD\lob-counts_manor-pk-v13\ForgeBridge\.test-tmp\campaign-manor-5e-validated-2026-11-02`. Selected every scene whose discovery source_path is `packs/adventure-5e` (17 scoped keys).
Used the public convert API with `pdf="references"`, no install. PDF rendering was deliberately excluded from this campaign check.
The source package fingerprint matched before/after conversion; this is provenance, not runtime evidence.

Counts: {"actors": 18, "items": 17, "manual_tracks": 3, "markers": 79, "notes": 1009, "playlists": 1, "rejected_tokens": 1, "scenes": 17, "spells": 0, "static_tiles": 15, "tables": 3, "token_actor_links": 28, "tokens": 28, "tracks": 0}.
Campaign content counts once across all scenes: 3 range tables, 18 actors, 17 item notes, no source spells, 1 playlist, 0 embedded tracks / 3 manual MP3 tracks, 38 shared notes.
All 18 actor graphs retain the captured 5e heading/body fonts and stat colours; HP, optional flags, rich runs, spell/item blocks and links also have synthetic regression coverage.

| Scene | Walls | Doors | Lights | Tokens | Rejected | Tiles | Actor links |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Manor - 1st Floor | 164 | 12 | 24 | 0 | 0 | 1 | 0 |
| Ritual Chamber - M | 4 | 0 | 13 | 0 | 0 | 1 | 0 |
| Crypt Tomb - M | 4 | 0 | 2 | 0 | 0 | 0 | 0 |
| Count's Lair | 137 | 12 | 17 | 11 | 0 | 2 | 11 |
| Manor - 4th Floor | 41 | 6 | 1 | 3 | 0 | 2 | 3 |
| Counts Lair - M | 4 | 0 | 2 | 0 | 0 | 0 | 0 |
| Dungeon Cell - M | 4 | 0 | 2 | 0 | 0 | 0 | 0 |
| Manor - 3rd Floor | 49 | 12 | 4 | 2 | 0 | 2 | 2 |
| Carriage - M | 4 | 0 | 2 | 1 | 0 | 0 | 1 |
| Crypt Hall - M | 4 | 0 | 3 | 0 | 0 | 0 | 0 |
| Crypt Stair Case - M | 4 | 0 | 2 | 0 | 0 | 0 | 0 |
| Manor - 2nd Floor | 56 | 7 | 18 | 1 | 0 | 2 | 1 |
| Count's Crypt | 199 | 23 | 66 | 9 | 1 | 4 | 9 |
| Main Hall - M | 4 | 0 | 8 | 0 | 0 | 0 | 0 |
| Dining Hall - M | 24 | 0 | 11 | 0 | 0 | 0 | 0 |
| Count's Manor - M | 4 | 0 | 5 | 0 | 0 | 0 | 0 |
| Conservatory - M | 10 | 0 | 7 | 1 | 0 | 1 | 1 |

## Limits and evidence

- 14 portrait references and six Crypt tile references point outside the supplied package; no loose workspace image was substituted. Other missing tile references are enumerated in the JSON.
- Three dnd5e compendium spell references are outside the package and remain plain text with manual losses.
- Lingering Injuries retains its source ranges and 1d2 formula mismatch as an approximation. No source roll was run or repaired.
- MP3 playback is unknown; all three tracks are manual and the native Ambient playlist has no song entries. Synthetic OGG bytes/provenance/closure are tested; playback is not.
- Token notes link to central stat blocks without replacing the icon/Size fields. This is navigation, not a native actor binding or live HP sync.
- Actor automation/effects/resources/vision/deltas, animated tiles, procedural light animation and fog/vision conversion remain manual/unsupported. Labels stay off.

Windows full suite: **282 run, 278 passed, four skipped, zero failures**. Skips are symlink privileges, not passed safety checks.
CI source Windows/Linux suites, existing repeat job and built-EXE smoke all passed at the implementation commit; links are in the companion JSON.
The fake-MyAssets test installed campaign/playlist files, kept an edited stat block with --keep-changed and preserved an existing user file. No real installation was attempted.

The first all-scene pass exposed an overcount of external/shared table targets; the report now counts emitted notes. A captured-font comparison also corrected generic fonts/black stat text to the captured 5e fonts/colours. This fresh case includes both fixes; earlier/interrupted test outputs are retained separately and are not this evidence.

Package SHA-256 hashes, counts, manual asset references, source provenance and test-log hash: [file results](2026-11-02-campaign-content-file-results.json).
No Arkenforge behavioral PASS is inferred from hashes, graphs, byte preservation or dependency closure.
