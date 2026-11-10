import os
# Must be set before ANY torch import so inductor never attempts C compilation
os.environ["TORCHDYNAMO_DISABLE"] = "1"

import torch

# True no-op: intercepts every torch.compile() call inside voxcpm (or any dep)
# before inductor ever looks for a C compiler.
# TORCHDYNAMO_DISABLE alone is insufficient because inductor raises the
# RuntimeError before dynamo's own error-suppression machinery can catch it.
def _noop_compile(fn=None, *_, **__):
    # Handles: torch.compile(fn), @torch.compile, @torch.compile()
    return fn if fn is not None else (lambda f: f)

torch.compile = _noop_compile

import runpod
from typing import Dict, Any
from src.service.APIService import process_clone_job_sync
from  src.utils.Base64 import base64_decode, compute_hash

def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    input_data = event.get("input", {})
    guide_text = input_data.get("guide_text", "")
    language = input_data.get("language")
    text_to_speech = input_data.get("text_to_speech")
    reference_audio = input_data.get("reference_audio")
    checksum = input_data.get("checksum")

    if not isinstance(language, str) or not language:
        return {
            "status": 400,
            "message": "language is required"
        }
    if not text_to_speech or not isinstance(text_to_speech, list) or not all(isinstance(x, str) for x in text_to_speech):
        return {
            "status": 400,
            "message": "text_to_speech is required"
        }
    if not isinstance(reference_audio, str) or not reference_audio:
        return {
            "status": 400,
            "message": "reference_audio is required (base64)"
        }
    if not checksum or not isinstance(checksum, str):
        return {
            "status": 400,
            "message": "checksum is required"
        }
    try:
        audio_bytes = base64_decode(reference_audio)
    except Exception:
        return {
            "status": 400,
            "message": "The base64 encoded audio is corrupted"
        }

    checksum_received = compute_hash(audio_bytes)

    # Compare
    if checksum_received != checksum:
        return {
            "status": 400,
            "message": "The audio is corrupted or has been altered."
        }

    result = process_clone_job_sync(
        guide_text=guide_text,
        language=language,
        reference_audio=reference_audio,
        text_to_speech=text_to_speech,
    )

    if result.get('status', None):
        return result

    out_payload = {
        "status": 200,
        "message": "OK",
        "result": result.get('audios_base64')
    }

    return out_payload



if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})


