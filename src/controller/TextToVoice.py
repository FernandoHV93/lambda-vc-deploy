import os.path
from src.utils.TelegramOperations import sendTelegramMessage
from src.config.config import Configurations
from src.utils.S3Service import download_file, upload_file
from src.controller.f5_tts.AudioModel import F5TTS

class TextToVoice:

    @staticmethod
    def text_to_voice_cloning_converter(text_in,audio_reference, audio_path, lang,voiceCloningId=None, ref_text = None):
        try:
            if voiceCloningId:
                s3_audio_path = voiceCloningId
            else:
                raise Exception("voiceCloningId is required")
            audio_ref = Configurations.LAMBDA_VC_AUDIOPATH + os.path.basename(s3_audio_path)
            if not os.path.exists(audio_ref):
                download_file(s3_audio_path, audio_ref)
            ckpt_file = ''
            preproc_lang = 'es'
            if lang == 'Spanish' or lang == 'es':
                ckpt_file = Configurations.MSNLP_AI_F5TTS_AUDIO_CHECKPOINT_ES

            elif lang =='English' or lang == 'en':
                ckpt_file = Configurations.MSNLP_AI_F5TTS_AUDIO_CHECKPOINT_EN

            else:
                ckpt_file = Configurations.MSNLP_AI_F5TTS_AUDIO_CHECKPOINT_EN
               
            audio_cloning_es = F5TTS(ckpt_file=ckpt_file)
            ref_text = ref_text

            _, ext = os.path.splitext(audio_ref)
            file_save = audio_path + audio_reference + '_cloned' + ext
            auxFolder = os.path.dirname(file_save)
            if auxFolder != "" and not os.path.exists(auxFolder):
                os.makedirs(auxFolder, exist_ok=True)
            if not os.path.exists(file_save):
                with open(file_save, "w"):
                    pass

            wav, sr, spect = audio_cloning_es.infer(ref_file=audio_ref,
                                                    ref_text=ref_text,
                                                    gen_text=text_in,
                                                    file_wave=file_save, speed=0.8,
                                                    remove_silence=False,
                                                    lang=preproc_lang)
            seed = audio_cloning_es.seed
            upload_file(file_save)
            del audio_cloning_es
            return 'OK'
        except Exception as e:
            raise sendTelegramMessage('📌🤮Exception at voice cloning ia method, raise error'+str(e))