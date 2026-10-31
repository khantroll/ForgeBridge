# Portable native capture

Export ZIPs are the default. Capture the selected map and its reachable metadata,
notes, media and map backlinks without rewriting their original bytes:

```powershell
$env:PYTHONPATH = "$PWD\src"
py -m forgebridge.native_capture --export control.zip --map "MyAssets/Maps/Control.rwmap" --out captured-control
py -m forgebridge.native_capture --profile manor.profile.json --out portable-manor
py -m forgebridge.package --profile portable-manor/scene-profile.json --preflight
```

Repeat `--export` for additional dependency exports. Multiple maps require explicit
selection. Missing references, conflicting bytes, unsafe/case-aliased paths and
existing output directories fail rather than replacing anything. ZIP output has
deterministic member timestamps; the manifest records input and member hashes,
dependency edges, primary map and the declared control/scene-geometry role.
NRBF parsing is inert; imported scripts are never executed.

## Read-only audit before capture

Check exports before choosing where to capture them. The audit writes nothing,
reuses the same limits and path/conflict/reference checks, and lists every
finding instead of stopping at the first:

```powershell
py -m forgebridge.native_capture --audit --export control.zip --export deps.zip --map "MyAssets/Maps/Control.rwmap" --out planned-capture
```

The JSON report gives input hashes, all maps found, the selected closure (paths,
hashes, which input supplied each file, dependency edges), files that capture
would leave out, and findings by `check`: `unreadable-export`, `case-conflict`,
`conflicting-bytes`, `limits`, `map-selection`, `selected-map-missing`,
`unsafe-path`, `unsupported-reference`, `missing-dependency`,
`destination-exists`, `destination-name`. With several maps and no `--map`, each
candidate map gets a completeness summary. `--out` is optional and only checked
for availability. Exit code 0 means capture would accept these inputs; 1 means
findings; 2 means a usage error. Saved-map (`--asset-root`) audits are not yet
supported; export the map first or capture directly with `--toolkit-closed`.

Path and conflict checks are shared with production package assembly. Repeated
exact paths with identical bytes deduplicate; differing bytes or case aliases
(even with identical bytes) fail with the conflicting paths. A failed dependency
merge leaves the original file dictionary unchanged. Reserved Windows names,
trailing dots/spaces and ZIP symlinks are rejected by the shared export loader.
The final package reference audit also checks path aliases, including builds
without tokens. Inert reports outside MyAssets remain supported in combined packages.

Native paths in the reachable graph must use the supported `.rwmap`, `.rwmeta`,
`.rwnote` or `.rwfile` formats. An unfamiliar native path now stops capture with
its originating file and exact reference instead of silently omitting it. Supply
a supported native export or extend the parser after inspecting the new schema;
capture does not guess how unknown assets should be migrated.

`--profile` validates the existing pinned profile, copies every original input
(including source package and original control ZIPs), rebases paths and validates
again. Move the entire output folder together. Its `scene-profile.json` consumes
the byte-preserved inputs; `capture/native.zip` is an additional dependency-closed
geometry snapshot. Reusable controls stay separate, including when they have
different bytes at identical paths. Calibration, identity and hashes are retained;
capture never infers origin, scale or runtime success. Source packages may be large
and remain subject to the existing profile fingerprint limits.

For explicitly selected saved assets only:

```powershell
py -m forgebridge.native_capture --asset-root "D:/Arkenforge/MyAssets" --map "MyAssets/Maps/Control.rwmap" --toolkit-closed --out saved-control
```

Install the declared optional dependency with
`py -m pip install -r requirements-native-capture.txt` when using saved-asset mode.
ZIP/profile capture needs no additional dependency and never installs one itself.
Close Toolkit normally first. The Windows-only snapshot path checks process absence
before and after reading and rereads every captured file to detect changes. It fails
if process verification is unavailable. Do not modify assets with other tools during
capture. Export ZIPs avoid these live-directory consistency constraints. Capture
never installs content or edits the installation/campaigns.

Manual steps remain native import/export/calibration, reviewed installation, GIF
setup and bounded fog control. Labels stay off. Foundry vision/fog, procedural light
animation and actor/stat behavior remain explicit gaps. Crypt actual-player
visibility and profile player restart checks remain pending independently of this
file-level workflow.
