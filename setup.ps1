$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== Piper TTS Mic setup ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Checking for VB-CABLE..." -ForegroundColor Cyan

$vbCableInstalled = $false
try {
    $devices = Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue
    $vbCableInstalled = [bool]($devices | Where-Object {
        $_.FriendlyName -match "CABLE (Input|Output)" -or $_.FriendlyName -match "VB-Audio.*Cable"
    })
} catch {}

if (-not $vbCableInstalled) {
    Write-Host "VB-CABLE not found. Downloading the official package..." -ForegroundColor Yellow

    $vbDir = Join-Path $PSScriptRoot "vb-cable"
    $zip = Join-Path $PSScriptRoot "VBCABLE_Driver_Pack45.zip"

    if (-not (Test-Path $zip)) {
        Invoke-WebRequest -Uri "https://download.vb-audio.com/Download_CABLE/VBCABLE_Driver_Pack45.zip" -OutFile $zip -UseBasicParsing
    }

    if (Test-Path $vbDir) {
        Remove-Item $vbDir -Recurse -Force
    }

    Expand-Archive -Path $zip -DestinationPath $vbDir -Force

    $installer = Get-ChildItem $vbDir -Recurse -Filter "VBCABLE_Setup_x64.exe" | Select-Object -First 1
    if (-not $installer) {
        $installer = Get-ChildItem $vbDir -Recurse -Filter "VBCABLE_Setup.exe" | Select-Object -First 1
    }

    if (-not $installer) {
        throw "VB-CABLE installer was not found in the downloaded package."
    }

    Write-Host "Launching VB-CABLE installer as administrator..." -ForegroundColor Yellow
    Start-Process -FilePath $installer.FullName -Verb RunAs -Wait

    Write-Host ""
    Write-Host "VB-CABLE installation finished." -ForegroundColor Green
    Write-Host "A Windows restart is required before CABLE Input/Output may appear." -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "VB-CABLE is already installed." -ForegroundColor Green
}

$py = $null
try { $py = (py -3.13 -c "import sys; print(sys.executable)" 2>$null) } catch {}

if (-not $py) {
    Write-Host "Python 3.13 not found. Installing with winget..." -ForegroundColor Yellow
    winget install --id Python.Python.3.13 -e --accept-source-agreements --accept-package-agreements
    $py = (py -3.13 -c "import sys; print(sys.executable)" 2>$null)
}
if (-not $py) { throw "Python 3.13 could not be found." }

if (-not (Test-Path ".venvScriptspython.exe")) {
    & py -3.13 -m venv .venv
}

$python = Join-Path $PSScriptRoot ".venvScriptspython.exe"
$voiceDir = Join-Path $PSScriptRoot "voices"
New-Item -ItemType Directory -Force $voiceDir | Out-Null

Write-Host "Installing Piper and audio libraries..." -ForegroundColor Cyan
& $python -m pip install --upgrade pip
& $python -m pip install piper-tts sounddevice numpy

if (-not (Test-Path (Join-Path $voiceDir "en_US-lessac-medium.onnx"))) {
    Write-Host "Downloading the default English voice..." -ForegroundColor Cyan
    & $python -m piper.download_voices --data-dir $voiceDir en_US-lessac-medium
} else {
    Write-Host "Piper voice already downloaded." -ForegroundColor Green
}

Write-Host ""
Write-Host "Setup complete." -ForegroundColor Green
Write-Host "If VB-CABLE was just installed, restart Windows before using the TTS mic." -ForegroundColor Yellow
Write-Host "Then run run.bat."
