import tempfile
from gtts import gTTS

def generate_voice(text: str, lang: str):
    tts_lang = "ml" if lang == "ml" else "en"
    tts = gTTS(text=text, lang=tts_lang)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    return temp_file.name
