from os import environ, getenv
from contextlib import suppress


def setEnvVar(name, value):
    environ[name] = value


def getCastEnv(name, default, cast):
    with suppress(Exception):
        return cast(getenv(name, default))
    return default


def getIntEnv(name, default):
    return getCastEnv(name, default, int)


def getFloatEnv(name, default):
    return getCastEnv(name, default, float)


def getBoolEnv(name, default):
    return getCastEnv(name, default, bool)


def getListEnv(name, default):
    return getCastEnv(name, default, list)


class Configurations:
    PREFIX = 'LAMBDA_VC_'
    MSNLP_AI_F5TTS_AUDIO_CHECKPOINT_ES = getenv(PREFIX + 'AI_F5TTS_AUDIO_CHECKPOINT_ES', 'src/controller/f5_tts/checkpoints/es/model_1200000.safetensors')
    MSNLP_AI_F5TTS_AUDIO_CHECKPOINT_EN = getenv(PREFIX + 'AI_F5TTS_AUDIO_CHECKPOINT_EN', 'src/controller/f5_tts/checkpoints/en/model_1200000.pt')
    MSNLP_AI_F5TTS_AUDIO_VOCAB_ES = getenv(PREFIX+'AI_F5TTS_AUDIO_VOCAB_ES', 'src/controller/f5_tts/vocab/vocab_es.txt')
    LAMBDA_VC_BUCKET_NAME = getenv(PREFIX+'BUCKET_USER_AUDIO_FILES', 'fyself_audio_users')
    BATCH_SIZE = getenv(PREFIX + 'BATCH_SIZE', 10)
    TELEGRAM_BOT_TOKEN = getenv(PREFIX + "TELEGRAM_BOT_TOKEN", "1919318351:AAGSLE_ootbLpaOPgwU0Enuyl3d3wpzc9kI")
