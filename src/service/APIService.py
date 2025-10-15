from src.controller.TextToVoice import TextToVoice


def process_clone_job_sync(guide_text: str, text_to_speech: str, reference_audio: str, language: str, return_strategy: str = 'base64'):
    return TextToVoice.text_to_voice_cloning_converter(
        text_in=text_to_speech,
        lang=language,
        reference_audio=reference_audio,
        ref_text=guide_text,
        return_strategy=return_strategy,
    )