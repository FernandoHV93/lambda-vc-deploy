import torch
import torchaudio
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

class ChatterboxTTS:

    @staticmethod
    def generate_multilingual_audio(
        text_in: str,
        reference_audio: str,
        result_audio_path: str,
        lang: str = 'es'
    ):
        # Detectar dispositivo
        use_cuda = torch.cuda.is_available()
        device = "cuda" if use_cuda else "cpu"

        # ⚠️ Solo parchear torch.load si NO hay GPU
        if not use_cuda:
            _original_load = torch.load

            def cpu_load(*args, **kwargs):
                kwargs["map_location"] = torch.device("cpu")
                return _original_load(*args, **kwargs)

            torch.load = cpu_load

        # Cargar modelo
        model = ChatterboxMultilingualTTS.from_pretrained(device=device)

        # Generar audio
        wav = model.generate(
            text_in,
            audio_prompt_path=reference_audio,
            language_id=lang
        )

        # Guardar resultado
        torchaudio.save(result_audio_path, wav, model.sr)
