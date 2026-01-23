import os
from src.config.config import Configurations
import requests
from src.utils.TelegramOperations import sendTelegramMessage


def is_single_model_checkpoint_downloaded( localModelPath, huggingfaceUri):
    localFolderModelPath = os.path.dirname(localModelPath)
    model_name = os.path.basename(localModelPath)

    if os.path.exists(localModelPath):
        return localModelPath

    if not os.path.exists(localFolderModelPath):
        os.makedirs(localFolderModelPath, exist_ok=True)
    if not os.path.exists(localModelPath):
        with open(localModelPath, mode='x'):
            pass

    response = requests.get(huggingfaceUri)
    if not response.ok:
        sendTelegramMessage(f"ERROR is_single_model_checkpoint_downloaded\n",
                            f"No se ha podido descargar el modelo {model_name}")
        raise Exception(f"No se ha podido descargar el modelo {model_name}")

    with open(localModelPath, 'wb') as f:
        f.write(response.content)

    return localModelPath

def is_model_checkpoint_downloaded(model_name: list):
    cached_paths = []
    if 'F5TTS_ES' in model_name:
        path = is_single_model_checkpoint_downloaded(Configurations.MSNLP_AI_F5TTS_AUDIO_CHECKPOINT_ES,
                                                     "https://huggingface.co/jpgallegoar/F5-Spanish/resolve/main/model_1200000.safetensors?download=true"
                                                     )
        cached_paths.append(path)
    if 'F5TTS_EN' in model_name:
        path = is_single_model_checkpoint_downloaded(Configurations.MSNLP_AI_F5TTS_AUDIO_CHECKPOINT_EN,
                                                     "https://huggingface.co/SWivid/F5-TTS/resolve/main/F5TTS_Base/model_1200000.pt?download=true"
                                                     )
        cached_paths.append(path)
    return cached_paths