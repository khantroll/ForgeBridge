# Fantasy Grounds reader vs Arkenforge's own FGU export — 2026-11-02

Ground truth: the native map **ForgeBridge Direct Crypt 2026-11-01** (199 walls,
23 doors — 3 of them open — and 66 lights; record-for-record identical to the
Toolkit's own UVTT import, validation/2026-11-01-DIRECT-MAP.md).

Export: Arkenforge Toolkit 0.5.1.18 → Export Map → VTT Export → **Fantasy
Grounds Unity**, PNG, export area drawn by Jeffrey with a margin around the map.
Output: `ForgeBridge Direct Crypt 2026-11-01.png` (5000×4800) + `.xml` sidecar
(`root version="4.1" dataversion="20210302"`, gridsize 100,100, gridoffset 0,50,
222 occluders, 66 lights, ambient block). Not committed.

Written by independent software (Arkenforge), so this checks the doors, windows
and lights paths that MFE 91 could not.

## Result — exact

Wrapped as a minimal module (definition.xml, db.xml image record with grid on,
image + sidecar) and read with `fantasy_grounds.to_uvtt`:

| | Original | Read back | Match |
|---|---:|---:|---|
| Walls | 199 | 199 | 199/199 segments, endpoints within 0.02 sq (actual 0.0) |
| Doors (closed) | 20 | 20 doors | 23/23 portals: endpoints exact (0.0), open/closed state equal |
| Doors (open) | 3 | 3 windows | Arkenforge writes open doors as `allow_vision` windows |
| Lights | 66 | 66 | positions exact (0.0 sq) |

The map sits at grid offset (5, 3) inside the larger export image, exactly the
margin of the export area; the centre-origin/y-up transform is confirmed again.

## Findings

- Arkenforge's FGU door flags: `toggleable closed counterclockwise hidden
  single_sided allow_move`; open doors: `toggleable closed allow_vision
  counterclockwise allow_move`. The reader handles both (window = see-through).
- **Light radius**: Arkenforge's exporter scales radius by ≈0.88 and rounds to
  0.1 square (1.6→1.4, 2.4→2.1, 4.0→3.6, 6.0→5.3, 8.0→7.1; 0.2 and 0.4
  unchanged). The reader reproduces the file's dim radius exactly; the
  difference is in Arkenforge's export, not the reader.
- `gridoffset 0,50` is present; it does not affect geometry here (grid display
  only) and is reported as an approximate loss line.
- Extra fields not used: `<ambient><on/><ambientcolor>`, top-level `<color>`.

## Coverage now

| Feature | Real FG-authored (MFE 91) | Arkenforge FGU export | uvtt2fgu writer | Synthetic tests |
|---|---|---|---|---|
| Centre-origin, y-up | ✔ | ✔ | ✔ | ✔ |
| Walls | ✔ (layer) | ✔ (sidecar) | ✔ | ✔ |
| Doors / windows | — | ✔ | ✔ | ✔ |
| Lights | — | ✔ | ✔ | ✔ |
| Missing gridsize | ✔ | — | — | ✔ |
| Encrypted vault modules refused | ✔ (real vault files) | — | — | ✔ |
