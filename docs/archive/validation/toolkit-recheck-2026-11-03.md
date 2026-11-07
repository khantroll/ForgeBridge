# Campaign-content Toolkit recheck — 2026-11-03

Windows, Arkenforge Toolkit **0.5.1.18**, launcher **7.0.0.3**.
Branch `campaign-content`, tested code `b79bbaaeec98b12bc003645febc00bfdc7f68adc`
(corrected writers `b3d67a0a96ce36385c6fe9302ab9f0538edd2694`).
Pulled with `git pull --rebase` before starting. This checks the existing installed
Count's Lair and audio experiment from [the preparation report](2026-11-03-CAMPAIGN-RECHECK.md),
not a rebuild or another installation. The requested handoff was read from
`origin/main:docs/HANDOFF-2026-11-03.md`; it is not on this branch.

## Runtime observations

| Check | Result | Observation / evidence |
|---|---|---|
| Desktop control | PASS | Window enumeration, activation, capture and clicks worked. No text entry was needed. No capture timeout occurred during this recheck. |
| Start correctly | PASS | No MastersToolkit process/window existed before launch. Clicked **Launch Arkenforge Toolkit** in the existing launcher; never executed MastersToolkit.exe directly. [Launcher](toolkit-recheck-2026-11-03/01-launcher-before-start.png), [Toolkit](toolkit-recheck-2026-11-03/02-toolkit-started.png). |
| Playlist listing | PASS | **Ambient** and **FB MP3 Test** appear under **FB Campaign Check**. [Library](toolkit-recheck-2026-11-03/03-playlists-visible.png). |
| Song listing | PASS | **FB MP3 Test - MP3 original** and **FB MP3 Test - OGG Vorbis converted** both appear, each **01:01**. [Tracks](toolkit-recheck-2026-11-03/04-mp3-test-tracks-listed.png). |
| MP3 UI playback | PASS | Clicked **Start playlist**. Footer selected MP3 original; timer advanced from **00:00** to **00:19**. No visible error message. [Timer](toolkit-recheck-2026-11-03/05-mp3-timer-advanced.png). |
| OGG UI playback | PASS | Clicked OGG's explicit play icon. Footer selected OGG Vorbis converted; timer advanced from **00:00** to **00:09**. No visible error message. [Timer](toolkit-recheck-2026-11-03/06-ogg-timer-advanced.png). Playback stopped afterward. |
| MP3 and OGG audible output | NOT CHECKED | Desktop tools expose screenshots/input, not a way to listen to this PC's output. Advancing timers do not prove audible sound or codec correctness. Production MP3 migration remains manual. |
| Boris stat block | PASS | **Armor Class 10**; **Claws: +1 to hit**; **Bite: +3 to hit**; **Languages common**; **Speed 30 ft, climb 30 ft**. HP **20 / 20 (3d8 + 4)**, proficiency **+2**. [AC/speed](toolkit-recheck-2026-11-03/07-boris-ac-speed.png), [languages](toolkit-recheck-2026-11-03/08-boris-languages.png), [attacks](toolkit-recheck-2026-11-03/09-boris-attacks.png). |
| Count's Lair loads | PASS | Opened **Maps → FB Campaign Check → Count's Lair**, successful-load notification. No map objects moved or edited. |
| Portrait regression, representative tokens | PASS | Six upper-room Dark Soul tokens visibly retain circular portrait sprites beneath cyan hidden-state **eye badges**, rather than replacing the sprite with a note pin. This was observed at 100–71% before zooming out. |
| Exact all-token portrait/pin census | NOT CHECKED | Full overview shows ten eye badges at hidden-token locations, but remaining sprites are too small for a reliable individual portrait/pin census at 25%. No cyan note-pin replacement was observed. Do not turn the file-level count of 11 below into an all-11 runtime PASS. [Full overview](toolkit-recheck-2026-11-03/10-counts-lair-overview.png). |
| Quit without saving | PASS | Stopped audio, clicked Quit, answered **Yes** to “Would you like to exit the Arkenforge Toolkit?”. Toolkit closed; subsequent process check found none. **No save prompt appeared**, so there was no save question to answer No. No Save action was used. |

Boris's natural AC is explicitly 10 in the Foundry source. Claws explicitly uses
INT 8 (−1), plus proficiency +2, hence +1; Bite uses STR 12 (+1) plus +2, hence +3.
The retained 10/+1 are source-faithful values, not a claim that DEX controls these
two fields. Languages are no longer duplicated, and walk speed is first.

Only library navigation, audio playback, note reading, camera zoom and exit were
performed. No visibility badge, tracked HP, edit pencil, fog control or Save was
clicked. Existing rendering/stream settings were left alone. Tests and file
auditing ran only after Toolkit closed. A startup one-second CPU sample reported
70.4% total on two logical CPUs; it includes sampling overhead and does not prove
a capture-timeout cause. Captures remained responsive, so no recovery was needed.

## Installed-file fallback (read-only, after exit)

[Machine-readable audit](toolkit-recheck-2026-11-03/installed-audit.json) and
[reproduction script](toolkit-recheck-2026-11-03/audit_installed.py).
These results inspect serialized data and do not replace the runtime observations.

- **PASS:** Both playlist metadata declarations match
  `fixtures/arkenforge-user-playlist/toolkit-empty-playlist.rwmeta`, including
  `_prevPathIfDeleted` and inherited `ArkenBaseMeta+_prevPathIfDeleted`, both null.
  Primitive metadata differences from that empty fixture are only the two name
  members. Ambient contains zero songs (three production MP3 tracks remain manual);
  FB MP3 Test contains the two experiment entries. Display-name filenames and the
  selected folder are correct.
- **PASS:** Both song metadata declarations match the complete captured user
  `ArkenAudioMeta` schema. Intentional SFX-control difference: `_isSong=True`.
  Both durations are 61.04090881347656 seconds. Embedded bytes retain the original
  MP3 SHA-256 `4e77a7a0717560718c79660e525b71ed37399e863a8a0e27bdcb15d27585ef04`
  and converted OGG SHA-256 `b5e1fcf41c0a9160a819155ce9ce33053778af9bce517f59b7e79a36b77a27d6`.
  `_originalFile` ends in `.mp3` / `.ogg` respectively. This is byte evidence,
  not audible playback evidence.
- **PASS:** Boris's typed `ArkenNoteFieldStatBlock5e` declaration matches
  `fixtures/arkenforge-5e-templates/5e-Character.rwnote`. Filled actor values,
  portrait, optional-field flags and action lists intentionally replace the
  generic template content. Decoded text agrees with the displayed values above.
- **PASS (files only):** Count's Lair contains **11 generated tokens**: Count
  Lugosi, six Dark Souls, two Skeletons, Swarm of Spiders and Willa. Ten are hidden;
  Willa is visible. All 11 retain independent native note references, reachable
  portrait icons and category/Size fields; none has the extra text/actor-link field
  that caused the pin regression. Actor stat blocks are separate notes; token
  notes intentionally are not 5e Character-template notes. Twelve separate journal
  markers are expected and are not counted as failed tokens.

### Toolkit automatic writes, preserved

Receipt hashes were clean before this session. After exit all **340** installed
files still exist; **338** retain their receipt hashes. Toolkit automatically
rewrote these two files even though no Save action or content edit was performed:

1. `MyAssets/Encyclopedia/Notes/FB Campaign Check/Campaign-v2-edfc87a75fc39f64264e-7160079c8c68016e7452.rwnote`:
   decoded member values match the original package (zero value differences).
2. `MyAssets/Playlists/FB Campaign Check/FB MP3 Test.rwpl`:
   both song ContentItem records omit `_officialFlag`, previously false.
   No other decoded value differences were found.

Neither file was restored, deleted or rewritten by ForgeBridge. Receipt-based
uninstall should use `--keep-changed` to preserve these Toolkit rewrites. The audit
records exact paths and screenshot hashes. No claim is made about unrelated
Toolkit settings/autosave files outside these receipts.

Campaign receipt:
`C:\AMD\fb-backups\forgebridge-034c85bacbe7477d8b4f76713e2b2072\uninstall.json`
(334 files). Audio receipt:
`C:\AMD\fb-backups\forgebridge-0c74d4820ef94387863b38923f695505\uninstall.json`
(6 files).

## Automated checks

Full source suite after closing Toolkit: **292 run, 288 passed, four Windows
symlink-privilege skips**, zero failures, 134.917 seconds; see
[test log](toolkit-recheck-2026-11-03/tests.txt). An earlier filesystem-sandbox run
failed on denied temporary-directory access (182 errors); the complete rerun
outside that sandbox passed. No errors were suppressed or tests altered.
No production code changed in this
recheck. Remaining human checks are audible MP3/OGG output and a close-up census of
the remaining five token portraits. Other profile/player/fog milestones are not
retested or upgraded by this report.
