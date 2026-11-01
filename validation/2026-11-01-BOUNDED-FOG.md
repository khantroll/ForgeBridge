# Bounded fog reveal/hide — 2026-11-01

## Outcome

PASS: bounded manual fog reveal → cover → reveal, observed in actual player output.
PASS (save step): the disposable map saved; a later Toolkit exit raised no
unsaved-changes prompt.
PENDING: persistence after a normal restart. The relaunch failed inside Toolkit
(see below) before the map could be reopened.

Toolkit 0.5.1.18 / launcher 7.0.0.3, launched normally. Desktop control: Claude
computer use. Player output: Claude desktop app built-in browser at
`http://127.0.0.1/`, stream 1280×720 / 15 FPS. No ICE-candidate exception in
this session (third clean built-in-browser session; Waterfox and Chrome attempts
on 10-31 raised it — see validation/2026-10-31-PLAYER-ADDRESS.md).

## Map

Disposable copy only: **ForgeBridge Fog Test 2026-10-31**, created 10-31 with
Maps → Save as new from ForgeBridge Profile Crypt 2026-10-16 (last modified
10/31/2026 5:42:52 PM before this run). Profile Crypt and Profile Manor were not
opened or saved. Saved manual fog was enabled with nothing revealed.

## Steps and observations

1. Opened the copy; edit counter 0/0. Started the stream; player output black with
   "Fog of war is active!".
2. Live Play/VTT → Fog of War → Manual fog options: brush function **Erase fog**,
   shape **Box selection**. One box dragged over the north Cursed Cannibal room.
   Player output: **only that room visible**, Cursed Cannibal token in it; the rest
   of the map stays black. Edit counter 1/0.
3. Brush function **Brush fog**, box over the same room. Player output: **fully
   black** again. Edit counter 2/0.
4. **Erase fog** box again: player output shows the same single room again. Brush
   function set back to None. Edit counter 3/0.
5. Maps → **Save map** on the copy (title bar confirmed "ForgeBridge Fog Te…").
6. Stopped projecting; Quit → Yes. **No unsaved-changes prompt**, so the save
   included the fog edits.

## Restart attempt (not a Toolkit pass or fail of the fog feature)

The first relaunch click on the launcher landed while it still showed "Running
Arkenforge Toolkit". The new Toolkit instance stopped at "An error has occurred.
Please try restarting the Masters Toolkit"; its unstable-state details read:

```text
NullReferenceException: Object reference not set to an instance of an object
UISoundManager.PlaySound
TextButton.DoStateTransition
UnityEngine.UI.Selectable.EvaluateAndTransitionToSelectionState
UnityEngine.UI.Selectable.OnPointerEnter
ArkenButton.OnPointerEnter
UnityEngine.EventSystems.ExecuteEvents.Execute
```

A UI hover sound failure during startup, most likely from launching before the
previous instance had fully exited. Neither "Close the Arkenforge Toolkit" nor
"Exit Toolkit" responded; the process needs to be ended by the user. No map
was open in that instance.

## Next

End the hung Toolkit, launch normally once the launcher no longer says
"Running", open the Fog Test copy, start the stream, connect the built-in
browser at 127.0.0.1 and confirm only the north room is visible to players.
