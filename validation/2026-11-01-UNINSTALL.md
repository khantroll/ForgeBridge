# Uninstall from receipts — 2026-11-01 (Codex run, Toolkit closed)

Reverse install order, `forgebridge install --uninstall <receipt>`; MyAssets
snapshots (path + SHA-256) before and after.

| Install | Exit | Removed | Result |
|---|---:|---:|---|
| Manor 2nd Floor (GUI) | 0 | 138 | PASS |
| Manor 1st Floor | 1 | 0 | Refused: `D000-P003.rwnote` changed since install |
| Count's Crypt | 0 | 304 | PASS |

Diff of MyAssets after vs. the first backup (taken before any ForgeBridge
install): the 134 Manor 1st files still present; `Maps/New Map.rwmap/.rwmeta`
changed (already different before the uninstall run; not written by
ForgeBridge, presumably the Toolkit's own working map); **no original file
missing**. No surviving file changed during the uninstall run. Backups and
receipts retained.

## Findings

1. **Correct refusal.** `D000-P003` of Manor 1st is very likely the Den note,
   opened from its marker during the Toolkit check
   (2026-11-01-MANOR-INSTALL.md); opening a note evidently rewrites its file. The
   uninstaller refused before deleting anything, as designed.
2. **Bug:** the CLI error handler referenced `zipfile` without importing it, so a
   refusal surfaced as `NameError` instead of exit 1 + message. Fixed; test added.
3. **Usability gap:** ordinary use (opening a note) blocks uninstall. Added
   `--keep-changed`: removes every file still identical to its recorded hash,
   leaves changed/missing ones, lists them, and marks the receipt
   `UNINSTALLED_KEPT_CHANGED`. Tested on a fake MyAssets.

Remaining: run `--keep-changed` on the Manor 1st receipt (expect 133 removed,
1 kept), then confirm in the Toolkit that the ForgeBridge maps are gone.
