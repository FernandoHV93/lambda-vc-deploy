#!/usr/bin/env python3
"""
Prueba local del handler (como RunPod).
Usa un archivo de audio como referencia; genera base64 + checksum y llama al handler.

Uso:
  . .venv/bin/activate
  python run_local_test.py
  # o con otro audio:
  REF_AUDIO=path/to/ref.wav python run_local_test.py
"""
import os
import sys
import json
from pathlib import Path

# raíz del proyecto
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.utils.Base64 import compute_hash
from rp_handler import handler


def main():
    ref_path = os.environ.get("REF_AUDIO", "audio/ref_audio.wav")
    if not os.path.isfile(ref_path):
        print(f"No existe el archivo de referencia: {ref_path}")
        print("Crea audio/ref_audio.wav o define REF_AUDIO=path/to/ref.wav")
        sys.exit(1)

    with open(ref_path, "rb") as f:
        audio_bytes = f.read()
    ref_b64 = __import__("base64").b64encode(audio_bytes).decode("utf-8")
    checksum = compute_hash(audio_bytes)

    payload = {
        "input": {
            "guide_text": "Lea detenidamente, con voz clara el siguiente texto.",
            "language": "es",
            "text_to_speech": ["Hola, esta es una prueba de síntesis de voz clonada."],
            "reference_audio": ref_b64,
            "checksum": checksum,
        }
    }

    print("Llamando al handler (primera vez puede tardar: Chatterbox descarga el modelo)...")
    res = handler(payload)

    status = res.get("status")
    print(f"Status: {status}")
    if status == 200:
        result = res.get("result", [])
        print(f"Audios generados: {len(result)}")
        os.makedirs("audio", exist_ok=True)
        for i, b64 in enumerate(result):
            out_path = f"audio/result_audio_{i}.wav"
            with open(out_path, "wb") as f:
                f.write(__import__("base64").b64decode(b64))
            print(f"  Guardado: {out_path}")
    else:
        print("Message:", res.get("message", ""))


if __name__ == "__main__":
    main()
