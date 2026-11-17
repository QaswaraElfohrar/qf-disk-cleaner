# Builds the portable single-file exe + zip. Usage: powershell -ExecutionPolicy Bypass -File build.ps1 [-SkipTests]
param([switch]$SkipTests)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$py = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
$version = (& $py -c "import qfdisk; print(qfdisk.__version__)").Trim()
$dist = Join-Path $PSScriptRoot 'dist'
if (-not $SkipTests) {
    $env:QT_QPA_PLATFORM = 'offscreen'
    & $py -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw 'tests failed' }
    Remove-Item Env:QT_QPA_PLATFORM
}
if (Test-Path $dist) { Remove-Item $dist -Recurse -Force }
& $py -m PyInstaller --noconfirm --clean --noconsole --onefile --name QFDisk --icon "$PSScriptRoot\qfdisk\assets\icon.ico" `
    --add-data "$PSScriptRoot\qfdisk\assets;assets" --distpath $dist --workpath "$PSScriptRoot\build\pyi" --specpath "$PSScriptRoot\build" `
    --exclude-module tkinter --exclude-module PySide6.QtWebEngineCore --exclude-module PySide6.QtQml --exclude-module PySide6.QtQuick `
    --exclude-module PySide6.Qt3DCore --exclude-module PySide6.QtMultimedia --exclude-module PySide6.QtCharts --exclude-module PySide6.QtNetwork --exclude-module PySide6.QtPdf `
    run_app.py
if ($LASTEXITCODE -ne 0) { throw 'build failed' }
$exe = Join-Path $dist 'QFDisk.exe'
$named = Join-Path $dist "QFDisk-$version-win-x64.exe"
Copy-Item $exe $named
$stage = Join-Path $dist 'portable'
New-Item -ItemType Directory $stage | Out-Null
Copy-Item $exe $stage
'Portable: settings are saved in the "data" folder next to QFDisk.exe. Delete this folder to remove everything.' | Set-Content (Join-Path $stage 'README.txt')
Compress-Archive -Path "$stage\*" -DestinationPath (Join-Path $dist "QFDisk-$version-portable-win-x64.zip") -Force
Remove-Item $stage -Recurse -Force; Remove-Item $exe
Get-ChildItem $dist -File | Select-Object Name, @{n = 'MB'; e = { [math]::Round($_.Length / 1MB, 1) } } | Format-Table -AutoSize
