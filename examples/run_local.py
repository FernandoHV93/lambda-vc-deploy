import json
import base64
import os
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

from rp_handler import handler


def file_to_base64(path: str) -> str:
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def main():
    ref_file = os.environ.get('REF_AUDIO', '')
    if not ref_file:
        print('Set REF_AUDIO to a small wav/mp3 file path')
        return
    payload = {
        "input": {
            "job_id": "local-test",
            "guide_text": "Breve muestra de referencia.",
            "language": "es",
            "text_to_speech": "Hola, esta es una prueba local de clonación.",
            "reference_audio": file_to_base64(ref_file)
        }
    }
    res = handler(payload)
    print(json.dumps({k: (v[:50] + '...') if k == 'result_audio_base64' and isinstance(v, str) else v for k, v in res.items()}, indent=2))


if __name__ == '__main__':
    main()


