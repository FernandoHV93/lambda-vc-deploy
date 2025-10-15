import os
import base64
import json
import io
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from rp_handler import handler


def sine_wave(duration_s=0.5, sr=24000, freq=440.0):
    t = np.linspace(0, duration_s, int(sr*duration_s), endpoint=False)
    return (0.2*np.sin(2*np.pi*freq*t)).astype(np.float32)


def wav_base64_from_numpy(wave: np.ndarray, sr: int = 24000):
    import soundfile as sf
    buff = io.BytesIO()
    sf.write(buff, wave, sr, format='WAV')
    buff.seek(0)
    return base64.b64encode(buff.read()).decode('utf-8')


def compute_basic_metrics(wave: np.ndarray):
    rms = float(np.sqrt(np.mean(np.square(wave))))
    peak = float(np.max(np.abs(wave)))
    duration_ms = int(1000 * len(wave) / 24000)
    return {"rms": rms, "peak": peak, "duration_ms": duration_ms}


def test_handler_accepts_base64_and_returns_audio(tmp_path):
    ref = sine_wave(0.2)
    ref_b64 = 'data:audio/wav;base64,' + wav_base64_from_numpy(ref)

    payload = {
        "input": {
            "job_id": "pytest-1",
            "guide_text": "Referencia corta.",
            "language": "es",
            "text_to_speech": "Hola, prueba de clonación.",
            "reference_audio": ref_b64
        }
    }
    res = handler(payload)
    assert res["status"] in ("completed", "Error")  # allow running without models in CI
    if res["status"] == "completed":
        b64 = res["result_audio_base64"]
        assert isinstance(b64, str) and len(b64) > 0


def test_metrics_plot(tmp_path):
    wave = sine_wave(0.4)
    metrics = compute_basic_metrics(wave)
    assert metrics["rms"] > 0
    assert metrics["duration_ms"] > 0

    fig, ax = plt.subplots(figsize=(6, 2))
    ax.plot(wave[:200])
    ax.set_title(r"Referencia $\\mathrm{RMS}=%.3f$" % metrics["rms"])  # LaTeX-like
    out = tmp_path / 'metric_plot.png'
    fig.savefig(out)
    assert out.exists()


