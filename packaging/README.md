# Windows standalone build

Use Windows x64 Python in an isolated environment. CI uses Python 3.13.

```powershell
py -3.13 -m venv .build-venv
.\packaging\build_windows.ps1 -Python .\.build-venv\Scripts\python.exe
.\.build-venv\Scripts\python.exe packaging/smoke_windows.py --zip dist/windows/ForgeBridge-0.12.0-windows-x64.zip --fixture fixtures/synthetic-module --out .test-tmp/frozen-smoke
```

The script installs the project and pinned PyInstaller into the chosen
interpreter. Use a build venv, not a shared/system Python. Existing output roots
are refused; choose a new -OutDir for another build. No installation or Toolkit
operation occurs during the build. Smoke installation uses only its own new
fake MyAssets directory, but the normal Toolkit-closed guard still applies.
Local --skip-install is diagnostic only; CI runs every phase and requires PASS.

The spec combines two onedir executables in a shared COLLECT, with UPX disabled.
It uses package-relative __file__ data paths, collects the project's schemas and
metadata, and writes a build-info version fallback. Explicit native collection
includes plyvel-next's delvewheel DLL directory and pdfium; standard hooks
collect Pillow, psutil and Tcl/Tk. Test modules and optional large packages are
excluded. Needed Tcl/Tk runtime resources are retained, not indiscriminately
stripped. See [PyInstaller spec docs](https://pyinstaller.org/en/stable/spec-files.html)
and [runtime data paths](https://pyinstaller.org/en/stable/runtime-information.html).

The ZIP contains ForgeBridge/ with the GUI, CLI and _internal data. The CLI name
uses a suffix because Windows filenames are case-insensitive. build-summary.json
records folder/ZIP byte sizes, ZIP SHA-256 and largest contributors. If over
150 MB, review that list before trimming; preserve runtime encodings, icons,
schemas and native DLLs. Neither executable is code-signed.
Dependency license notices are included in the collected dist-info directories;
the Python license is in _internal/licenses/python.

The smoke test extracts the ZIP to a relocated path with spaces, clears Python
environment variables and removes Python from the child process PATH. It runs
the actual EXEs for conversion, PDF pages, LevelDB input and fake install /
uninstall --keep-changed. GUI diagnostics exercise real Tcl/Tk picker widgets,
native dialog-command validation, psutil, worker queues and error dispatch/logs.
They do not claim manual visual QA or native modal picker interaction.

On pushed v* tags, CI attaches the ZIP to an existing release or creates a
pre-release from matching docs/RELEASE-NOTES-v*.md. Tag/package-version mismatch,
missing notes or insufficient token permissions leave the workflow artifact and
an explicit summary. Existing assets are not overwritten. This PR does not move
old release tags or publish an unmerged candidate as a release.
