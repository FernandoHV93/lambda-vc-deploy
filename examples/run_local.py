import json
import base64
import os
from pathlib import Path
import  hashlib
from src.utils.Base64 import compute_hash

import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

from rp_handler import handler


def file_to_base64(path: str):
    with open(path, "rb") as f:
        audio_bytes = f.read()
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
    return audio_b64, audio_bytes

def main():
    ref_file = os.environ.get('REF_AUDIO', '')
    if not ref_file:
        print('Set REF_AUDIO to a small wav/mp3 file path')
        return
    audio_b64, audio_bytes = file_to_base64(ref_file)
    checksum = compute_hash(audio_bytes)
    payload = {
        "input": {
            "job_id": "local-test",
            "guide_text": "Lea detenidamente, con voz clara el siguiente texto: Confirmo que esta grabación de voz es mía o que tengo todos los derechos necesarios para enviarla. Al continuar, declaro que he leído y aceptado los Términos de Uso de FySelf y de la aplicación TwinH para este envío.",
            "language": "es",
            "text_to_speech": ["En una tranquila tarde de verano,", "los niños jugaban en el parque mientras los adultos conversaban alegremente,", "disfrutando del cálido sol que iluminaba cada rincón del pequeño vecindario."],
            "reference_audio": audio_b64,
            "checksum": checksum,
        }
    }
    res = handler(payload)
    for i, result in enumerate(res['result']):
        decoded = base64.b64decode(result, validate=True)
        path = os.path.join('audio', 'result_audio' + str(i) + '.wav')
        with open(path, 'wb') as f:
            f.write(decoded)
    # print(json.dumps({k: (v[:50] + '...') if k == 'result_audio_base64' and isinstance(v, str) else v for k, v in res.items()}, indent=2))


if __name__ == '__main__':
    main()


