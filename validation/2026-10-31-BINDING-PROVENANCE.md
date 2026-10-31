# Pinned binding provenance and trace readiness — 2026-10-31

PASS (file-level): downloaded the pinned cp314/win-amd64 wheel and source archive
from PyPI without installing or executing downloaded code. Verified their SHA256
against PyPI 2.1.2 JSON metadata:

| Artifact | SHA256 |
|---|---|
| plyvel_next-2.1.2-cp314-cp314-win_amd64.whl | `5716a13eaa8613e8f83422292bbad6930b381b169af3cfd10bab1553a17aa262` |
| plyvel_next-2.1.2.tar.gz | `fadf128846e173b97b9fec1764eaf86a4d5226d6882d51cfe0f3a8e3f7ba0b53` |

The installed extension and every bundled DLL hash match their wheel members:

| Installed member | SHA256 |
|---|---|
| _plyvel.cp314-win_amd64.pyd | `6f078f99374f221dd167a4c9f556648fd5e65b7a426df3bee0a380201e3a164a` |
| leveldb DLL | `5ef874100049eecce76bcb4dcd2383199363cce6d1a8e0d206f49db0d201afbc` |
| msvcp140 DLL | `a4c2229bdc2a2a630acdc095b4d86008e5c3e3bc7773174354f3da4f5beb9cde` |
| snappy DLL | `0bc48c7ead01b6a9163cb2b5a07aaa57c1349b7bc0592c4e84170af0b69305de` |

Queried only version-returning C API functions in the already installed LevelDB
DLL: major=1, minor=23. This identifies compiled version **1.23**. It does not
establish an exact source commit or absence of build-time patches. No source build,
dependency change, DLL replacement or package installation performed.

The public binding repository's current scripts/install-leveldb.ps1 also selects
LevelDB1.23 (blob91b472b11879f328cf6e3c11dae13ecabb1d0b51). This is corroborating
current build metadata, not cryptographic proof it produced this wheel. The sdist
contains pyproject.toml but not that build script. Upstream LevelDB1.23's Windows
rename source uses the MoveFileA/ReplaceFileA sequence already probed; no longer
necessary to rely solely on latest main. Downloaded artifacts stay locally under
.test-tmp/2026-10-31-wheel-provenance; no downloaded scripts run.

Sources: [PyPI pinned release](https://pypi.org/project/plyvel-next/2.1.2/),
[binding Windows build script](https://github.com/Modding-Forge/plyvel-next/blob/master/scripts/install-leveldb.ps1),
[LevelDB1.23 Windows source](https://github.com/google/leveldb/blob/1.23/util/env_windows.cc).

PASS (read-only tool availability): WPR10.0.26100, WPA and logman are installed.
WPR -status says not recording; -profiles lists FileIO and Minifilter. ProcMon/
ProcMon64 were not on PATH; this is not a full-disk absence claim. These commands
started no trace and changed no privilege or settings.

PENDING APPROVAL: built-in FileIO would collect system-wide filenames/metadata,
exceeding the prior owned-file-only diagnostic scope. A concrete one-capture plan
is [LEVELDB-TRACE.md](../docs/LEVELDB-TRACE.md). No collection started and no admin
elevation attempted. Raw ETL must stay local; support transmission is not authorized.

Superseding outcome: user explicitly approved one short local capture. Attempted
`wpr -start FileIO` in the current non-elevated context after confirming no existing
recording. WPR returned signed exit -2147024891, **0x80070005 Access is denied**,
profile FileIO.Verbose.Memory. Follow-up -status confirms WPR is not recording.
No diagnostic process was launched under WPR, no ETL created, no -stop/-cancel
called against another session, and no escalation of Windows privileges attempted.
The tool's sandbox approval only permits host execution; it does not grant a
Windows administrator token. Raw before/start/after text stays under
.test-tmp/2026-10-31-approved-wpr. Actual file-I/O tracing is now BLOCKED by access;
additional tracing rights require a separately authorized Windows operator action.

Root cause remains unresolved, and latest full suite remains 173 run/168 passed/
four skips/one LevelDB error. No new tests were needed for read-only provenance
inspection/documents; preceding seven targeted reader/probe checks remain separate.
No native runtime claim, installed campaign read/edit, source mutation or merge.

Independent roadmap progress: all production package builds now include
manual_steps and runtime_acceptance in conversion-report.json, plus explicit
bounded-fog exclusion/Foundry vision guidance in INSTALL.txt. This applies to
explicit builds as well as profiles; it does not mark fog passed or implement
vision. Six package regressions pass, 4.634s. Latest full-suite failure remains
unchanged; no full rerun performed for this report-only addition.
