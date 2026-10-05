$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== Piper TTS Mic setup ===" -ForegroundColor Cyan

$py = $null
try { $py = (py -3.13 -c "import sys; print(sys.executable)" 2>$null) } catch {}

if (-not $py) {
    Write-Host "Python 3.13 not found. Installing with winget..." -ForegroundColor Yellow
    winget install --id Python.Python.3.13 -e --accept-source-agreements --accept-package-agreements
    $py = (py -3.13 -c "import sys; print(sys.executable)" 2>$null)
}
if (-not $py) { throw "Python 3.13 could not be found." }

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    & py -3.13 -m venv .venv
}

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$voiceDir = Join-Path $PSScriptRoot "voices"
New-Item -ItemType Directory -Force $voiceDir | Out-Null

Write-Host "Installing Piper and audio libraries..." -ForegroundColor Cyan
& $python -m pip install --upgrade pip
& $python -m pip install piper-tts sounddevice numpy

Write-Host "Downloading the default English voice..." -ForegroundColor Cyan
& $python -m piper.download_voices --data-dir $voiceDir en_US-lessac-medium

Write-Host ""
Write-Host "Setup complete. Run run.bat." -ForegroundColor Green
