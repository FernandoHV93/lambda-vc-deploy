import os
# Must be set before ANY torch import so inductor never attempts C compilation
os.environ["TORCHDYNAMO_DISABLE"] = "1"

import traceback

import runpod
from typing import Dict, Any

# Startup errors (bad dependency versions, missing CUDA kernels, ...) used to
# crash the worker before it could answer, and Runpod logs are not reachable.
# Capture them and return them in the job response instead.
STARTUP_ERROR = None
try:
    import torch

    # True no-op: intercepts every torch.compile() call inside voxcpm (or any dep)
    # before inductor ever looks for a C compiler.
    # TORCHDYNAMO_DISABLE alone is insufficient because inductor raises the
    # RuntimeError before dynamo's own error-suppression machinery can catch it.
    def _noop_compile(fn=None, *_, **__):
        # Handles: torch.compile(fn), @torch.compile, @torch.compile()
        return fn if fn is not None else (lambda f: f)

    torch.compile = _noop_compile

    from src.service.APIService import process_clone_job_sync
    from src.utils.Base64 import base64_decode, compute_hash
except BaseException:
    STARTUP_ERROR = traceback.format_exc()
    print(STARTUP_ERROR, flush=True)


def _gpu_diagnostics() -> Dict[str, Any]:
    info: Dict[str, Any] = {}
    try:
        import torch
        info["torch"] = torch.__version__
        info["torch_cuda"] = torch.version.cuda
        info["cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            info["gpu"] = torch.cuda.get_device_name(0)
            info["capability"] = list(torch.cuda.get_device_capability(0))
            info["arch_list"] = torch.cuda.get_arch_list()
    except BaseException as e:
        info["diagnostics_error"] = str(e)
    return info


def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    input_data = event.get("input", {})

    if STARTUP_ERROR:
        return {"status": 500, "message": "Worker startup error", "startup_error": STARTUP_ERROR,
                "diagnostics": _gpu_diagnostics()}

    # Health probe: {"input": {"diagnostics": true}} returns GPU/torch info, no model load.
    if input_data.get("diagnostics"):
        return {"status": 200, "message": "OK", "diagnostics": _gpu_diagnostics()}

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


