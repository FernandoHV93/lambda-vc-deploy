import os.path
import base64
import tempfile
from urllib.parse import urlparse
import requests
from src.utils.TelegramOperations import sendTelegramMessage
from src.config.config import Configurations
from src.utils.S3Service import download_file, upload_file, generate_presigned_url
from src.controller.f5_tts.AudioModel import F5TTS

class TextToVoice:

    @staticmethod
    def _save_reference_audio_local(reference_audio: str) -> str:
        try:
            os.makedirs('/tmp', exist_ok=True)
            if reference_audio.startswith('data:') and ';base64,' in reference_audio:
                header, b64data = reference_audio.split(';base64,', 1)
                ext = '.wav'
                if 'audio/' in header:
                    ext = '.' + header.split('audio/')[1]
                path = os.path.join('/tmp', 'ref_audio' + ext)
                with open(path, 'wb') as f:
                    f.write(base64.b64decode(b64data))
                return path

            try:
                decoded = base64.b64decode(reference_audio, validate=True)
                path = os.path.join('/tmp', 'ref_audio')
                with open(path, 'wb') as f:
                    f.write(decoded)
                return path
            except Exception:
                pass

            parsed = urlparse(reference_audio)
            if parsed.scheme in ('http', 'https'):
                ext = os.path.splitext(parsed.path)[1] or '.wav'
                path = os.path.join('/tmp', 'ref_audio' + ext)
                r = requests.get(reference_audio, timeout=30)
                r.raise_for_status()
                with open(path, 'wb') as f:
                    f.write(r.content)
                return path

            filename = os.path.join('/tmp', os.path.basename(reference_audio))
            if not os.path.exists(filename):
                download_file(reference_audio, filename)
            return filename
        except Exception as e:
            raise Exception('Failed to load reference_audio: ' + str(e))

    @staticmethod
    def text_to_voice_cloning_converter(text_in: str, lang: str, reference_audio: str, ref_text: str = None, return_strategy: str = 'base64'):
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
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_out:
                file_save = tmp_out.name

            wav, sr, spect = model.infer(
                ref_file=audio_ref,
                ref_text=ref_text or '',
                gen_text=text_in,
                file_wave=file_save,
                speed=0.95,
                remove_silence=False,
                lang=preproc_lang,
            )
            seed = model.seed
            if return_strategy == 's3':
                object_name = os.path.join(Configurations.LAMBDA_VC_OUTPUT_PREFIX, os.path.basename(file_save))
                upload_file(file_save, object_name=object_name)
                url = generate_presigned_url(object_name)
                return {
                    's3_url_presigned': url,
                    's3_key': object_name,
                    'format': 'wav',
                    'sample_rate': sr,
                    'seed': seed
                }
            else:
                with open(file_save, 'rb') as f:
                    wav_b64 = base64.b64encode(f.read()).decode('utf-8')
                return {
                    'audio_base64': wav_b64,
                    'format': 'wav',
                    'sample_rate': sr,
                    'seed': seed
                }
        except Exception as e:
            sendTelegramMessage('📌🤮Exception at voice cloning ia method, raise error'+str(e))
            raise