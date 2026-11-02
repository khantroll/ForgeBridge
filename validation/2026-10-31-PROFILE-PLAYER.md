# Profile player visibility and restart — 2026-10-31

## Runtime outcome

PASS: Crypt generated-token actual-player visibility (visible → hidden → restored).
PASS: Crypt profile player restart check.
PASS: Manor profile player restart check (generated Stoker visible to players).
Bounded fog remains DEFERRED; labels remain off. No profile map was saved.

Toolkit 0.5.1.18 / launcher 7.0.0.3. Toolkit launched normally (not elevated).
Desktop control in this run was Claude computer use (Claude desktop app bridge),
not the Codex helper. Player output was observed in the Claude desktop app's
built-in browser at `http://127.0.0.1/` (the Toolkit-reported stream address
`http://192.168.1.201/` did not load in that browser; loopback did).

## Root cause of the 10-24 capture blocker (resolved, not a converter issue)

Before the user rebooted the host, every capture showed a full-screen masked
"unidentified" window covering everything except a ~30 px strip at the bottom of
the display (the taskbar area). Clicks still reached the Toolkit through it.
After a Windows restart the mask was gone and capture/input worked throughout.
Consistent with a stale full-screen overlay left by the earlier desktop helper
(running since 10-18, failing startup on 10-24); exact owning process was not
identified. No settings, privileges or applications were changed to recover.

## Crypt — ForgeBridge Profile Crypt 2026-10-16

- Opened from Map Browser; last modified `10/18/2026 11:45:20 AM`.
- Stream: Settings → Display → Add extended screen → Local network streaming →
  Player Screen. Dialog defaulted to 1920×1080 / 30; set to **1280×720 / 15**
  before Activate. Toolkit 30-FPS cap not edited.
- Play connected on first attempt; no WebRTC/ICE exception, no "unstable state"
  modal across two stream sessions.
- Initial player output was black with the native overlay text
  "Fog of war is active!" — the saved map has manual fog enabled with no
  revealed area. This likely explains the 10-19 "black output" observation
  independently of the WebRTC failure that followed it.
- Fog of war was disabled **for the session only** (Live Play/VTT → Fog of War →
  Disable fog of war) and the player view box moved over the west rooms.
- Generated **Cursed Cannibal** (west small room) identified in the
  current-selection pane.
  - Player view: token visible.
  - Toggle hidden → player view: token absent; GM shows hidden marker.
  - Toggle hidden again → player view: token visible in the same position.
- Native edit counter read 1/0 before the hide test (after an initial selection
  click; undo did not change it), 3/0 after hide/restore.
- Stream stopped via **Stop projecting**. Quit → "unsaved changes" prompt →
  **No**. Saved file not modified.

## Restart

- Normal relaunch via launcher → Launch Arkenforge Toolkit.
- Crypt reopened: last modified still `10/18/2026 11:45:20 AM`; edit counter 0/0;
  fog enabled again (saved state).
- Both generated Cursed Cannibal tokens present in their original rooms, not
  hidden. The pre-existing hidden token in the large room remains hidden.
- New stream (1280×720 / 15 again — dialog reset to defaults), fog disabled for
  session, view box moved: player view shows **both Cursed Cannibal tokens**;
  hidden large-room token correctly not shown to players.

## Manor — ForgeBridge Profile Manor 2026-10-16 (same restarted Toolkit session)

- Opened without a save prompt for Crypt (no pending changes).
- Last modified `10/18/2026 3:54:55 PM`; edit counter 0/0.
- Generated **Stoker** identified in the lower hall; player view shows Stoker in
  the same position. Hide/restore not repeated (accepted 10-18).
- Stream stopped; Toolkit exited with no save prompt.

## Not changed

No token, note, geometry, fog or visibility state saved. No packages rebuilt or
installed. No converter code changed. Settings: stream resolution/framerate set
per session (dialog does not persist them).

## Remaining

- Bounded fog gesture/persistence: DEFERRED (fog was disabled for these checks,
  so this run does not establish fog behavior).
- Intermittent Windows LevelDB `.dbtmp` replacement error: unresolved.
- Native UVTT import/export/calibration, reviewed installation, GIF setup: manual.
- Foundry vision/fog, procedural animation, actor/stat behavior: explicit gaps.
