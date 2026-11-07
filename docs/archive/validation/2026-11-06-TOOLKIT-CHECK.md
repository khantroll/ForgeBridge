# Toolkit check — 2026-11-06 (Claude + Jeffrey), last trial day

Toolkit 0.5.1.18 from the launcher. Nothing saved except the two capture maps
(FB Capture Base / FB Capture Effects, see fixtures/arkenforge-fog-vision-2026-11-06).
Accidental edits on FB FG Owned Map were discarded (No to save).

## PR #31 — animated tiles and ambience: PASS
| Target | Result |
|---|---|
| Upper-left WEBM tile | PASS — test-pattern timer changes between frames (loops) |
| Upper-middle GIF tile | PASS — inner square cycles yellow → blue → green |
| Lower-left 440 Hz OGG / lower-right 660 Hz WAV ambience | PASS — native sound objects (e.g. "FB Left OGG 440Hz") at circle centres; Jeffrey heard the audio |
| FB Motion Watcher (no CR) | not opened |

## PR #32 — Fantasy Grounds real adventure: PASS with defects
| Target | Result |
|---|---|
| Owned map pin → story note | PASS — pin "FB FG Room" opens the story note (paragraphs, list, WatcherKey link) |
| Owned map tokens | PASS — "Second watcher", "Watcher token" show portraits, size, rotation (no cyan pin) |
| Well Met NPC "Blood Priest" (3.5E) | PASS — portrait, AC 15 touch/flat-footed, HP 36 (4d8+4) tracker, skills, Challenge 4, special attacks |
| Well Met story "Narrative 1: Arrival in Kith'takharos" | PASS — full text |

Defects to fix before merge:
1. Literal `\r\r` sequences in NPC special-attacks text ("…Spell Level)\r\rLevel 0 Spells…"): FG `\r`/newline escapes must become line breaks.
2. FG story/text fields render dim grey on dark background with no paragraph spacing: use the same readable text colour/spacing as Foundry journal notes.
3. Blank gap above Challenge in the 3.5E stat block (empty lines still occupy space).

## Fog, vision, light animation
Native controls captured (fixtures/arkenforge-fog-vision-2026-11-06). No converter
build was installed before the trial ended, so Foundry → native fog/vision/animation
is file-level only from here on.
