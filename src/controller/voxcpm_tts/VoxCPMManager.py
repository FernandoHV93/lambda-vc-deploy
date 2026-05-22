import os
import soundfile as sf

# Disable torch dynamo/inductor compilation — no C compiler in Lambda environment
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")

from voxcpm import VoxCPM


class VoxCPMTTS:

    @staticmethod
    def generate_audio(
        text_in: str,
        reference_audio: str,
        result_audio_path: str,
        ref_text: str = None,
    ):
        model = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False)

        if ref_text:
            # Ultimate cloning: highest fidelity using reference audio + transcript
            wav = model.generate(
                text=text_in,
                prompt_wav_path=reference_audio,
                prompt_text=ref_text,
                reference_wav_path=reference_audio,
            )
        else:
            # Controllable cloning: timbre only from reference audio
            wav = model.generate(
                text=text_in,
                reference_wav_path=reference_audio,
                cfg_value=2.0,
            )

        sf.write(result_audio_path, wav, model.tts_model.sample_rate)
