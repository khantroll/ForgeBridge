# Capture timeout diagnosis — 2026-10-18

This is a desktop/helper diagnostic, not a ForgeBridge conversion failure.
No campaign/map content, Windows security setting, process priority or driver changed.

## Observations

- Host Windows11 Pro build26200; Codex package26.1007.9446.0.
- Intel Celeron G5905T, two logical processors. Two host CPU-load observations report100%.
- Short process CPU-delta sample attributes approximately97.4% of total two-thread capacity to MastersToolkit PID1856. Sampling is approximate; this establishes heavy load, not causation of capture failure.
- Approximately18GB physical RAM free of32GB; memory exhaustion not supported by this snapshot.
- Toolkit, launcher and codex-computer-use-swift all report Responding=True and Normal priority. Responding does not prove the screenshot pipeline is healthy.
- Helper window enumeration times out twice; timed retry10471ms. Failure therefore extends beyond a Toolkit screenshot request.
- Installed guidance's supported Node REPL reset performed after the two failures. Fresh sky initialization/list request itself reaches the30-second execution timeout; kernel automatically resets. Did not recover control.
- Earlier actual errors: `FrameArrived timed out: timed out waiting on channel` and `window capture timed out: timed out waiting on channel`. These are screenshot/helper deadlines, not native-package validation errors.
- Today's app log records computer-use native-pipe startup ready, followed by a Windows Appshot hotkey registration warning `Appshot capture deadline expired` at2026-10-18T11:18:26.162Z. This predates the present diagnostic and is supporting capture-stack evidence, not a proven common cause.
- Radeon RX6800XT driver32.0.21041.1000 and Parsec Virtual Display Adapter0.45.0.0 both report Status=OK. The virtual-display capture path remains a possible variable; neither its involvement nor a driver fault is established. Limited recent System-event scan returned no matching display/GPU/DWM warning/error.

## Conclusion and discriminating test

Toolkit CPU saturation is the strongest measured resource problem. The native capture/helper request path is unresponsive; an additional graphics/capture deadlock remains possible. Do not call CPU load alone a confirmed root cause, or blame firewall, Foundry data, token hidden state or ForgeBridge.

Requested human action: minimize Toolkit normally without closing/saving/changing content, leave it minimized and report completion. Compare host CPU load and a fresh supported helper enumeration/capture of an ordinary window while minimized. This cannot currently be performed by native UI automation because even enumeration times out. Do not bypass it with a different automation mechanism or suspend/kill processes.

If CPU drops and helper capture recovers, test a native FPS/render-load limit and player-stream load separately, one setting at a time. If CPU drops but capture still fails, collect the same minimal reproduction in an ordinary app for app support; preserve unsaved work before a normal app restart. No uninstallation, driver replacement or privilege change justified yet. No diagnostic/log upload or third-party issue was submitted.

Official troubleshooting reference consulted: https://learn.chatgpt.com/docs/reference/troubleshooting (Feedback and logs; review logs for sensitive data before sharing). It does not establish a specific fix for FrameArrived timeouts.

Toolkit's own Player.log confirms hardware Direct3D11 rendering on the Radeon RX6800XT (Unity2021.3.45f2), not an identified software-rendering fallback. Recent tail contains `Releasing render texture that is set to be RenderTexture.active!`; its relationship to the Computer Use failure is unknown. Registry read returned1920x1080/native/fullscreen settings, but no matching FPS preference. No frame-rate configuration change attempted. The minimize comparison still awaits human confirmation.

Workflow follow-up: user reports Toolkit could not be minimized. The subsequent CPU-aware workflow preserves that observation without another intervention request. Baseline Toolkit70.8–76.5%; recovery72.3–75.8%; helper0% in counted sample. One setup/enumeration attempt times out at30s, zero screenshot attempts. Native30-FPS and720p/15-FPS changes are BLOCKED/unapplied; no after-intervention result. See contention-comparison.json and docs/DESKTOP-VALIDATION.md. Independent sampler/runbook implementation continued with UI paused.
