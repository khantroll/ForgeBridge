# Build a batch of calibrated scenes

`forgebridge.scene_batch` accepts **2–32 existing version-1 scene profiles**.
It reuses the single-scene hash/identity/calibration preflight and package builder.
It does not infer calibration, install content, or edit campaigns.

```powershell
$env:PYTHONPATH = "$PWD\src"
py -m forgebridge.scene_batch --profile profiles/manor.json --profile profiles/crypt.json --preflight
py -m forgebridge.scene_batch --profile profiles/manor.json --profile profiles/crypt.json --out builds/two-scenes-v1
```

The output parent (`builds` here) must already exist; the batch folder must not.
There are no overrides: edit/review/pin the appropriate profile to change its
identity, inputs, output names or scene-specific calibration.

Preflight writes JSON to stdout and performs no package build, PDF rendering or
output writes. It checks every profile even when one is invalid; exit 1 means the
batch is rejected. It reports case-insensitive output-map/namespace collisions,
duplicate effective scopes, shared native dependencies and conflicting bytes or
case aliases. Preserved source geometry/backlink maps are included; reusable
schema-only marker/media controls are not misidentified as scene geometry.
Repeated source token and note/document IDs are listed with their scene owners:
they are permitted across distinct scopes, not silently merged. Each scene's
unsupported tokens, missing media, note/link gaps and original graded source loss
report are retained in one `loss_report` array. Missing source loss reports are
explicit, never invented. Labels stay off.

A build first preflights the whole batch, then builds each package in temporary
staging using the production builder. Actual native output bytes are checked for
cross-package conflicts and dependency closure before publication. Input/profile
hashes are rechecked; changed inputs fail without repinning or retrying. This final
check also covers generated media/dependencies that read-only preflight does not
render. Preflight is not a guarantee that a later build or PDF renderer will succeed.

Successful output:

```text
two-scenes-v1/
  scene-01/scene.zip
  scene-02/scene.zip
  batch-report.json
```

Packages keep their profile-defined map names, separate token/media/note scopes,
calibration and provenance. Shared byte-identical native dependencies can coexist;
different bytes at the same native path block the batch. Each ZIP remains a
complete independent scene package. The combined report retains per-scene
conversion reports, package hashes and total closed metadata references.

Existing output folders (even empty ones), links/junctions and output inside an
input directory are refused. Staging failures publish nothing. Publication uses
exclusive creation and never overwrites files; an IO failure during publication
may leave an incomplete new folder. Treat a missing `batch-report.json` as
incomplete, preserve it for inspection, and choose a fresh destination after
resolving the failure. Builds never repair or delete an existing output folder.

Review packages and [installation guidance](SCENE-IMPORT-RELEASE.md) before any
manual installation. No runtime acceptance is inferred. Native UVTT
import/export/calibration, reviewed installation, GIF/FPS setup and bounded fog
remain manual. Bounded fog waits for Claude's built-in-browser validation.
Foundry fog/vision, actor/stat/behavior and procedural light animation mapping
remain explicit gaps. This command does not create cross-scene navigation or
convert an entire Adventure automatically.
