# Native scene schema and comparison — 2026-11-01 (file level only)

Read installed MyAssets records read-only as explicitly requested. Added code
class/member/type/library definitions and inert default recipes for native
wall/door/light/image records, background asset pairs and fresh map containers.
No native file, image payload, source note, saved fog or bookmark is bundled.
Production factories read no installed Arkenforge files. Defaults preserve mutable
aliases and inherited member definitions; generated images are parameters.
The existing native_scene geometry calculations are unchanged.

Crypt reference comparison uses the same empty container and UVTT for cloned and
schema templates. Canonical comparison includes root-reachable class/member/type,
array data and aliases (arbitrary NRBF IDs normalized; stale unreachable records
are not scene objects). Result: **PASS — zero graph differences**, 199 walls,
23 doors, 66 lights, one background. The entire resulting byte streams also match:
SHA256 e48ffac5659570ca00eaea17f3dce156ff2593765a2e2d5a3e2efb4b501d61ec.
Reference Crypt map SHA256:
d08058217fd719936d6a84ce88bbb7a61f331cacd67b9a80759fd2823217f87e.
Private comparison script/report stay under .test-tmp; no reference map is copied.

Initial schema/serializer/native-map regressions: **28 run, 28 passed**, 1.481s.
Primitive arrays now use the existing primitive serializer when building fresh
records; the synthetic round-trip tests exercise this branch. Fresh defaults
contain no saved fog/bookmarks or user creator identity. Their Toolkit acceptance
remains Claude's task; this is not runtime evidence and no M1 row is changed.

## Synthetic integration and thumbnail (steps 2–3)

Added a synthetic container and four template records written by the test
FixtureWriter. synthesize_map now runs end-to-end in CI without MyAssets or
reference files; its decoded result matches the schema-factory output. Generated
PNG backgrounds exercise background_asset fully, including 128-pixel asset
previews. map_metadata accepts background bytes and emits a 256-pixel PNG map
preview preserving aspect ratio. Tests decode thumbnail pixels/dimensions and
verify no Pillow global pixel-limit change. Backgrounds enforce their own 64 MP
bound. No geometry formula changed.

Synthetic/schema suite: **9 run, 9 passed**, 0.333s. Map-browser display itself
is not observed here; Claude owns Toolkit checks. Existing two-scene native
runtime evidence is in Claude's DIRECT-MAP note and is not edited by this work.

## Default native conversion and installer/GUI integration (steps 4–5)

Default convert now synthesizes geometry at 2.56 units/grid and origin (0,0), adds
schema-built background assets and the map preview, then calls the existing
native note/room-marker/media/token writers. Controls are code-built too; token
control uses the observed spriteWidth -1 sentinel and a generated 500px icon,
normalizing observed Size2/scale1.024 to Size1/scale.512. No existing map is needed.
Generated helper maps/controls are removed after rebuilding their generated token
notes to eliminate stale unreachable references; final dependency closure is
checked. Geometry formulas in native_scene are unchanged.

The command publishes per-scene native/UVTT packages, a combined MyAssets tree
and one stage-specific loss report. Source/UVTT grades are preserved separately
from native counts/losses. Missing marker positions/targets, unsupported tokens,
media, light ranges and environment/fog/behavior gaps stay explicit. Zero-token
and journal-free scenes work. Flat ZIPs resolve qualified module asset paths by
the local manifest ID, never by looking outside the package.

Explicit --install requires MyAssets and a separate backup root and uses the
existing add-only installer. The GUI uses the same native-output selector and
installer; no profiles are required by default. Both were tested only on fake
MyAssets, not the real installation. Review/receipt limits now align with the
conversion tree (1 GiB/16384 native files; up to 256 scene packages); full backups
remain capped at 16 GiB/100k entries. No automatic elevation or security change.

Local tests: full development run **226 run, 222 passed, four Windows symlink
skips**, 132.388s. Final direct/record/convert/GUI/installer/review selection recorded
in .test-tmp/direct-final-targeted.txt; final CI must be checked at the pushed head.

Real file-only command:
`python -m forgebridge convert lob-counts_manor-pk-v13 --scene fP7VKkP46gQPED6X --out .test-tmp/schema-direct-crypt-2026-11-01`
PASS, with both 5e and SA Adventure variants selected by that shared scene ID.
Each: 199 walls, 23 doors, 66 lights, 19 markers, 84 notes, 55 image attachments,
9 supported tokens and 1 rejection. Combined: 608 native files, 666 closed metadata
references, 18 tokens/2 rejections, 168 notes, 38 markers. Each ZIP has exactly one
final map; no generated helper maps/controls published. Paths/Adventure scopes
remain distinct. See direct-crypt-file-results.json for both package hashes.
Neither output was installed or observed in Toolkit; Claude owns those checks.
A-step notes and M1 rows remain unchanged. No new LevelDB investigation/retries.
