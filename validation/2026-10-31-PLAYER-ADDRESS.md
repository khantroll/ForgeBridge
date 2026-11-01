# Player address comparison — 2026-10-31

Toolkit 0.5.1.18; launcher 7.0.0.3. Disposable map only:
ForgeBridge Fog Test 2026-10-31. Application cap retained at 30 FPS.
Sequential Computer Use captures; no builds/tests/rendering during this comparison.

| Attempt | Browser/address | Stream | Observation |
| --- | --- | --- | --- |
| A, before loopback comparison | Waterfox, http://192.168.1.201/ | 1280×720, 15 FPS | Start Streaming clicked; black picture; native ICE exception below. |
| B | Chrome, http://192.168.1.201/ | 1280×720, 15 FPS | Page title loaded; Computer Use URL-confidence policy stopped control before Play. Playback/error outcome unknown. |
| C, about 19:08–19:09 CDT | Waterfox, http://127.0.0.1/ | 1280×720, 15 FPS visually verified before Activate | Start Streaming clicked. Actual frame contained “Fog of war is active!” and Live Play/VTT fog-menu guidance. Returning to Toolkit showed the same native ICE exception. |

Before C, Settings → Display → Active extended screens → Stop projecting was
used. “Local streaming stopped” was observed and the active entry disappeared.
A fresh Player Screen projection was then configured and activated. The old Chrome
player page remained open but was not started by this operator. An older Waterfox
player tab was listed among existing user tabs; its session state was not inspected.
This limits claims about a single-client controlled comparison. Only the newly
created loopback tab was closed afterward; unrelated tabs were preserved.

Both A and C showed this native diagnostic (transcribed from UI):

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

**FAIL:** loopback alone did not prevent the native ICE exception. Address-specific
causation remains unconfirmed; do not attribute this to ForgeBridge conversion.
**PASS (limited):** Waterfox loaded the loopback player page and received a frame
with Toolkit's fog overlay. This does not establish room framing or fog reveal.
**BLOCKED:** bounded reveal/cover/reveal and saved-reveal restart acceptance.
Earlier accepted profile/Multi Scene player observations remain separate.

Toolkit reported unstable state and disabled autosaving. The native Close Toolkit
option was used; subsequent enumeration confirmed it exited. No map changes were
saved, edit counter remained 0/0, and original profile maps were not opened.
No further recovery loop, privilege/security changes, or converter edits made.

CPU sample before C is in 2026-10-31-loopback-before.json: Toolkit 12.08/13.47%,
browsers 2.65/3.34%, capture helper 0/0%, identified compute candidates 0/0%.
These two samples precede activation and do not establish load at the error.
No capture timeout occurred during this loopback attempt. UI captures are retained
in the conversation tool evidence; no standalone screenshot files were created.
