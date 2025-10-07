from src.controller.TextToVoice import TextToVoice


def process_clone_job_sync(guide_text,text_to_speech, referece_audio, language):
    return TextToVoice.text_to_voice_cloning_converter(ref_text=guide_text,text_in=text_to_speech, voiceCloningId=referece_audio, lang=language)