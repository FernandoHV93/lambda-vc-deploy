import os.path
import tempfile
from src.controller.voxcpm_tts.VoxCPMManager import VoxCPMTTS
from src.utils.TelegramOperations import sendTelegramMessage
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
    def text_to_voice_cloning_converter(text_in: list, reference_audio: str, lang: str = 'es', ref_text: str = None):
        try:
            audio_ref = TextToVoice._save_reference_audio_local(reference_audio)

            waves = []
            for text in text_in:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_out:
                    file_save = tmp_out.name
                VoxCPMTTS.generate_audio(
                    text_in=text,
                    reference_audio=audio_ref,
                    result_audio_path=file_save,
                    ref_text=ref_text,
                )

                with open(file_save, 'rb') as f:
                    wav_b64 = base64_encode(f.read()).decode('utf-8')
                waves.append(wav_b64)

            return {
                'audios_base64': waves,
            }
        except Exception as e:
            sendTelegramMessage('📌🤮Exception at voice cloning ia method, raise error ' + str(e))
            return {
                "status": 500,
                "message": 'Error: ' + str(e)
            }