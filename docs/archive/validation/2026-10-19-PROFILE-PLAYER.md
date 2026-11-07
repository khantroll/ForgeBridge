# Profile player follow-up — 2026-10-19

## Runtime outcome

BLOCKED: Crypt generated-token actual-player visibility and both profile player
restart checks. No new token/player PASS. Accepted Manor generated Stoker initial
visible → hidden → restored-visible and both profiles' GM persistence remain
accepted. Outside manual `Stoker_token_1` was not substituted for generated Stoker.
Bounded fog remains separately DEFERRED; labels remain off.

Toolkit 0.5.1.18 / launcher 7.0.0.3. Initial fresh enumeration returned running
Toolkit window 9111242, launcher, Waterfox player screen and Task Manager. Host
CPU samples before UI: Toolkit 20.40/20.84%, browser 1.01/1.02%, helper 0%, no
named compute candidates. No tests/builds/PDF/compression ran during desktop work.
Captures/input were sequential and responsive throughout the active session.

Existing Profile Crypt was open. GM zoom changed 95→20%; generated **Cursed
Cannibal** was specifically selected and identified in the native current-selection
pane, without changing visibility. Attempts to drag the player-view box selected
the underlying map group instead; selection was cleared with Escape. Native edit
counter remained 0/0. No object transforms, token states, notes or saved maps changed.
Map Projection hotkeys were inspected, not assigned. Native widget tooltip
identified **match player view to DM view**; it was used once. Native camera
bindings D and S+D moved only the GM camera. No bounded-fog gestures occurred.

The stream creation dialog reset to 1920×1080/30 when opened again. Before
activation it was explicitly changed to **1280×720/15**, with both values observed.
The 30-FPS application cap from cf46fe7 was not edited. The single existing
Waterfox player tab displayed its play button; clicking Play produced black output.
The room itself was not established as visible, so no token hidden-state experiment
was started. No physical player display was tested.

On returning to Toolkit, its own modal reported **“The Arkenforge Toolkit is now
in an unstable state”**, warned autosave was disabled, and recommended restarting.
“Give me the details” showed:

```text
ArgumentException: create candidate is failed. error type:InvalidParameter, candidate:
sdpMid:0
sdpMLineIndex:0
Unity.WebRTC.RTCIceCandidate..ctor
Unity.RenderStreaming.SignalingManagerInternal.OnIceCandidate
Unity.RenderStreaming.Signaling.WebSocketSignaling+<>c__DisplayClass39_3.<WSProcessMessage>b__4
UnityEngine.UnitySynchronizationContext+WorkRequest.Invoke
UnityEngine.UnitySynchronizationContext.Exec
UnityEngine.UnitySynchronizationContext.ExecuteTasks
```

This is a native stream/session failure; no evidence establishes a ForgeBridge
conversion defect or a CPU cause for this exception. The preceding black frame
does not isolate camera/fog from failed streaming. Toolkit itself reported automatic
log upload; no support report was manually sent externally by the agent.

Clicked the modal's **Close the Arkenforge Toolkit**. The next capture against
the exiting window reported `foreground window did not report a process id`.
Fresh enumeration succeeded and no longer contained Toolkit, confirming shutdown;
this is not evidence of a Toolkit-only capture failure while it was running.
No stale-view input followed. CPU after shutdown: Toolkit absent, browser
13.36–13.63%, helper 7.39–8.25%; these are not measurements at exception onset.

One normal restart used the existing launcher, no elevation. Fresh window 330596
was discovered and captured successfully at **New Map**, projection inactive.
This recovery restart is not a profile player persistence PASS. Native streaming
was stopped by shutdown and was not restarted before compute. Original profile
token source states remain untouched and no profile save occurred in this attempt.

Read-only local log inspection independently confirms the empty-candidate error
in `Player-prev.log` lines 3433–3441, preceded by “this candidate can't accept on
state.” A private copy stays in `.test-tmp/profile-WebRTC-Player-prev.log`, SHA256
`a7b34e2701dd42c80bc3036171c07deaf364a0cf84f77bb79d24d9236814f4ae`.
Full local log is excluded from Git. The screenshots are in this conversation's
tool evidence; no screenshot file is claimed. Raw CPU samples accompany this log.

## Independent work

PASS: controlled unfamiliar-reference regression reproduced a capture omission:
`MyAssets/Media/unsupported.png` could be silently ignored. Shared reference
inspection now refuses unsupported native paths with origin/reference and an
actionable parser/export instruction, in both ZIP and saved-snapshot capture.
Unsafe paths still fail safety validation first. Tests confirm no output publication
and original export preservation. No conversion math or LevelDB retry changed.

PASS (file level): recaptured existing Manor/Crypt portable native ZIPs, explicitly
selecting their recorded primary maps. Bundle hashes remain respectively
`e60479e9424ced7d7c42fe5fd060bd6f35683cafa3864f52f76c80e31764c814`
and `5323d2eeae51b6eeb566000188f0a754549125cc90be4d4d3c0add1abc3c59`.
The first Crypt command correctly refused ambiguous auto-selection (two reachable
maps); a subsequent command refused overwriting an existing Manor output. Fresh
destinations and explicit primary maps passed. No scene package installed/rebuilt.

PASS: five native-capture tests, 2.195s. Subsequent full run: **149 run, 143 passed,
four skipped, two errors**, 34.484s. Errors were existing intermittent LevelDB
scene-inventory absence in notes dependency and UVTT tests. This supersedes a
claim that the new full run is clean; cf46fe7's clean 148-test run remains historical.
Five controlled fixture inventory reads all found scene-vault; retained diagnostics
showed expected hostile/missing-source fixture warnings, no open error.
An additional diagnostic full run records LevelDB warnings next to failures,
without changing production behavior or adding retries; result recorded below.

FAIL (diagnostic full run): **149 run, 143 passed, four skipped, two errors**,
33.036s. This time retained diagnostics identify Windows LevelDB temporary-file
replacement failures, not just missing inventory scenes:

```text
plyvel_next._plyvel.IOError: IO error: .../packs/journal/000002.dbtmp:
Unable to remove the file to be replaced.
Reader diagnostics: leveldb-not-decoded: .../db/000006.dbtmp:
Unable to remove the file to be replaced.
```

The first occurred while a test created a new database, before ForgeBridge snapshot
reading; the second occurred opening a copied scene snapshot. Thus the retained
failure is not exclusive to snapshot copying. Exact root cause (binding/filesystem/
external file access) is unresolved. No blind retries, error suppression, lock
removal, permission/security changes or production LevelDB modifications were made.
Full diagnostic output remains local at
`.test-tmp/native-reference-diagnostic-full-tests.txt`; the initial full run at
`.test-tmp/native-reference-full-tests.txt`. No further full-suite repeat was run.

Next independent implementation task: use retained LevelDB-open diagnostics to
establish a reproducible cause before changing snapshot behavior. Native reference
schema coverage can continue independently of player output. The next desktop task
is a fresh browser streaming session that can display a lit Crypt room without
the ICE-candidate exception, followed by token visibility and both-profile restart
checks. Do not request repeated human framing or alter converter code to repair
the native stream. Native import/export/calibration, reviewed installation and GIF
setup remain manual; Foundry vision/fog, procedural animation and actor/stat behavior
remain explicit gaps.
