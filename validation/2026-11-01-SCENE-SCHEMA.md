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
SHA256 e48ffac5659570ca00eaea17f3dce156ff2593765a2e2efb4b501d61ec.
Reference Crypt map SHA256:
d08058217fd719936d6a84ce88bbb7a61f331cacd67b9a80759fd2823217f87e.
Private comparison script/report stay under .test-tmp; no reference map is copied.

Initial schema/serializer/native-map regressions: **28 run, 28 passed**, 1.481s.
Primitive arrays now use the existing primitive serializer when building fresh
records; the synthetic round-trip tests exercise this branch. Fresh defaults
contain no saved fog/bookmarks or user creator identity. Their Toolkit acceptance
remains Claude's task; this is not runtime evidence and no M1 row is changed.
