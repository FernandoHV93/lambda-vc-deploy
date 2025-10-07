import os

import runpod

from typing import Dict, Any
from src.service.APIService import process_clone_job_sync
from src.utils.S3Service import download_file_bucket, list_files, upload_file
from src.config.config import Configurations
import requests
from src.utils.TelegramOperations import sendTelegramMessage



def is_single_model_checkpoint_downloaded( localModelPath, fyself_s3_models, huggingfaceUri):
    localFolderModelPath = os.path.dirname(localModelPath)
    model_name = os.path.basename(localModelPath)

    if os.path.exists(localModelPath):
        sendTelegramMessage(f"is_single_model_checkpoint_downloaded\nModelo ya existe\n ",
                            f"localModelPath: {localModelPath}\n ",
                            f"fyself_s3_models:{fyself_s3_models}\n ",
                            f"model_name:{model_name}\n ",
                            f"huggingfaceUri:{huggingfaceUri}\n ",
                            )
        return localModelPath

    if not os.path.exists(localFolderModelPath):
        os.makedirs(localFolderModelPath, exist_ok=True)
    if not os.path.exists(localModelPath):
        with open(localModelPath, mode='x'):
            pass

    if Configurations.isProd() or Configurations.isStaging():
        modelS3Path = Configurations.FYSELF_S3_MODELS + "/" + model_name
        if modelS3Path in fyself_s3_models:
            rr = download_file_bucket(Configurations.MSNLP_BUCKET_NAME, modelS3Path, localModelPath)
            sendTelegramMessage(f"is_single_model_checkpoint_downloaded\n",
                                f"Descargado desde S3 {model_name}",
                                f"result:{rr}")
            return str(localModelPath)

    response = requests.get(huggingfaceUri)
    if not response.ok:
        sendTelegramMessage(f"ERROR is_single_model_checkpoint_downloaded\n",
                            f"No se ha podido descargar el modelo {model_name}")

    sendTelegramMessage(f"is_single_model_checkpoint_downloaded\nDescargado desde huggingfaceUri {model_name}")

    with open(localModelPath, 'wb') as f:
        f.write(response.content)

    if Configurations.isProd() or Configurations.isStaging():
        if not upload_file(localModelPath, folder=Configurations.FYSELF_S3_MODELS):
            sendTelegramMessage(f"WARNING is_single_model_checkpoint_downloaded\n",
                                f"No se pudo subir el modelo {model_name} a S3")

    return localModelPath
def is_model_checkpoint_downloaded(model_name: list):
    fyself_s3_models = []
    if Configurations.isProd() or Configurations.isStaging():
        fyself_s3_models = list_files(Configurations.FYSELF_S3_MODELS, Configurations.MSNLP_BUCKET_NAME)

    cached_paths = []
    if 'F5TTS_ES' in model_name:
        path = is_single_model_checkpoint_downloaded(Configurations.MSNLP_AI_F5TTS_AUDIO_CHECKPOINT_ES,
                                                            fyself_s3_models,
                                                            "https://huggingface.co/jpgallegoar/F5-Spanish/resolve/main/model_1200000.safetensors?download=true"
                                                            )
        cached_paths.append(path)
    if 'F5TTS_EN' in model_name:
        path = is_single_model_checkpoint_downloaded(Configurations.MSNLP_AI_F5TTS_AUDIO_CHECKPOINT_EN,
                                                            fyself_s3_models,
                                                            "https://huggingface.co/SWivid/F5-TTS/resolve/main/F5TTS_Base/model_1200000.pt?download=true"
                                                            )
        cached_paths.append(path)
    return cached_paths


def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    input_data = event.get("input", {})
    out = {}
    out["job_id"] = input_data.get("job_id")
    guide_text = input_data.get("guide_text")
    if not isinstance(guide_text, str):
        return {
            "job_id": out["job_id"],
            "status": "Error",
            "message": "Guide text is necessary!"
        }
    language = input_data.get("language")
    if not isinstance(language, str):
        return {
        "job_id": out["job_id"],
        "status": "Error",
        "message": "Language text is necessary!"
    }
    text_to_speech = input_data.get("text_to_speech")
    if not isinstance(text_to_speech, str):
        return {
        "job_id": out["job_id"],
        "status": "Error",
        "message": "Text to speech is necessary!"
    }

    reference_audio =input_data.get("reference_audio")


    if not isinstance(guide_text, str) or not guide_text:
        return {"error": "guide_text is required"}



    out = process_clone_job_sync(
        guide_text=guide_text,
        language=language,
        referece_audio=reference_audio,
        text_to_speech = text_to_speech
    )

    # Return a minimal confirmation to Runpod; heavy payload is sent to webhook.
    return {
        "job_id": out["job_id"],
        "status": "submitted",
    }



is_model_checkpoint_downloaded(['F5TTS_ES','F5TTS_EN'])
runpod.serverless.start({"handler": handler})


