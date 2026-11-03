# Toolkit-made user playlist (captured 2026-11-03, Toolkit 0.5.1.18)

Created with Audio → Playlists → New playlist ("FBCapture Playlist", no songs).
The Toolkit lists this playlist; it does NOT list ForgeBridge's own
`22eea67e32f99a22da82.rwpl` (*Ambient*) or `FB MP3 Test.rwpl` in the same place,
and the Content Library song search does not find ForgeBridge's song files.

Differences found against ForgeBridge's playlist (decoded):
- `.rwmeta`: the Toolkit writes an extra `_prevPathIfDeleted = None` member
  (also `ArkenBaseMeta+_prevPathIfDeleted`); ForgeBridge copied the older shipped
  pack layout, which lacks it. Shipped Packs load without it; user MyAssets content
  evidently does not.
- `_creator` is '' for user content (ForgeBridge wrote 'ForgeBridge'; notes/maps with
  creator ForgeBridge do load, so this is probably not the cause).
- Campaign playlist file name `22eea67e…` differs from its `_name` 'Ambient'.
