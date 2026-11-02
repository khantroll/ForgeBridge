# Fresh-operator run by Jeffrey — 2026-11-02 (in progress)

Fresh clone to `C:\AMD\fb-fresh`, following docs/USER-GUIDE.md without help.

## Findings so far (all fixed in the guide unless noted)

1. `git clone` creates a `ForgeBridge` subfolder; the guide never said to `cd`
   into it, so `git checkout` failed ("not a git repository").
2. The guide hard-coded `py -3.13`; the host has only Python 3.14, so the venv was
   never created and activation then failed. Now `py -m venv .venv`, with a
   `py --list` fallback.
3. The guide led new users down the developer path (`PYTHONPATH`, raw JSON
   report) instead of `pip install .` + `forgebridge-gui`. Split into
   *Quick start* and *Developer setup*.
4. Re-running the self-check failed with "Choose a new output directory under an
   existing parent" because the folder already existed. Message now says the
   folder exists and ForgeBridge never overwrites (`convert.py`).
5. Pasting the ```powershell fence line into PowerShell errors. Guide now says to
   type each line, not the fences.
6. The synthetic self-check prints ~900 lines of JSON. Left as is (CI and tests
   parse it); the guide now tells users to look for "status": "PASS".

Remaining: GUI install of Count's Lair, Toolkit check, uninstall.
