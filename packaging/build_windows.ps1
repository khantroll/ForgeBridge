param(
    [string]$Python = 'python',
    [string]$OutDir = '',
    [switch]$SkipInstall
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
if (-not $OutDir) { $OutDir = Join-Path $repo 'dist\windows' }
$OutDir = [IO.Path]::GetFullPath($OutDir)
if (Test-Path -LiteralPath $OutDir) { throw "Output already exists; choose a new -OutDir: $OutDir" }
Push-Location $repo
try {
    & $Python -c "import sys,struct; assert sys.platform == 'win32' and struct.calcsize('P') == 8, 'Windows x64 Python required'"
    if ($LASTEXITCODE -ne 0) { throw 'Windows x64 build interpreter required' }
    if (-not $SkipInstall) {
        & $Python -m pip install . -r packaging/requirements-build.txt
        if ($LASTEXITCODE -ne 0) { throw 'Build dependency installation failed' }
    }
    $version = (& $Python -c "from importlib.metadata import version; print(version('forgebridge'))").Trim()
    if ($LASTEXITCODE -ne 0 -or $version -notmatch '^\d+\.\d+\.\d+([A-Za-z0-9.+-]*)$') { throw 'Invalid package version' }
    $work = Join-Path $repo ('.build\windows-' + [guid]::NewGuid().ToString('N'))
    & $Python -m PyInstaller --distpath $OutDir --workpath $work packaging/forgebridge.spec
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller build failed' }
    $folder = Join-Path $OutDir 'ForgeBridge'
    @'
ForgeBridge Windows app (unsigned)
Run ForgeBridge.exe for the GUI. Keep _internal and both EXEs together.
CLI: .\forgebridge-cli.exe --version
Uninstall: .\forgebridge-cli.exe install --uninstall "PATH\uninstall.json" --keep-changed
Unzip into a normal user folder, not Program Files or MyAssets.
Review conversion losses and installation conflicts. Toolkit must be closed for installation.
No Python install is needed to run these executables.
'@ | Set-Content -LiteralPath (Join-Path $folder 'WINDOWS-README.txt') -Encoding utf8
    $zip = Join-Path $OutDir "ForgeBridge-$version-windows-x64.zip"
    Compress-Archive -LiteralPath $folder -DestinationPath $zip -CompressionLevel Optimal
    $files = @(Get-ChildItem -LiteralPath $folder -File -Recurse)
    $summary = [ordered]@{version=$version; folder=$folder; zip=$zip;
        folder_bytes=($files | Measure-Object Length -Sum).Sum; zip_bytes=(Get-Item -LiteralPath $zip).Length;
        zip_sha256=(Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLowerInvariant();
        largest=@($files | Sort-Object Length -Descending | Select-Object -First 15 @{n='path';e={$_.FullName.Substring($folder.Length+1)}},Length)}
    $summary | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $OutDir 'build-summary.json') -Encoding utf8
    if ($summary.zip_bytes -gt 150MB) { Write-Warning 'ZIP exceeds 150 MiB; review largest contributors in build-summary.json before release.' }
    $summary | ConvertTo-Json -Depth 5
} finally { Pop-Location }
