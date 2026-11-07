# Desktop validation under constrained CPU

Keep compute work and Toolkit UI validation in separate phases. Tests, builds,
PDF rendering, compression and dependency scans must finish before capture starts.
The CPU sampler below reads counters only; it does not control applications.

```powershell
pwsh -NoProfile -File docs/archive/validation/measure-desktop-load.ps1 -Phase before -OutputFile docs/archive/validation/NEW-before.json
```

Run the sampler from a host shell that can see Toolkit. A sandbox may expose only
its own processes; a report without Toolkit cannot establish desktop CPU load.
Record original native settings before editing them. Through supported Toolkit UI,
set an application cap of30 FPS and player streaming to720p/15 FPS **if those
controls exist**. Record unsupported/unavailable controls explicitly. Never guess
PlayerPrefs keys, edit native binaries, change global power/security settings or
process priority to recover capture. Preserve lighting/fog/output settings needed
for the behavior under test; camera width is not stream resolution or frame rate.

Keep one player-stream browser tab active. Stop native streaming for GM-only
checks; leave unrelated tabs/processes alone. If a second browser contains a player
page, stop/close only that identified stream tab through supported browser controls.
Do not infer the number of tabs from the number of browser processes.

After an application settings change, let Toolkit settle and finish a separate
`-Phase after` sampler run before UI work resumes. Capture sequentially with one
outstanding request. Observe, inspect, perform one action, settle, then refresh.
Do not poll screenshots rapidly or send input from an occluded/wrong/stale view.

For each controlled comparison record:

| Phase | Original/change | CPU samples | Enumeration | Screenshot captures | Timeouts |
|---|---|---|---|---|---|
| Before | exact app/stream settings or unknown | Toolkit/browser/helper/compute categories | completed/attempted and latency | completed/attempted and latency | exact operation/error |
| After | one supported load reduction at a time | same sampler/settings | same bounded observation sequence | same target/window state | count and denominator |

Do not combine initialization timeouts, enumeration timeouts and screenshot
timeouts into one capture rate. Failed initialization means no screenshot was
attempted. A handful of successful captures supports a useful workaround, not a
confirmed cause. Mark unavailable after measurements BLOCKED instead of inventing
an improvement. No screenshot based on saved package data is a runtime PASS.

After a timeout, stop input and allow the request to finish. Pause UI work and
sample with `-Phase timeout-recovery`; do not overlap sampling with a capture.
Follow the installed Computer Use skill's bounded recovery: fresh selection for
capture failure, or its lightweight retry/session reset sequence for helper failure.
No capture storm, alternate automation bypass, automatic process termination or
priority change. If saturation/control failure persists, checkpoint exact live
token/settings state, retain desktop checks as pending and do independent
implementation work. Do not restart validation setup or repeatedly request human
intervention for the same unchanged condition.

Resuming after recovery requires fresh enumeration and capture. Verify token
identity before visibility changes; an eye badge itself reveals a hidden token.
Restore source states, save only the intended validation maps and distinguish
saved-file audit evidence from observed player output. Keep labels off.

October 31 window-switch recovery: the documented Windows CUA bound-input API
activates its selected window, while capture alone did not bring Toolkit forward.
After the user explicitly requested switching windows, binding the fresh Toolkit
ID and pressing only Shift brought Toolkit forward; the following screenshot
showed Toolkit and edit counter 0/0. This was window activation, not a map-edit
gesture. Never send content-changing keys or clicks through a mismatched image,
and never automate Codex's own UI to minimize it. Re-observe the actual Toolkit
surface before any map action. This observation does not establish why occluded
capture showed the foreground app or prove that future capture failures are fixed.
