# ForgeBridge operator guide

ForgeBridge turns Foundry v13/dnd5e packages and unencrypted Fantasy Grounds Unity
modules into Arkenforge maps and notes. You do not need Python when using the
Windows app, or a manual UVTT import/map export for normal conversion. Keep your
original package: the report lists missing or approximate content.

Current release: **v0.13.0**. The Toolkit trial has ended. Earlier observations and
new file-level-only features are separated in [the release notes](RELEASE-NOTES-v0.13.0.md).
Passing conversion is not proof of appearance, audio or player behavior in Toolkit.

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
git checkout v0.13.0               # the tested release
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

1. Open **ForgeBridge.exe**. Use **Choose folder** / **Choose ZIP** for a Foundry
   package, or **Choose FG module** for a Fantasy Grounds `.mod` file. An unpacked
   FG module folder can also be selected with Choose folder.
2. For Foundry only, optionally choose the **Foundry Data folder** for missing
   portraits/tiles, and the **dnd5e system folder / spells pack** for external spell
   links. Both are explained below; leave them blank if you do not have them.
3. Click **Discover scenes**. Nothing is selected automatically. Foundry rows
   show the scene and parent Adventure; FG rows show map, module and grid status.
   Ctrl-click the maps you want, or use **Select all** / **Clear**. Choosing one FG
   map still brings across the module's supported campaign notes.
4. For an FG **NEEDS_GRID** row, select it and choose **Squares across** or
   **Pixels per square**. Supply a value you know; ForgeBridge does not guess.
   **Include artwork (FG ART)** reveals pictures normally excluded from map discovery.
5. Set **Map folder** and **Notes folder**, and double-click a map row or choose
   **Rename selected maps** to change its name. Existing library map names must
   be unique even across folders. The build summary shows the sanitized names used.
6. Click **Choose where to save output**. Pick a parent folder and check the new
   child folder shown under **Folder to create**; it must not already exist.
   Leave optional profiles alone for the normal workflow. Foundry PDF handouts
   become bounded note pages when the PDF checkbox is checked.
7. Click **Build / export**. Read the counts and losses before using the output.
   An FG build with no maps selected is notes-only; a Foundry build requires a
   scene selection. A refused map or missing image is not silently replaced.
8. To install, close Toolkit normally, then choose **Install reviewed native
   outputs**. Select actual MyAssets and a separate backup folder. Review the
   destination, added files and conflicts; confirm only a successful build. No
   Toolkit launch or installation happens just because you build.
9. Keep the backup and **uninstall.json** path from the result. Opening notes in
   Toolkit can change their files; `--keep-changed` preserves those edits later.

Wait for file work to finish before closing ForgeBridge. With a Python install,
`forgebridge-gui` or `python -m forgebridge gui` opens the same interface.

## Command-line conversion and output

### Fantasy Grounds walkthrough: one module → maps and notes

Find your `.mod` under `%APPDATA%\SmiteWorks\Fantasy Grounds\modules`.
AppData is hidden: paste that path into Explorer's address bar. Copy the module
somewhere convenient if desired; ForgeBridge reads it without modifying it.
Choose an **unencrypted** module. Protected Store/Forge/vault content is refused;
ForgeBridge cannot unlock it. A folder containing `definition.xml` and `db.xml`,
or an unencrypted vault-style ZIP containing one module, is also accepted.

For example, choose My Adventure.mod, click Discover scenes, select one READABLE
map, name both output folders My Adventure, and build into a new folder. That
**single build includes the selected maps and the module's supported notes**.
There is no need to combine separate map/note ZIPs yourself.

| Discovery status | What to do |
|---|---|
| READABLE | Stored image/grid can build. Select the map. |
| NEEDS_GRID | Enter known squares across or pixels per square before building. |
| ART | Normally a handout, not a calibrated map. Leave it as an image note; show artwork and supply a grid only if you intend a map. |
| BLOCKED | Read the reason; do not install a partial result. |

The stored FG grid always wins over an override. Unsupported layers, transforms,
terrain and environment settings remain report losses. Maps without a known grid
are not assigned a guessed scale. Your build includes available NPC/item/spell,
story, table, manual, parcel, quest and image notes even when a map does not use them.

Command-line equivalent (use the printed key for the map you selected):

```powershell
forgebridge convert "C:/Sources/My Adventure.mod" --list-scenes
forgebridge convert "C:/Sources/My Adventure.mod" --scene-key MAP_KEY --out "C:/Conversions/Adventure-01" --map-folder "My Adventure" --notes-folder "My Adventure"
```

For one selected map without a grid, add `--squares 40` or `--grid-size 100` only
when those values are correct for your map. With multiple maps, use repeated
`--squares KEY=N` / `--grid-size KEY=PX`. To convert only campaign notes:

```powershell
forgebridge convert "C:/Sources/My Adventure.mod" --notes-only --out "C:/Conversions/Adventure-notes-01"
```

The output's root **native-package.zip** is the coherent installable package;
`MyAssets/` contains its native files and `conversion-report.json` contains the
counts and losses. Use the same reviewed installer/uninstall receipt workflow
below. Missing external-module text/images stay losses; no replacement is invented.
A map pin opens its converted note. Tokens keep portraits and Size controls;
open the corresponding NPC note separately, because adding its link changes the
observed token appearance into a note pin.

### Foundry packages

Use a Foundry v13 package folder or ZIP. In the GUI, discover scenes and select
only the Adventure/maps you want; 5e and SA variants are listed separately.

The **optional Foundry Data folder** is the user-data folder containing `modules`,
`worlds` and `systems`, not the Foundry program folder or just an arbitrary image
folder. A common location is `%LOCALAPPDATA%\FoundryVTT\Data`; your server may
use another location. Use **Choose Foundry Data folder** if you have that matching
folder. This can supply art referenced outside the adventure package. It is read
only; missing/unsafe files still appear as losses. If you only have the adventure
ZIP, skip it. The new lookup is file-level tested, not seen in Toolkit.

The separate **optional dnd5e system/spells pack** supplies exact external spell
IDs. Use an unzipped compatible system folder or its `packs/spells`, not the Data
folder itself. Missing spells remain explicit links/losses without this input;
monsters/items from other system packs are not resolved yet. See the spell
walkthrough below for the tested free download.

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

## What campaign content comes across?

| Source content | Native result and limits |
|---|---|
| Scenes/maps | Background, supported barriers/doors/lights, map name/folder and available placements. Source grids/padding are normalized. |
| Journals, FG stories/manuals/handouts | Notes with readable text, converted local links and available image attachments; original interactive formatting is flattened. |
| dnd5e NPCs/characters | Display stat-block notes, available portrait, tracked HP and abilities/actions/reactions/legendary actions. Not combat/actor automation. Legacy FG stats are source display text, not a new supported game system. |
| Items/spells | Item/Spell notes from available source text/images; exact Foundry spell-compendium links need the optional spell pack. |
| Roll tables | Native range-table notes and available result links; formulas, weights and chained rolls need review. |
| FG parcels/quests | Reward/item/currency/status text as notes, without inventory/reward automation. |
| Playlists | Available local MP3/OGG song bytes and ordered playlist entries. Loop/fade/channel/volume/mode need manual review. |
| Static and animated tiles | Supported images, GIF/PNG/WebP animation frames and WEBM VP9/MP4 H.264 video with placement; unsupported codecs/limits become losses. |
| Ambient sounds | Supported Foundry OGG/MP3/PCM-WAV positioned on the map; radius/volume mapped, easing/walls approximate. |
| Tokens/map pins | Supported square portrait tokens and note-opening markers. Automatic token-to-NPC bindings are omitted to preserve portraits. |
| Foundry PDFs | Bounded page-image notes by default with renderer available; source-only references when selected or limits refuse rendering. |

For a selected Foundry Adventure, shared supported actors/items/tables/playlists
come across once, not only records reached from a selected map. Read
`campaign_content`, `native_losses`, `static_tiles`, `ambient_sounds` and
`visibility` in the report. Hashes prove input identity, not native behavior.
Labels remain off; scripts, active effects and source automation never execute.

## Supported / manual / unsupported

| Feature | Scope |
| --- | --- |
| Geometry/background | Direct native maps, barriers, doors, lights, background assets and browser previews from known schemas; no native files shipped. |
| Notes and tokens | Existing journal/table/image/marker/token writers; supported square/static tokens preserve identity, position, footprint, scale, rotation and hidden state. |
| Non-success | Invalid marker positions/targets, unsupported token geometry/scales, source/media gaps and unsupported light ranges remain explicit. |
| Light fidelity | Observed light defaults plus bounded Flicker/Blink/darkness flags; unsupported animation and scene darkness stay manual. New effects are file-level only. |
| Scene motion / audio | Synthesized Foundry scenes support captured WEBM VP9 / MP4 H.264 video, animated GIF/PNG/WebP frames, and OGG/MP3/PCM-WAV map sounds. Codec/size and timing limits apply; new output needs Toolkit validation. Procedural light animation remains separate. |
| Fog/vision | Native configuration and bounded character sight/effects are written at file level. Historical exploration masks, complete detection/permissions and runtime equivalence remain gaps. |
| Actors/behaviors | Supported stat-block notes are display content; full actor/combat behavior remains a gap. No script execution. |
| Labels | Off. Player behavior cannot be inferred from GM view. |

Advanced profile/capture/batch workflows remain in SCENE-PROFILES.md,
NATIVE-CAPTURE.md and SCENE-BATCH.md. Don't repin hashes just to clear errors.

## Install, back up and uninstall

Building creates files only. Installation is a separate reviewed action and
requires Toolkit to be **closed normally**; ForgeBridge will refuse while it is
running. Choose actual MyAssets, usually
`C:\Program Files (x86)\ArkenforgeData\MyAssets`, and a **separate backup folder**.
The installer backs up the entire existing MyAssets first, which needs disk
space. It adds absent files and reuses identical dependencies; different existing
bytes or duplicate library map names are conflicts, not overwrite requests.
Rename/rebuild or resolve the report deliberately; never Replace All.

After a successful GUI install, copy the displayed **uninstall.json** path to
your notes. Keep that file and its backup folder. CLI users can install an
already built combined package (the Windows app uses forgebridge-cli.exe):

```powershell
.\forgebridge-cli.exe install --package "C:\Conversions\Adventure-01\native-package.zip" --myassets "C:\Program Files (x86)\ArkenforgeData\MyAssets" --backup-root "D:\ForgeBridgeBackups"
```

To undo this install, close Toolkit again. Open PowerShell in the extracted app
folder, paste your **actual receipt path**, and run:

```powershell
.\forgebridge-cli.exe install --uninstall "D:\ForgeBridgeBackups\forgebridge-RUN_ID\uninstall.json" --keep-changed
```

`--keep-changed` removes the install's unchanged files and keeps edited ones,
listing them in the result. Opening a note in Toolkit can rewrite it, so a kept
note does not necessarily mean you edited its text. Kept files may remain visible;
review them later in a licensed Toolkit. No unrelated files or backups are removed.
Without this option, changed files cause a refusal. Do not delete edits to bypass it.
Only empty folders created by that install are tidied. Incomplete receipts need
manual review; never restore a whole backup over later work blindly.

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
2. The recorded check used **6.0.6**. For that tested setup, open its release
   and, under **Assets**, download
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

5. Check the report. Supported exact spell IDs become 5e Spell notes linked
   from their scroll or monster note. Any unresolved spell stays listed; do not
   assume a different system release contains the same IDs.

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

Build into a new output folder and review the loss report first. The guide and
release notes separate historical Toolkit observations from post-trial file checks.
See [native campaign details](NATIVE-CAMPAIGN-CONTENT.md) for implementation notes.

| Symptom | Action |
| --- | --- |
| Conflict/existing output | Select a new output; preserve/review user edits. Never overwrite to clear it. |
| Hash mismatch with advanced profile | Restore pinned inputs or deliberately recapture the correct profile; no blind repinning. |
| ICE/unstable player stream | Check output/projection settings in a licensed Toolkit. A recorded browser/session pattern is in the validation notes; it is not a proved converter defect or a universal browser fix. |
| Relaunch fails | Wait until the launcher no longer reports Toolkit running; no duplicate/elevated instances. |
| Black player view with fog text | Check native fog and framing on a disposable copy; fog-off and bounded reveal/persistence are distinct checks. Preserve original profile maps. |
| Windows LevelDB .dbtmp error | Retain diagnostics and stop that operation. Host intermittency remains unresolved despite clean CI; no blind retries, new probes or automatic Defender/indexer exclusions. If this happens to you, please open an issue. |
| Lock/backup failure | Inspect the active/interrupted install and retained receipt; don't remove unfamiliar locks or bypass the closed-Toolkit guard. |
| Size limit | Export/select fewer scenes. Backup: 16 GiB/100k entries; combined review: 1 GiB/16384 native files; conversion tree: 1 GiB/16384 files. |
| PDF renderer absent | Keep PDFs manual, or install optional PDF requirements. Skips are not renderer acceptance. |

The trial has ended; future native checks require Toolkit access. This guide adds no new runtime observations.

### Animated map tiles and ambient sounds: supported limits

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

### Fantasy Grounds display corrections (file-level)

FG prose carriage-return/newline escapes become real line breaks. Story, manual and other ordinary text fields share the Foundry journal writer's explicit white body text, pale links on dark fields and preserved paragraph breaks; parchment blocks retain dark links. Empty stat rows use captured active flags where present; remaining empty rows request zero-size, zero-width text. The trial has ended: these written-field checks do not confirm native layout or playback.
