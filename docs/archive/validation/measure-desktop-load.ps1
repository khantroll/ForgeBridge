<#
.SYNOPSIS
Read-only process CPU sampling for a separate desktop-validation phase.
.DESCRIPTION
Run before UI work, never concurrently with capture. No app control, priority,
power, security or network changes. An optional JSON report refuses overwrite.
Process names identify candidates, not whether a process is actually building.
#>
[CmdletBinding()]
param(
    [ValidateRange(1, 10)][int]$Samples = 3,
    [ValidateRange(1, 10)][int]$IntervalSeconds = 3,
    [ValidateSet('before', 'after', 'timeout-recovery')][string]$Phase = 'before',
    [string]$OutputFile
)
$ErrorActionPreference = 'Stop'
if ($OutputFile -and (Test-Path -LiteralPath $OutputFile)) {
    throw "Report exists: $OutputFile. Choose a new evidence path."
}
$taskProcessorCount = [Environment]::ProcessorCount
function Get-TaskSnapshot {
    $taskSnapshot = @{}
    foreach ($taskProcess in Get-Process) {
        if ($taskProcess.Id -eq 0) { continue } # Idle time is not CPU consumption.
        try {
            $taskCpu = $taskProcess.TotalProcessorTime.TotalSeconds
            $taskSnapshot[$taskProcess.Id] = [pscustomobject]@{
                name = $taskProcess.ProcessName
                cpu = $taskCpu
                tick = [Diagnostics.Stopwatch]::GetTimestamp()
                working_mb = [math]::Round($taskProcess.WorkingSet64 / 1MB, 1)
            }
        } catch { } # Protected or exited processes are not measured.
    }
    return $taskSnapshot
}
function Get-TaskCategory([string]$ProcessName) {
    switch -Regex ($ProcessName) {
        '^MastersToolkit$' { return 'toolkit' }
        '^ArkenforgeLauncher$' { return 'launcher' }
        '^codex-computer-use' { return 'capture_helper' }
        '^(waterfox|firefox|chrome|msedge)$' { return 'browser' }
        '^(python|pythonw|py|7z|7za|ffmpeg|magick|pdftoppm|mutool)$' { return 'compute_candidate' }
        '^(ChatGPT|Codex|codex-code-mode-host|node|node_repl)$' { return 'client_or_runtime' }
        default { return 'other' }
    }
}
$taskMeasurements = @()
for ($taskIndex = 0; $taskIndex -lt $Samples; $taskIndex++) {
    $taskBefore = Get-TaskSnapshot
    Start-Sleep -Seconds $IntervalSeconds
    $taskAfter = Get-TaskSnapshot
    $taskRows = @(
        foreach ($taskId in $taskAfter.Keys) {
            if (-not $taskBefore.ContainsKey($taskId)) { continue }
            $taskOld = $taskBefore[$taskId]
            $taskNew = $taskAfter[$taskId]
            if ($taskOld.name -ne $taskNew.name) { continue }
            $taskElapsed = ($taskNew.tick - $taskOld.tick) / [double][Diagnostics.Stopwatch]::Frequency
            $taskDelta = $taskNew.cpu - $taskOld.cpu
            if ($taskElapsed -le 0 -or $taskDelta -lt 0) { continue }
            [pscustomobject]@{
                name = $taskNew.name
                pid = $taskId
                category = Get-TaskCategory $taskNew.name
                cpu_percent = [math]::Round(100 * $taskDelta / $taskElapsed / $taskProcessorCount, 2)
                working_mb = $taskNew.working_mb
            }
        }
    )
    $taskCategories = [ordered]@{}
    $taskCategoryCounts = [ordered]@{}
    foreach ($taskCategory in @('toolkit', 'launcher', 'browser', 'capture_helper', 'compute_candidate', 'client_or_runtime', 'other')) {
        $taskMembers = @($taskRows | Where-Object category -eq $taskCategory)
        $taskCategoryCounts[$taskCategory] = $taskMembers.Count
        $taskSum = ($taskMembers | Measure-Object cpu_percent -Sum).Sum
        $taskCategories[$taskCategory] = if ($taskMembers.Count) { [math]::Round([double]$taskSum, 2) } else { $null }
    }
    $taskMeasurements += [pscustomobject]@{
        utc = [datetime]::UtcNow.ToString('o')
        category_cpu_percent = $taskCategories
        category_measured_process_count = $taskCategoryCounts
        top_processes = @($taskRows | Sort-Object cpu_percent -Descending | Select-Object -First 12)
    }
}
$taskReport = [ordered]@{
    format = 'forgebridge.desktop-load'
    version = 1
    phase = $Phase
    logical_processors = $taskProcessorCount
    interval_seconds = $IntervalSeconds
    scope = 'Approximate CPU deltas normalized across logical processors; not proof of timeout causation. Protected/exited processes may be omitted; browser totals include unrelated tabs. Compute candidates are names, not confirmed builds.'
    samples = $taskMeasurements
}
$taskJson = $taskReport | ConvertTo-Json -Depth 8
$taskJson = $taskJson.Replace("`r`n", "`n")
if ($OutputFile) {
    $taskDestination = [IO.Path]::GetFullPath($OutputFile)
    $taskStream = [IO.File]::Open($taskDestination, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write)
    try {
        $taskBytes = [Text.UTF8Encoding]::new($false).GetBytes($taskJson + "`n")
        $taskStream.Write($taskBytes, 0, $taskBytes.Length)
    } finally { $taskStream.Dispose() }
}
$taskJson
