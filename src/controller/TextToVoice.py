import os.path
import tempfile
from src.utils.TelegramOperations import sendTelegramMessage
from src.config.config import Configurations
from src.controller.f5_tts.AudioModel import F5TTS
from src.utils.Base64 import base64_decode, base64_encode

class TextToVoice:

    @staticmethod
    def _save_reference_audio_local(reference_audio: str) -> str:
        try:
            os.makedirs('audio', exist_ok=True)
            if reference_audio.startswith('data:') and ';base64,' in reference_audio:
                header, b64data = reference_audio.split(';base64,', 1)
                ext = '.wav'
                if 'audio/' in header:
                    ext = '.' + header.split('audio/')[1]
                path = os.path.join('audio', 'ref_audio' + ext)
                with open(path, 'wb') as f:
                    f.write(base64_decode(b64data))
                return path


            decoded = base64_decode(reference_audio, validate=True)
            path = os.path.join('audio', 'ref_audio.wav')
            with open(path, 'wb') as f:
                f.write(decoded)
            return path
        except Exception as e:
            raise Exception('Failed to load reference_audio: ' + str(e))

    @staticmethod
    def text_to_voice_cloning_converter(text_in: list, lang: str, reference_audio: str, ref_text: str = None):
        try:
            audio_ref = TextToVoice._save_reference_audio_local(reference_audio)
            ckpt_file = ''
            preproc_lang = 'es' if lang in ('Spanish', 'es') else 'en'
            if lang == 'Spanish' or lang == 'es':
                ckpt_file = Configurations.MSNLP_AI_F5TTS_AUDIO_CHECKPOINT_ES
            elif lang == 'English' or lang == 'en':
                ckpt_file = Configurations.MSNLP_AI_F5TTS_AUDIO_CHECKPOINT_EN
            else:
                ckpt_file = Configurations.MSNLP_AI_F5TTS_AUDIO_CHECKPOINT_EN

            model = F5TTS(ckpt_file=ckpt_file)

            _, ext = os.path.splitext(audio_ref)

            texts_in = [text_in[i:i + Configurations.BATCH_SIZE] for i in range(0, len(text_in), Configurations.BATCH_SIZE)]
            waves = []
            for text in texts_in:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_out:
                    file_save = tmp_out.name

                wav, sr, spect = model.infer(
                    ref_file=audio_ref,
                    ref_text=ref_text or '',
                    gen_text=text,
                    file_wave=file_save,
                    speed=0.8,
                    remove_silence=False,
                    lang=preproc_lang,
                )

                with open(file_save, 'rb') as f:
                    wav_b64 = base64_encode(f.read()).decode('utf-8')
                waves.append(wav_b64)
            return {
                'audios_base64': waves,
            }
        except Exception as e:
            sendTelegramMessage('📌🤮Exception at voice cloning ia method, raise error '+str(e))
            return {
                "status": 500,
                "message": 'Error: ' + str(e)
            }