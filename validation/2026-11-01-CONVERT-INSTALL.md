# End-to-end convert + install + Toolkit — 2026-11-01

First full run of the new-user flow on the real Count's Manor package: no manual
UVTT import, export or calibration, no installed templates.

## Command (run by Codex on the Windows host, Toolkit confirmed closed)

```
python -m pip install .
forgebridge convert "C:\AMD\lob-counts_manor-pk-v13\ForgeBridge\lob-counts_manor-pk-v13" --scene-key 49e50a53aeebc515a48f1d82 --out "C:\AMD\fb-convert-crypt-2026-11-01b" --install --myassets "C:\Program Files (x86)\ArkenforgeData\MyAssets" --backup-root "C:\AMD\fb-backups"
```

Exit 0. Installation report PASS: 304 files added, receipt COMPLETE, no refusals.
Backup: `C:\AMD\fb-backups\forgebridge-da098b9146b74a05bf960de9d54d58a7\MyAssets`
(353.7 MiB, 1,401 files). Content: 84 notes, 19 room markers, 9 tokens, 1 token
explicitly rejected. (A Linux build from a partial copy of the package produced
290 files; the 7 extra image pairs come from package files that copy omitted.
The generated .rwmap is byte-identical in size, 325,873 bytes.)

Two earlier attempts refused safely and led to fixes: missing `PYTHONPATH`
(now `pip install .` provides `forgebridge`, f815323) and a not-yet-created
backup folder (installer now creates the final folder under an existing parent,
a91243d).

## Toolkit 0.5.1.18 runtime (Claude)

- Map Browser shows folder **ForgeBridge** → **ForgeBridge Count's Crypt -
  c293b013c0** with a real background thumbnail (schema-generated).
- Opens with edit counter 0/0. Walls, doors (closed red / open), lights render on
  the drawn crypt; fresh manual fog enabled (covered for players, as reported).
- Tokens present including hidden ones; selecting one shows **Cursed Cannibal**.
- Room-marker icons present; selecting one shows note **Sir Knight Lugosi's S…**.
- Closed without saving.

Geometry is the same synthesis already verified record-for-record against the
Toolkit's own import (validation/2026-11-01-DIRECT-MAP.md).

## Observations / follow-ups

- Map metadata shows creator "ForgeBridge" and a fixed last-modified of
  12/31/2025 6:00 PM local (deterministic build timestamp). Cosmetic; consider
  using build time.
- Opening a marker's note from the map and the player view of this installed
  output were not re-run here (both validated earlier on profile outputs).
- A double-click on the map background registered one native edit (no visible
  change); not saved.
