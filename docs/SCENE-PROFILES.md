# Calibrated scene profiles (version 1)

A profile binds one Foundry scene to one measured native geometry export. Native
marker, image-note and sized-token controls are reusable schemas; they do not
supply the generated scene's geometry, origin or scale. Profile builds still use
source adapters → IR → target adapters. Labels stay off.

```powershell
$env:PYTHONPATH = "$PWD\src"
py -m forgebridge.package --profile profiles/manor.json --preflight
py -m forgebridge.package --profile profiles/manor.json --out builds/manor-v1.zip
```

Preflight reads inputs, verifies hashes and exact source identity, probes native
controls in memory, checks metadata dependencies and reports token rejections and
source-media gaps. It writes no package, profile, source files or installed content
and changes no settings. Existing LevelDB readers use temporary copies for safe
inspection. PDF rasterization and final generated media validation occur during
the build; preflight does not establish PDF readability or runtime behavior.

## Authoring and pinning

First import the scene's current UVTT into an isolated native map. Save/export it
and measure native origin and units per **source** grid square. Record the matching
package/scene and measurement evidence in a draft. Do not copy another scene's
calibration. Export a reusable native marker, image-note and (when needed) token
control with its native Size field and dependencies. Version 1 requires an
unpacked original package directory for exact source and texture checks.

This is the complete draft shape; empty hashes are allowed only during explicit
capture. Paths are relative to the JSON file, including paths containing `..`.
No paths are resolved relative to the working directory. Absolute paths also work.

```json
{
  "format": "forgebridge.scene-profile",
  "version": 1,
  "source": {
    "package_id": "your-module", "scene_id": "scene-id",
    "package": {"path": "../source/your-module", "sha256": ""},
    "companion": {"path": "scene.forgebridge.json", "sha256": ""},
    "scene_sha256": ""
  },
  "geometry": {
    "export": {"path": "scene-native.zip", "sha256": ""},
    "map_path": "MyAssets/Maps/This scene.rwmap",
    "calibration": {
      "package_id": "your-module", "scene_id": "scene-id",
      "scene_sha256": "", "geometry_sha256": "",
      "map_path": "MyAssets/Maps/This scene.rwmap",
      "origin": [0, 0], "units_per_grid": 2.56,
      "evidence": "Replace with this scene's measured native coordinates and export record"
    }
  },
  "controls": {
    "marker": {"input": {"path": "../controls/marker.zip", "sha256": ""}, "name": "FB Cal A"},
    "media": {"input": {"path": "../controls/image-note.zip", "sha256": ""}},
    "token": {"input": {"path": "../controls/token.zip", "sha256": ""}, "name": "Control token", "units_per_size_square": 2.56}
  },
  "output": {"map_name": "Separate scene map", "note_namespace": "Separate scene notes"},
  "options": {"pdf_pages": false}
}
```

For ambiguous embedded Adventure IDs, add the same explicit `selector` object to
both `source` and `geometry.calibration`:
`{"source_path":"packs/adventure-5e","parent_adventure_id":"parent-id"}`.
Standalone scenes can omit it. `controls.token` may be `null` only for scenes with
no source tokens. Calibration numbers above are examples, not defaults.

Pin this explicit binding with
`py -m forgebridge.scene_profile --capture profiles/draft.json --out profiles/scene.json`.
Capture verifies source scene identity, pins SHA256s and rebases relative paths
when the destination directory differs. It refuses an existing profile output.
It never measures or infers calibration and never grants runtime PASS status.
Changing the selected Adventure also requires an explicitly matching calibration
selector. The strict parser rejects unknown keys, duplicate JSON keys, unsupported
versions, missing identities and nonfinite calibration.

## Locks, overrides and isolation

Files use SHA256 of bytes. A source directory uses SHA256 of a canonical sorted
list of relative file paths and file SHA256s, rejecting links/escapes; 50,000 entries,
1 GiB per tree and 256 MiB per file are the limits. Companion scene data must also
match the exact original pack/Adventure payload. A hash change stops the build
with its input role, expected/actual hash and recovery instructions. Restore the
pinned input, or regenerate the companion, recheck that scene's calibration and
explicitly capture a new profile. Do not merely replace hashes to bypass a warning.
The directory hash is deliberately conservative: changes to unreferenced files
also require review. Hashes prove input consistency, not native behavior or that a
human's calibration declaration is correct.

With `--profile`, only `--out`, `--name`, `--note-folder`, `--pdf-pages` and
`--no-pdf-pages` may override the profile. Input/template/calibration flags and
`--regenerate-notes` are rejected. Explicit legacy CLI usage keeps its prior
behavior. Output ZIP names are never stored in a profile or overwritten; keep
outputs outside the pinned source directory.

Generated notes, token notes/images and converted attachments use a stable scope
derived from package ID, scene ID, optional Adventure selector, output map name
and note namespace. A readable note namespace receives a scope suffix, so even
identical requested note namespaces in different scenes remain isolated. Repeated
textures still have separate token identities. Different output maps must have
different names. Profiles preserve original map objects and native backlinks;
control exports can carry their original map as an explicit dependency, never as
the generated scene's geometry. Shared preserved controls must be byte-identical
to coexist. Conflicts fail rather than overwrite user content. Installation remains
a separate reviewed operation; rebuilding writes a new ZIP and cannot alter an
installed campaign or another package. `profile-provenance.json` and the conversion
report record the effective scope, pinned inputs and calibration, separately from
runtime evidence. Profile builds are repeatable at the native payload/reference
level; ZIP timestamps are not promised to be byte-identical.

## Manual steps and conversion gaps

Native UVTT import, export and coordinate calibration remain manual. Back up
MyAssets, inspect installation conflicts and copy only absent/identical files.
Ungroup imported geometry when editing individual objects. GIF import and FPS
setup remain manual. Bounded fog stays deferred to the documented human rectangle
erase/paint gesture, followed by actual player and persistence checks. Builds and
preflight perform none of these operations and never install content or change
system settings. Foundry vision/fog, procedural light animation, actors/statistics
and combat behavior remain retained/unmapped. Source table/media gaps are reported
without invented replacements. See the validation log for current automated and
runtime scopes; input fingerprints are not runtime validation.


## Real-scene demonstration

`validation/2026-10-16/prepare_real_profiles.py` snapshots the already calibrated
Manor and Crypt native exports and captures separate profiles. The pinned
`profile-runtime-private/{manor,crypt}.scene-profile.json` files record the exact
inputs used; source media and native ZIP exports remain local assets. Missing or
changed inputs must be supplied/recalibrated, not replaced with guessed exports.
Run the package CLI with either profile and a new output path. The separate
`audit_profile_packages.py` compares both outputs, closes dependencies and reviews
installation conflicts read-only by default. Its explicit `--install` is a local
validation operation, never part of a production build/preflight.

The pair's file audit passes (Manor one token, Crypt nine and one explicit
rejection). Representative runtime token/link switching and restart checks pass on October18.
Actual player visibility/restart samples passed October 31; see
[runtime evidence](../validation/2026-10-31-PROFILE-PLAYER.md). Fog was disabled
for those observations; bounded fog is still deferred. The validation log separates
runtime observations from file-only provenance and earlier player evidence.
