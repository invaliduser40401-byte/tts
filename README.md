# Piper TTS Mic

A small Windows app for typing text and sending local Piper TTS audio to any Windows output device.

## Run

Double-click `run.bat`.

The first run automatically creates a Python virtual environment, installs Piper TTS plus audio support, and downloads the default English voice.

After setup, `run.bat` opens the TTS window directly.

## Virtual microphone

With VB-CABLE installed:

TTS app -> CABLE Input -> Discord/game microphone = CABLE Output

The app remembers the selected output device, speed, and volume.

Piper upstream: https://github.com/OHF-Voice/piper1-gpl