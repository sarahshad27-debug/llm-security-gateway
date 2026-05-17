from langdetect import detect, LangDetectException
from deep_translator import GoogleTranslator

# Supported language codes
SUPPORTED_LANGUAGES = {
    "en": "English",
    "ur": "Urdu",
    "ko": "Korean",
    "ar": "Arabic",
    "hi": "Hindi",
}


def detect_language(text: str) -> str:
    """
    Detects the language of the input text.
    Returns ISO 639-1 language code (e.g. 'en', 'ur', 'ko').
    Falls back to 'en' if detection fails.
    """
    try:
        lang = detect(text)
        return lang
    except LangDetectException:
        return "en"


def translate_to_english(text: str, source_lang: str) -> str:
    """
    Translates text to English using Google Translate via deep-translator.
    Returns original text if translation fails or language is already English.

    Limitation: Translation may lose obfuscation cues present in the original
    (e.g. character substitutions like 0 for o). The translated version is used
    for semantic scoring; rule-based detection always runs on the original.
    """
    if source_lang == "en":
        return text

    try:
        translated = GoogleTranslator(source=source_lang, target="en").translate(text)
        return translated if translated else text
    except Exception:
        # If translation fails, return original — detectors will still run on it
        return text


def get_language_info(text: str) -> dict:
    """
    Returns detected language code and name, plus English translation if needed.
    """
    detected = detect_language(text)
    translated = translate_to_english(text, detected)

    return {
        "detected_language": detected,
        "language_name": SUPPORTED_LANGUAGES.get(detected, detected),
        "translated_text": translated,
        "was_translated": detected != "en"
    }