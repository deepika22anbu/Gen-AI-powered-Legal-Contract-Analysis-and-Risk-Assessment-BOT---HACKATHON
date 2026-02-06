import langdetect
from deep_translator import GoogleTranslator

def normalize_to_english(text):

    if not text or len(text.strip()) < 10:
        return text

    try:
        language = langdetect.detect(text)
    except:
        return text

    #  English → pass unchanged
    if language == "en":
        return text

    #  Hindi → translate to English
    if language == "hi":
        translator = GoogleTranslator(source="hi", target="en")

        # Chunking to avoid Google limit
        chunks = [text[i:i + 4000] for i in range(0, len(text), 4000)]
        translated_chunks = [translator.translate(chunk) for chunk in chunks]

        return "\n".join(translated_chunks)

    #  Any other language → pass unchanged
    return text
