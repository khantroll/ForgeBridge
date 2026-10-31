# Next LevelDB diagnostic: bounded local file-I/O trace

This is an approval plan, not evidence that tracing ran or that the cause is known.
Use only for the retained error1175 reproduction. Do not change the converter,
disable antivirus/indexing, change ACLs, elevate Toolkit/helper, or retry a failed
database operation. Native export/campaign files are not involved.

October31 outcome: the user approved this one capture, but WPR start was denied
with **0x80070005**, FileIO.Verbose.Memory, under the non-elevated host token.
Before/after status says not recording. No ETL or traced diagnostic exists. The
next prerequisite is separately authorized Windows tracing rights; no automatic
elevation, permission edit or additional capture attempt is authorized by this
result. Toolkit and desktop helper stay non-elevated.

## Available tools and collection boundary

Read-only inspection on October31 found Windows Performance Recorder (WPR)
10.0.26100 and Windows Performance Analyzer (WPA) installed. WPR reports not
recording. Built-in FileIO/Minifilter profiles exist; ProcMon was not found on PATH.
No new software is required or installed by this plan.

Built-in FileIO recording is system-wide, not restricted at collection time to
ForgeBridge. It may include other processes' filenames and metadata. Analysis will
filter to the diagnostic output directory; raw ETL stays local under .test-tmp,
is never committed or sent externally, and must not be described as containing
only fixture activity. Permission to perform this broader capture is required
before starting. WPR may require administrator tracing rights; a normal
non-elevated context is currently in use. No application elevation is planned.

## One proposed capture

Prepare a **new** local directory before recording. Let all UI tests/builds stop,
and do not run a full test suite or player streaming during this experiment.
The commands below assume repository-root working directory and installed deps.
Replace `NEW` with a unique suffix. Use memory mode; do not enable unbounded
`-filemode`, boot tracing, persistent registry tracing or new drivers.

```powershell
$env:TEMP = "$PWD\.test-tmp"
$env:TMP = $env:TEMP
wpr -status
# Stop here if any existing recording is active. Do not cancel or replace it.
# Only after the specific trace permission has been granted:
wpr -start FileIO
py scripts/diagnose_leveldb.py --out .test-tmp/traced-LevelDB-NEW --trials 10
# Preserve the Python exit code as evidence, including a nonzero result.
wpr -stop .test-tmp/traced-LevelDB-NEW.etl -skipPdbGen
```

The diagnostic is bounded to ten distinct trials per case (six cases on Windows).
Each failed operation is recorded, never retried. Retain all database copies.
Recording should span only that diagnostic (normally seconds); cap the session at
30 seconds. If the diagnostic hangs or the tool reports an error, stop and save
only this newly started recording rather than beginning another trace. Run the
stop in a finally block if automating an approved capture. If start fails for
privileges, record its full output, confirm no session started, and do not elevate
or alter security settings automatically. Never run -cancel against an unowned
recording. No trace start/stop has been run as part of authoring this document.

## Evidence to extract locally

In WPA, filter File I/O to the new trial directory and the failing trial's time.
Identify operations on CURRENT, its new MANIFEST and `.dbtmp`, with process/thread,
operation/result, path and timestamps. If stacks/minifilter attribution are not
present, record that limitation; do not identify antivirus or another process by
guessing. A passing traced run is not a fix or a reason to repeat until failure.

Commit only a sanitized finding with exact trial and native error, trace/report
hashes and narrowly relevant process attribution when actually supported. Keep raw
ETL and unrelated paths local. If no matching failure occurs, record the run as
inconclusive and continue independent roadmap work. The latest failed full suite
remains authoritative until a justified change and relevant validation supersede it.

Microsoft reference: [WPR command-line options](https://learn.microsoft.com/en-us/windows-hardware/test/wpt/wpr-command-line-options).
Trace capability/permissions and on-host scheduling remain separate from ForgeBridge
conversion correctness. Bounded fog and native manual steps remain separate gates.
