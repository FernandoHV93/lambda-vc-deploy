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
    ENVIROMENT = getenv(PREFIX + "ENVIROMENT", 'prod')
    ENVIROMENT_PROD = 'prod'
    ENVIROMENT_STAGING = 'staging'
    BASE_URL = getenv('BASE_URL', '')
    LAMBDA_VC_LANGUAGE = getenv("LAMBDA_VC_LANGUAGE", 'es')
    LAMBDA_VC_AUDIOPATH = getenv(PREFIX+"AUDIOPATH", 'assets')
    MSNLP_AI_F5TTS_AUDIO_CHECKPOINT_ES = getenv(PREFIX + 'AI_F5TTS_AUDIO_CHECKPOINT_ES', 'src/controller/f5_tts/checkpoints/es/model_1200000.safetensors')
    MSNLP_AI_F5TTS_AUDIO_CHECKPOINT_EN = getenv(PREFIX + 'AI_F5TTS_AUDIO_CHECKPOINT_EN', 'src/controller/f5_tts/checkpoints/en/model_1200000.pt')
    MSNLP_AI_F5TTS_AUDIO_VOCAB_ES = getenv(PREFIX+'AI_F5TTS_AUDIO_VOCAB_ES', 'src/controller/f5_tts/vocab/vocab_es.txt')
    LAMBDA_VC_BUCKET_NAME = getenv(PREFIX+'BUCKET_USER_AUDIO_FILES', 'fyself_audio_users')
    FYSELF_S3_MODELS = getenv(PREFIX + "FYSELF_S3_MODELS", "fyself-ia-models")
    MSNLP_BUCKET_NAME = getenv("MSNLP_BUCKET_NAME", 'nlp-glove-data')
    LAMBDA_VC_OUTPUT_PREFIX = getenv(PREFIX + 'OUTPUT_PREFIX', 'voice-clones')
    BATCH_SIZE = getenv(PREFIX + 'BATCH_SIZE', 10)

    @staticmethod
    def isProd():
        return Configurations.ENVIROMENT == Configurations.ENVIROMENT_PROD

    @staticmethod
    def isStaging():
        return Configurations.ENVIROMENT == Configurations.ENVIROMENT_STAGING