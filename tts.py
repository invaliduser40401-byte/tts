import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

import numpy as np
import sounddevice as sd
from piper import PiperVoice

ROOT = Path(__file__).resolve().parent
VOICE_DIR = ROOT / "voices"
CONFIG = ROOT / "config.json"
VOICE_NAME = "en_US-lessac-medium"

def load_config():
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except Exception:
        return {"device": "", "speed": 1.0, "volume": 1.0}

def save_config():
    try:
        CONFIG.write_text(json.dumps({
            "device": device_var.get(),
            "speed": float(speed_var.get()),
            "volume": float(volume_var.get())
        }, indent=2), encoding="utf-8")
    except Exception:
        pass

def output_devices():
    return [
        (i, d["name"])
        for i, d in enumerate(sd.query_devices())
        if d["max_output_channels"] > 0
    ]

def refresh_devices():
    names = [name for _, name in output_devices()]
    device_box["values"] = names

    if device_var.get() not in names:
        preferred = next(
            (n for n in names if "CABLE Input" in n or "VB-Audio" in n),
            names[0] if names else ""
        )
        device_var.set(preferred)

def speak():
    text = input_box.get("1.0", "end").strip()
    if not text:
        return

    model = VOICE_DIR / f"{VOICE_NAME}.onnx"
    if not model.exists():
        messagebox.showerror("Piper", "The voice is missing. Run setup.ps1 again.")
        return

    try:
        speed = max(0.5, min(2.0, float(speed_var.get())))
        volume = max(0.0, min(2.0, float(volume_var.get())))
    except ValueError:
        messagebox.showerror("Settings", "Speed and volume must be numbers.")
        return

    selected_name = device_var.get()
    selected_device = next(
        (i for i, name in output_devices() if name == selected_name),
        None
    )

    speak_btn.config(state="disabled", text="SPEAKING...")
    status_var.set("Generating speech...")

    def worker():
        try:
            voice = PiperVoice.load(str(model))
            chunks = []
            sample_rate = 22050

            for chunk in voice.synthesize(text):
                sample_rate = chunk.sample_rate
                chunks.append(chunk.audio_int16_bytes)

            samples = np.frombuffer(
                b"".join(chunks), dtype=np.int16
            ).astype(np.float32) / 32768.0

            if speed != 1.0 and len(samples) > 1:
                old_x = np.linspace(0, 1, len(samples))
                new_len = max(1, int(len(samples) / speed))
                new_x = np.linspace(0, 1, new_len)
                samples = np.interp(new_x, old_x, samples)

            samples *= volume
            sd.play(samples, sample_rate, device=selected_device, blocking=True)

            root.after(0, lambda: status_var.set("Ready"))
        except Exception as exc:
            root.after(0, lambda: messagebox.showerror("TTS error", str(exc)))
            root.after(0, lambda: status_var.set("Error"))
        finally:
            root.after(0, lambda: speak_btn.config(state="normal", text="SPEAK"))

    threading.Thread(target=worker, daemon=True).start()

def stop():
    sd.stop()
    status_var.set("Stopped")

cfg = load_config()

root = tk.Tk()
root.title("Piper TTS Mic")
root.geometry("760x470")
root.minsize(620, 380)

main = ttk.Frame(root, padding=14)
main.pack(fill="both", expand=True)

ttk.Label(
    main, text="Piper TTS Mic",
    font=("Segoe UI", 18, "bold")
).pack(anchor="w")

ttk.Label(
    main,
    text="Type text, press SPEAK, and send the audio to any output device."
).pack(anchor="w", pady=(0, 10))

input_box = tk.Text(
    main, height=9, wrap="word", font=("Segoe UI", 12)
)
input_box.pack(fill="both", expand=True)
input_box.bind("<Control-Return>", lambda _: speak())

controls = ttk.Frame(main)
controls.pack(fill="x", pady=10)
controls.columnconfigure(1, weight=1)

ttk.Label(controls, text="Output:").grid(row=0, column=0, sticky="w")
device_var = tk.StringVar(value=cfg.get("device", ""))
device_box = ttk.Combobox(
    controls, textvariable=device_var, state="readonly", width=55
)
device_box.grid(row=0, column=1, padx=6, sticky="ew")
ttk.Button(controls, text="Refresh", command=refresh_devices).grid(
    row=0, column=2
)

ttk.Label(controls, text="Speed:").grid(row=1, column=0, sticky="w")
speed_var = tk.StringVar(value=str(cfg.get("speed", 1.0)))
ttk.Entry(controls, textvariable=speed_var, width=10).grid(
    row=1, column=1, padx=6, sticky="w"
)

ttk.Label(controls, text="Volume:").grid(row=2, column=0, sticky="w")
volume_var = tk.StringVar(value=str(cfg.get("volume", 1.0)))
ttk.Entry(controls, textvariable=volume_var, width=10).grid(
    row=2, column=1, padx=6, sticky="w"
)

buttons = ttk.Frame(main)
buttons.pack(fill="x")

speak_btn = ttk.Button(buttons, text="SPEAK", command=speak)
speak_btn.pack(side="left")

ttk.Button(buttons, text="STOP", command=stop).pack(
    side="left", padx=6
)

ttk.Button(buttons, text="Save settings", command=save_config).pack(
    side="right"
)

status_var = tk.StringVar(value="Ready")
ttk.Label(main, textvariable=status_var).pack(
    anchor="w", pady=(8, 0)
)

refresh_devices()
root.protocol("WM_DELETE_WINDOW", lambda: (save_config(), root.destroy()))
root.mainloop()
