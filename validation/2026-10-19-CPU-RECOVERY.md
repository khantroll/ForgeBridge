# CPU mitigation and recovery — 2026-10-19

PASS: supported desktop enumeration, activation, capture and input recovered.
Computer Use guidance was followed, with sequential requests and no concurrent
tests/builds during desktop work. No timeout occurred in this pass. The final
five Toolkit observations (refresh, Settings, Display, PlayerScreen expansion,
Stop projecting) completed 5/5; timeout frequency for that bounded sequence: 0/5.
Previous October 18 failures occurred during helper setup/enumeration, before
capture; they must not be counted as screenshot failures.

Initial enumeration returned launcher, Waterfox player screen and Task Manager;
Toolkit was absent. Read-only host sampling also measured zero Toolkit processes.
No compute candidates were measured. Browser CPU was 0.78–1.54%, launcher
4.90–6.88%, helper 0%. Existing Waterfox capture and launcher activation/capture
succeeded. Toolkit was launched normally through the existing launcher, then
selected by newly discovered window identifier 9111242. No administrator launch,
priority, power, security or unrelated-process changes were made. Per-process
elevation was not remeasured in this pass.

Toolkit 0.5.1.18 / launcher 7.0.0.3, two logical CPUs. Native supported settings:

| Setting | Observed original | Applied / verified |
|---|---|---|
| Settings → Performance → Quality settings → Maximum framerate | 60 | 30; Current frame rate displayed 30.0 after leaving the field |
| Display → Add extended screen → Local network streaming → Player Screen → Streaming settings | 1920×1080, 30 FPS defaults | 1280×720, 15 FPS; verified on active PlayerScreen |
| Asset / fog / lighting quality | Ultra native / Medium 40% / Medium 180 points | Unchanged |

After cap, empty map Toolkit CPU: 4.64, 5.68, 5.43%; browser 1.29–1.81%;
helper 0.26–0.78%. After loading the existing **ForgeBridge Profile Crypt
2026-10-16**, with reduced stream active: Toolkit 16.91, 15.21, 17.22%; browser
0.26–2.33%; helper 0–0.77%. Raw reports accompany this document. Sampler overhead
appears in `other` and these are normalized process deltas, not system-total
counters. Historical loaded Toolkit samples were 70.8–76.5% with failed helper
calls. This supports reduced contention as a useful operating condition; no
same-scene 60-vs-30 controlled CPU baseline was collected, so causation and the
cap's isolated CPU benefit are not established.

The existing Crypt map loaded; GM framing only changed from 100% to 95% zoom.
No tokens, notes, geometry or source visibility states were edited or saved.
No packages were rebuilt or installed. Only one Waterfox player window was
enumerated; tab count was not inferred from process count. Stream was stopped
through **Stop projecting**, with “Local streaming stopped” observed, before
automated work. An independent in-app player stream was not started.

PASS (automated, not runtime): full suite **148 run, 144 passed, four skipped**,
48.387 seconds, exit 0. Windows symlink skips remain skips, not passed safety
checks. Both formerly problematic tests passed, including ZIP LevelDB scene
loading and the no-dynamic-execution safety assertion. Log retained locally at
`.test-tmp/cpu-mitigated-full-tests.txt`. Previous full run took 1618.064 seconds
and had two issues; this comparison also differs in corrected code and host state.

PENDING: Crypt actual-player token visibility, both profile player restart checks.
DEFERRED: bounded fog human gesture. This recovery pass does not establish player
behavior from the GM view. Accepted earlier GM/Multi Scene/Manor observations
remain unchanged. Labels off; GIF setup manual; Foundry vision/fog, procedural
animation and actor/stat behavior remain explicit gaps. Next desktop task is
representative profile player testing using these limits, separately from compute.
Independent development remains unblocked.
