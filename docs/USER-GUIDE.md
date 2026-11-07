# ForgeBridge operator guide

ForgeBridge discovers scenes in a Foundry package and builds native Arkenforge
output with code-defined records. The default path needs no manual UVTT import,
map export or calibration and no pre-existing imported map. Existing calibrated
profiles remain optional advanced overrides. Every output still needs its own
Toolkit check; this tool does not claim lossless campaign/behavior conversion.

## Easiest: download the Windows app

No Python or Git installation is needed. Download
`ForgeBridge-<version>-windows-x64.zip` from
[GitHub Releases](https://github.com/khantroll/ForgeBridge/releases), then unzip
the whole folder somewhere you own, such as Documents. Do **not** unzip into
Program Files or MyAssets. Double-click **ForgeBridge.exe** for the GUI; follow
the Graphical workflow below. Keep both executables and the `_internal` folder
together; copying just the EXE will not work.

The command-line program is **forgebridge-cli.exe** (Windows cannot distinguish
ForgeBridge.exe from forgebridge.exe by capitalization alone). Open PowerShell
in the extracted folder for commands such as:

```powershell
.\forgebridge-cli.exe --version
.\forgebridge-cli.exe install --uninstall "C:\Backups\forgebridge-ID\uninstall.json" --keep-changed
```

For the other CLI examples below, replace `forgebridge` or
`python -m forgebridge` with `.\forgebridge-cli.exe` when using the Windows app.

The app is unsigned; code signing is not done yet. Windows SmartScreen may show
"Windows protected your PC". For a ZIP obtained from this project's release,
choose **More info → Run anyway**. Conversion errors show a message and write
`forgebridge-error.log` beside your output folder, or under
`%LOCALAPPDATA%\ForgeBridge` if that location cannot be used.

Release ZIPs are attached by the Windows build workflow on new release tags.
Development candidates are available as Windows standalone workflow artifacts
for review before a release is published.

## Option 2: Python setup and tested scope

- Python 3.13 is the Windows/Linux CI target; local Windows also tests 3.14.2.
  Path checks require Python 3.12+, but 3.12 is not the CI promise.
- Native protocol reference: Toolkit 0.5.1.18 / launcher 7.0.0.3. Other versions
  need validation. Real source corpus: Foundry v13 Count's Manor, plus synthetic
  module/world/Adventure fixtures; not every Foundry version or system.
- Use only source assets you may migrate. Imported JS/macros/active HTML never run.
- Folder and ZIP input support JSON/JSONL/NeDB and read-only LevelDB snapshots.

### Quick start (Windows, new users)

Type each line below into PowerShell on its own (do not paste the ```` ``` ````
fence lines). You need Git and Python 3.12 or newer from python.org; 3.13 and
3.14 are tested.

```powershell
cd C:\AMD                       # any folder you like
git clone https://github.com/khantroll/ForgeBridge.git
cd .\ForgeBridge                # git clone creates this folder; work inside it
git checkout v0.11.0               # the tested release
py -m venv .venv                # uses your newest installed Python
.\.venv\Scripts\Activate.ps1
python -m pip install .
forgebridge-gui
```

The last line opens the ForgeBridge window; continue with *Graphical workflow*
below. Next time, open PowerShell in the ForgeBridge folder, run
`.\.venv\Scripts\Activate.ps1`, then `forgebridge-gui` (or double-click
`forgebridge_gui.pyw`).

- If `Activate.ps1` is blocked, skip it and use `.\.venv\Scripts\python.exe -m pip install .`
  and `.\.venv\Scripts\forgebridge-gui.exe` instead. Don't change system security settings.
- If `py` says "No suitable Python runtime found", run `py --list` and use one of the
  listed versions, for example `py -3.14 -m venv .venv`.
- Optional self-check (prints a long JSON report; look for `"status": "PASS"` near
  the top): `forgebridge convert fixtures/synthetic-module --out "$env:TEMP\fb-check-1"`.
  ForgeBridge never overwrites, so use a new folder name each time.

### Developer setup

From a checkout, without installing:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt -r requirements-native-capture.txt
$env:PYTHONPATH = "$PWD\src"
python -m forgebridge convert fixtures/synthetic-module --out converted-example
```

On Linux use python3, source .venv/bin/activate and export PYTHONPATH="$PWD/src".
The packaged install includes pypdfium2. Conversion defaults to PDF page images
when it imports; otherwise PDFs remain references with an explicit loss reason.
CI runs the synthetic command.

## Graphical workflow

After setup, run `forgebridge-gui`, double-click forgebridge_gui.pyw on Windows (it prefers .venv's
Pythonw), or run `python -m forgebridge gui`. Tkinter must be installed. No web
server or browser is needed.

1. Choose the Foundry folder/ZIP and click Discover scenes.
2. Discovery starts with nothing selected. Rows show scene — Adventure name
   (pack folder), grouped by Adventure then scene name; without an Adventure
   name, the pack folder is shown instead. Select scenes (Ctrl-click for multiple),
   or use Select all / Clear. Pack/Adventure scope remains separate even if IDs match.
   Map folder and Notes folder start with the first displayed Adventure name
   (or package title, or ForgeBridge). Edit them as needed. Map names default to
   scene names: double-click a selected row or use Rename selected maps to edit.
   Names actually used after Windows sanitization appear in the build summary.
3. Click Choose where to save output and select a parent folder; the app proposes
   a new child folder and shows the full Folder to create path. Profiles are
   optional overrides; default output uses schema-built native synthesis.
4. Leave Convert PDF handouts into note pages checked for page images, or uncheck
   it to keep references. Build/export and read the source-stage and native-stage
   loss summary. Duplicate map names require renaming before building; no hash
   suffix is added. Existing destination map names are shown before installing.
5. Review before using Install reviewed native outputs. Select actual MyAssets
   and a separate existing backup folder; keep Toolkit closed and confirm the
   displayed destination/backup summary. Rejected/UVTT-only results cannot install.
   Opening notes in the Toolkit can change them; uninstall with --keep-changed
   later keeps those edits.

Wait for file work to finish before closing. The GUI has headless controller
coverage, but was not launched/visually validated by Codex in this session.

## Command-line conversion and output

### Fantasy Grounds modules

Use Choose FG module in the GUI, or give convert a `.mod`, an unpacked folder
containing `definition.xml`, or an unencrypted vault-style ZIP containing one
module under `modules/<name>/`. Detection is automatic; Foundry inputs retain
their existing workflow. FG normally keeps `.mod` files in
`%APPDATA%\SmiteWorks\Fantasy Grounds\modules` (AppData is hidden in Explorer;
paste this path into Explorer's address bar). Store and Forge `vault` content is
encrypted and **not supported**. Export an unprotected module from your own
campaign instead; ForgeBridge never bypasses protection.

```powershell
forgebridge convert "C:/Sources/MyModule.mod" --list-scenes
forgebridge convert "C:/Sources/MyModule.mod" --scene-key KEY --squares 40 --out "C:/Conversions/FG-01"
```

FG rows show the map name, module, READABLE/NEEDS_GRID/ART status and pixels per
square when known. ART pictures are hidden by default; CLI --include-art or the
GUI Include artwork (FG ART) checkbox lists them. Selecting ART does not invent
a grid. For NEEDS_GRID, select the row and choose Squares across or Pixels per
square. CLI --squares KEY=N and --grid-size KEY=PX may repeat per selected map;
the bare value works only when exactly one map is selected. A stored gridsize
always wins. Missing grids refuse that map; no grid is guessed. Fractional grids
resample the background to whole UVTT pixels per square, with source/output
dimensions and the approximation recorded.

Map folder defaults to the module display name, then its name; map name defaults
to the image record name. The same --map-folder, --notes-folder and keyed
--map-name overrides, Windows sanitization and clash rules apply. Native output
uses the existing 2.56 units/grid writer. FG pins, story, tokens, ambient/vision
and unsupported occluders remain explicit manual/unsupported losses; no Foundry
note/token stages run. Notes folder is reserved for future FG notes, not populated
with invented content. FG wall counts describe source polylines; native record
counts describe their straight segments. Native door counts include see-through
window portals. Source counts, metadata source, pixels/square, resampling and
graded FG losses appear in conversion-report.json and the GUI summary.

The same explicit --install flags and GUI reviewed installer use full backups,
refuse conflicts, and create receipts supporting uninstall/--keep-changed. Never
install a PARTIAL build. FG native output has synthetic/file-level coverage;
Claude's Toolkit check remains required for a new output.

#### NPCs, items and story

Map conversion does not write these notes. A separate command does, and only
from text stored in the module. Output is file-level only; Toolkit check
pending. Passing tests prove files and receipts, not that notes appear in the
Toolkit.

```powershell
python -m forgebridge.fantasy_grounds "C:/Sources/MyModule.mod" --campaign-out "C:/Conversions/FG-notes"
python -m forgebridge.fantasy_grounds "C:/Sources/MyModule.mod" --campaign-out "C:/Conversions/FG-notes" --install --myassets "C:/ArkenforgeData/MyAssets" --backup-root "D:/ForgeBridgeBackups"
```

`--campaign-out` writes the loose MyAssets tree, `fg-campaign-report.json`, and
an installable `native-package.zip`. That zip uses the same review, full
backup, uninstall receipt and `--keep-changed` path as Foundry native packages
(`forgebridge install --package …` also accepts it). `--install` requires
`--myassets` and `--backup-root`; Toolkit must stay closed.

What it writes (file-level only, Toolkit check pending):

- Each NPC becomes a 5e Character note: armor class, hit points, speed, ability
  scores, saves, skills, senses, languages, traits, actions, reactions and
  legendary actions. Walk speed is listed first. Repeated languages are kept
  once. An attack bonus is ability modifier + proficiency + item bonus when
  the module stores the ability. A different stored total is left as written.
- Each item becomes a 5e Item note. A spell item becomes a 5e Spell note only
  when the module itself contains the spell text. A name that only points at
  another FG library is skipped.
- Each story or encounter entry with text becomes one note. Links between
  those NPCs, items and story entries are kept. An image stored in the module
  is attached. A path that leaves the module is not opened.

What stays a loss, with the reason in `fg-campaign-report.json`:

- Missing scores, hit points, challenge rating, descriptions or story text.
- Bonus actions share the actions list, because the 5e Character note has no
  bonus-action field. Lair actions are not placed.
- Map pins, tokens on maps, and the map file itself are unchanged by this
  command. Do not treat a passing test as proof the Toolkit shows the note.

### Foundry packages

```powershell
python -m forgebridge convert "C:/Sources/MyModule.zip" --list-scenes
python -m forgebridge convert "C:/Sources/MyModule.zip" --out "C:/Conversions/MyModule-01"
python -m forgebridge convert "C:/Sources/MyModule.zip" --out "C:/Conversions/MyModule-01" --foundry-data "C:/Users/me/AppData/Local/FoundryVTT/Data"
```

`--foundry-data` is optional and read-only. Portraits and tiles whose paths
point at another module, such as `modules/legends-of-barovia-pk/assets/...`,
are read from inside that Data folder only. A path that leaves the folder, or
a file that is not there, stays a loss. Nothing is written into Data. This is
file-level only, Toolkit check pending. The GUI has Choose Foundry Data folder.

Repeat --scene ID or select exact --scene-key KEY from discovery. Default native
calibration is 2.56 units/grid, upper-left origin, native y up; source padding and
grid are normalized before synthesis. No source pixel/native coordinate shortcut.
Choose new output; existing paths are never refreshed or overwritten.

Visible naming options (default synthesis):

```powershell
forgebridge convert PACKAGE --scene-key KEY --out NEW_DIR --map-folder "The Count's Manor" --notes-folder "The Count's Manor" --map-name "KEY=Count's Lair" --pdf pages
```

Map folder defaults per scene to its Adventure name, then package title, then
ForgeBridge. Notes folder defaults to the same folder. Map name defaults to the
scene name alone. Repeat --map-name SCENE_KEY=NAME for multiple scenes, or use
--map-name NAME for one scene. Identical scene names across 5e/SA need explicit
overrides. Map names are unique across a build and must not already exist in the
destination, including another map folder. Review refuses these clashes and
suggests renaming; it never silently adds a hash. The add-only installer and
receipt/keep-changed uninstall rules are unchanged.

Names strip Windows-invalid punctuation/control characters and trailing dots or
spaces, must have 1–80 characters, and refuse reserved device names such as CON
or COM1. Apostrophes and spaces are retained. Actual names/paths appear in
output_names in each native report. Notes share the chosen visible folder; their
internal filenames retain a scene hash to avoid cross-scene collisions. Internal
media and token folders keep their existing hash scopes.

--pdf pages renders bounded handouts using the existing limits (32 pages per PDF,
64 MiB rendered bytes, capped image dimensions); --pdf references retains sources
without page images. Automatic mode chooses pages if pypdfium2 imports, otherwise
reports why references were used. Explicit pages requires an importable renderer;
invalid/oversized PDFs stay explicit reference-only losses. New naming controls
are for synthesized scenes; optional calibrated profiles keep their pinned naming
workflow through the package command rather than silently ignoring overrides.

Open conversion-report.json first: source/UVTT grades are retained separately
from native_counts/native_losses and each native_report. BUILT is not runtime
PASS. PARTIAL/exit 1 lists rejected scenes; invalid requests exit 2. Supported
features can coexist with explicit token/media/link gaps. No replacements for
unresolved source tables/media are invented. Counts are not a fidelity percentage.

MyAssets/ is the combined ready-to-copy native tree. Each scene also has a native
ZIP, UVTT ZIP, original companion and readable notes. Reports/original PDFs stay
outside MyAssets. Missing completion report means incomplete publication: preserve
it for inspection and choose a fresh destination after fixing the cause.

## Supported / manual / unsupported

| Feature | Scope |
| --- | --- |
| Geometry/background | Direct native maps, barriers, doors, lights, background assets and browser previews from known schemas; no native files shipped. |
| Notes and tokens | Existing journal/table/image/marker/token writers; supported square/static tokens preserve identity, position, footprint, scale, rotation and hidden state. |
| Non-success | Invalid marker positions/targets, unsupported token geometry/scales, source/media gaps and unsupported light ranges remain explicit. |
| Light fidelity | Uses observed Toolkit UVTT-import color/intensity defaults; independent Foundry color/intensity/animation mapping not claimed. |
| Scene motion / audio | Synthesized Foundry scenes support captured WEBM VP9 / MP4 H.264 video, animated GIF/PNG/WebP frames, and OGG/MP3/PCM-WAV map sounds. Codec/size and timing limits apply; new output needs Toolkit validation. Procedural light animation remains separate. |
| Fog/vision | Fresh native manual fog starts covered. Foundry exploration, vision/detection and token vision aren't converted. |
| Actors/behaviors | Source retained/reported; full actors/stats/combat/automation remain gaps. No script execution. |
| Labels | Off. Player behavior cannot be inferred from GM view. |

Advanced profile/capture/batch workflows remain in SCENE-PROFILES.md,
NATIVE-CAPTURE.md and SCENE-BATCH.md. Don't repin hashes just to clear errors.

## Installation, backups and recovery

Toolkit must stay closed; wait for the launcher to stop saying Running Arkenforge
Toolkit before relaunching. Keep Toolkit/launcher/helper non-elevated.

```powershell
python -m forgebridge convert "C:/Sources/MyModule.zip" --out "C:/Conversions/MyModule-02" --install --myassets "C:/ArkenforgeData/MyAssets" --backup-root "D:/ForgeBridgeBackups"
```

This deliberately authorizes add-only installation after build/conflict checks;
it does not pause for review. Prefer build-only plus the explicit install command
in SCENE-IMPORT-RELEASE.md when you want to review first. A full MyAssets backup
comes before copying; conflicts/running Toolkit/inspection failure refuse writes.
Only absent files are added; identical files untouched. Backups are separate,
existing folders. No permission/security changes or automatic elevation.

The backup run holds hashes and an uninstall receipt. Review later references
and preserve later edits before:

```powershell
python -m forgebridge install --uninstall "D:/ForgeBridgeBackups/forgebridge-RUN_ID/uninstall.json"
```

Only recorded unchanged additions are removed. Edited/missing additions block
removal; existing content, later user files, directories and backups remain.

Opening a converted note in the Toolkit can rewrite its file, so after real use a
plain uninstall may refuse with "Added file changed/missing". To remove
everything that is still exactly as installed and keep the changed files (they
are listed, and recorded in the receipt), add `--keep-changed`:

```powershell
forgebridge install --uninstall "D:/ForgeBridgeBackups/forgebridge-RUN_ID/uninstall.json" --keep-changed
```

Delete the listed kept files yourself afterwards if you do not want them.

Uninstall also removes folders the install created once they are empty; folders
that still hold kept or later files stay. Running `--uninstall` again on a
receipt that was already uninstalled only tidies such empty folders (useful for
receipts from v0.9.0, which left empty folders behind); it never deletes files.
INCOMPLETE receipts require manual review. Restore only reviewed affected backup
files with Toolkit closed; never Replace All or blind folder synchronization.

## Spells that need the free dnd5e system download

### Why some spells don't convert on their own

Many Foundry adventures don't store the full text of the spells they use. A
spell scroll or a monster's spell list often holds only a *link* to the spell,
and the spell itself lives in Foundry's free **dnd5e game system**, not in the
adventure you bought. ForgeBridge can only convert what it's given. Without the
dnd5e system, it can't see those spells.

Example: in *The Count's Manor*, the scrolls of **Bless**, **Spiritual Weapon**
and **Protection from Poison** are links like that.

### What happens if you skip this

Everything else still converts normally. The linked spells just don't become
spell notes. Each one is listed once in the conversion report as a missing
`external-spell`, and the link stays as plain text in the note that mentioned
it. Nothing is made up or swapped for a similar spell.

### How to fix it (about 5 minutes, no Foundry needed)

You **don't** need Foundry installed, running or licensed. You only need the
free dnd5e system download, which is about 108 MB.

1. Open the dnd5e releases page:
   <https://github.com/foundryvtt/dnd5e/releases>
2. Find the newest release that is **not** marked *Pre-release*. As of
   November 2026 that's **6.0.6**. Under **Assets**, download
   `dnd5e-release-<version>.zip`, for example
   [dnd5e-release-6.0.6.zip](https://github.com/foundryvtt/dnd5e/releases/download/release-6.0.6/dnd5e-release-6.0.6.zip).
3. **Unzip it** to a folder, for example `C:\Foundry\dnd5e`. Right-click the zip
   and choose **Extract All**. The folder should contain `system.json` and a
   `packs` folder, and the spells are in `packs\spells`.
   *Use the unzipped folder, not the .zip itself.* The release zip contains a
   large monster file that ForgeBridge's safety limits refuse to read from inside
   a zip.
4. Point ForgeBridge at that folder:
   - **Windows app:** in **Optional dnd5e system folder / spells pack**, click
     **Choose dnd5e system folder** and pick `C:\Foundry\dnd5e`.
   - **Command line:** add `--dnd5e-system` with that folder:

     ```powershell
     forgebridge convert "C:\Adventures\counts-manor" --out "C:\ForgeBridge\counts-manor-out" --dnd5e-system "C:\Foundry\dnd5e"
     ```

5. Check the report. The missing-spell entries are gone, and each linked
   spell is now its own 5e Spell note that the scroll or monster note links to.

**Already have Foundry installed?** You can skip the download and pick your
existing system folder, `<Foundry user data>\Data\systems\dnd5e`. Its spells are
in `Data\systems\dnd5e\packs\spells`.

### Details for advanced users

- `--dnd5e-system` accepts a dnd5e system folder (with `system.json` id
  `dnd5e`), or the spells pack folder by itself (`packs/spells`, LevelDB). It
  also accepts a standalone spells JSON/NeDB (`.db`) file. A bare pack means
  the `dnd5e.spells` namespace and gives no image root, so spell icons from it
  stay manual. Foundry's core `icons/...` images aren't in the system download
  either way, so spell portraits are reported as manual.
- A system ZIP is accepted only if every entry fits the read budget. The
  official 6.0.6 ZIP doesn't (`packs/actors24/000005.ldb` is about 8.6 MB), so
  unzip it first.
- Only the exact spells the adventure links to are converted, plus any spells
  those spells link to. ForgeBridge never matches by name and never swaps in a
  different edition. Both `Compendium.dnd5e.spells.ID` and
  `Compendium.dnd5e.spells.Item.ID` link forms work.
- Spell notes show text only. Slots, effects and automation aren't converted.
  `campaign_content[].spell_source` in the report lists the resolved and
  unresolved links and the system version and hash.
- The option applies to Foundry packages only, not Fantasy Grounds or legacy
  calibrated profiles. ForgeBridge refuses to run if an input changes during
  the build, if spell IDs are ambiguous, or if a path is unsafe. Inputs are never
  modified.

## Troubleshooting

Foundry campaign content is included automatically for the selected Adventure:
all roll tables, supported dnd5e actor stat blocks, item/spell notes and playlists,
alongside the chosen scenes. Shared content is counted once in
`conversion-report.json` → `campaign_content`; per-scene reports list static
tiles and omitted token-link losses. Token portraits use the v0.10 Size/icon
notes; adding stat links caused note-marker rendering in Toolkit, so actor
notes remain separate. Review the graded losses before installing. Stat
blocks are display content, not actor automation. Missing portraits stay manual.
Local MP3 and OGG Vorbis tracks are embedded unchanged, retaining their original
format; no encoder or Toolkit ffmpeg is needed. Jeffrey confirmed native MP3
and OGG playback in Toolkit 0.5.1.18; each rebuilt playlist still needs listening. New campaign fields, playlists
and tile placements still require Toolkit acceptance. See
[native campaign details](NATIVE-CAMPAIGN-CONTENT.md).
Playlists now use their display-name filenames inside the chosen notes folder
in `MyAssets/Playlists`, with current Toolkit user metadata. Listing and playback
await recheck. Corrected generated notes use revision-scoped `Campaign-vN-` filenames; edited
predecessors kept by uninstall remain preserved and are not overwritten. Campaign
playlist filenames also carry the internal revision while their displayed names
remain unchanged.

| Symptom | Action |
| --- | --- |
| Conflict/existing output | Select a new output; preserve/review user edits. Never overwrite to clear it. |
| Hash mismatch with advanced profile | Restore pinned inputs or deliberately recapture the correct profile; no blind repinning. |
| ICE/unstable Toolkit | Stop projection, close normally, use Claude's built-in browser at http://127.0.0.1/ with Waterfox/Chrome player tabs closed. This is an observed browser/session pattern, not a proved cause or converter defect. |
| Relaunch fails | Wait until the launcher no longer reports Toolkit running; no duplicate/elevated instances. |
| Black player view with fog text | Check native fog and framing on a disposable copy; fog-off and bounded reveal/persistence are distinct checks. Preserve original profile maps. |
| Windows LevelDB .dbtmp error | Retain diagnostics and stop that operation. Host intermittency remains unresolved despite clean CI; no blind retries, new probes or automatic Defender/indexer exclusions. Jeffrey owns exception decisions. |
| Lock/backup failure | Inspect the active/interrupted install and retained receipt; don't remove unfamiliar locks or bypass the closed-Toolkit guard. |
| Size limit | Export/select fewer scenes. Backup: 16 GiB/100k entries; combined review: 1 GiB/16384 native files; conversion tree: 1 GiB/16384 files. |
| PDF renderer absent | Keep PDFs manual, or install optional PDF requirements. Skips are not renderer acceptance. |

Runtime checks belong to Claude; see ACCEPTANCE-MATRIX.md and his direct-map
note. This guide adds no Toolkit observations or M1 acceptance claims.

### Animated map tiles and ambient sounds (development branch)

Normal Foundry `convert` writes supported tiles and AmbientSound documents into
the same native scene package. Read `native_counts.animated_tiles` /
`ambient_sounds` and each scene's `static_tiles` / `ambient_sounds` audits plus
`native_losses`. These file-level results do not prove playback or audibility.

- WEBM VP9 and MP4 H.264/AVC: one video track, original bytes embedded, muted,
  captured autoplay/loop defaults, generated play-symbol thumbnail. Codec headers
  are inspected, not fully decoded by ForgeBridge; other containers/codecs are losses.
- Animated GIF/PNG/WebP: decoded composed RGBA frames, at most 128 frames and
  16 million total frame pixels. Uniform timing maps to FPS (capped 60); variable
  timing is approximated by mean frame duration and reported. Missing/invalid
  frame durations assume 100 ms and add an explicit loss. Position, square
  footprint, clockwise rotation and hidden state map independently.
- Sound: OGG Vorbis, MP3 or mono/stereo uncompressed PCM WAV, maximum 16 MiB
  per source asset (tiles have the same byte limit). Position includes source
  padding/origin. Radius in source distance units / grid distance gives squares,
  then ×2.56 native units. Native falloff outer radius is that boundary; eased
  sources approximate linear attenuation from the centre. Without easing the
  outermost 0.1% is a small native falloff edge. Walls, precise easing curves,
  schedules, levels/channels and effects require review. Preset/track gain stays
  1; the map attachment carries source volume. Source hidden disables sound.
- Static tiles remain supported. Unsupported/unsafe/missing assets are explicit
  losses, with no invented replacement. No external/Toolkit encoder is used.

The owned FB Motion Check fixture shows separate nonoverlapping radius rings;
use its validation checklist before accepting this converter-written output.
### Native fog, vision and light effects

Conversion reports include a `visibility` section. Foundry scene fog configuration, bounded character vision and recognized flicker/blink effects are written from captured native schemas. Review fog and global darkness settings manually; historical reveal masks are not migrated. NPCs do not gain vision lights. Unsupported modes/animations and uncalibrated scene darkness remain losses. Native runtime acceptance is pending.
