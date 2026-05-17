from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_custom import all_custom_recognizers, apply_context_boost

# Initialize engines
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

for recognizer in all_custom_recognizers:
    analyzer.registry.add_recognizer(recognizer)

# Secret entity types (used for secret_weight in policy engine)
SECRET_ENTITIES = {"API_KEY", "JWT_TOKEN", "PAKISTAN_CNIC", "PAKISTAN_IBAN", "PAKISTAN_PASSPORT"}

# Placeholder map — clear, readable anonymization
PLACEHOLDER_MAP = {
    "PERSON": "<PERSON>",
    "EMAIL_ADDRESS": "<EMAIL>",
    "PHONE_NUMBER": "<PHONE>",
    "PAKISTAN_PHONE": "<PHONE>",
    "PAKISTAN_CNIC": "<CNIC>",
    "PAKISTAN_IBAN": "<IBAN>",
    "PAKISTAN_SALARY": "<AMOUNT>",
    "PAKISTAN_CITY": "<CITY>",
    "PAKISTAN_INSTITUTE": "<INSTITUTE>",
    "PAKISTAN_PASSPORT": "<PASSPORT>",
    "STUDENT_ID": "<STUDENT_ID>",
    "API_KEY": "<API_KEY>",
    "JWT_TOKEN": "<JWT_TOKEN>",
    "CREDIT_CARD": "<CREDIT_CARD>",
    "LOCATION": "<LOCATION>",
    "URL": "<URL>",
    "NRP": "<NRP>",
}


def detect_pii(text: str, language: str = "en", min_confidence: float = 0.60) -> list:
    """
    Detects PII in text using Presidio + custom recognizers.
    Applies context-aware score boosting.
    Filters results below min_confidence threshold.
    """
    # Presidio only supports 'en' natively for NLP-based detection
    # For non-English, we analyze the translated version (passed from policy engine)
    analysis_lang = "en" if language not in ["en"] else language

    results = analyzer.analyze(
        text=text,
        language=analysis_lang,
        score_threshold=min_confidence
    )

    # Apply context-aware boosting
    results = apply_context_boost(text, results)

    # Filter again after boosting
    results = [r for r in results if r.score >= min_confidence]

    return results


def anonymize_pii(text: str, language: str = "en", min_confidence: float = 0.60):
    """
    Detects and anonymizes PII. Returns (anonymized_text, detected_entities_list).
    """
    detected = detect_pii(text, language, min_confidence)

    if not detected:
        return text, []

    # Build operator config using placeholder map
    operators = {}
    for result in detected:
        placeholder = PLACEHOLDER_MAP.get(result.entity_type, f"<{result.entity_type}>")
        operators[result.entity_type] = OperatorConfig(
            "replace", {"new_value": placeholder}
        )

    anonymized = anonymizer.anonymize(
        text=text,
        analyzer_results=detected,
        operators=operators
    )

    return anonymized.text, detected


def has_secrets(detected_entities: list) -> bool:
    """Returns True if any detected entity is a high-risk secret."""
    return any(e.entity_type in SECRET_ENTITIES for e in detected_entities)


def format_pii_entities(detected_entities: list, original_text: str) -> list:
    """Formats detected entities into JSON-serializable list for audit log."""
    formatted = []
    for entity in detected_entities:
        formatted.append({
            "type": entity.entity_type,
            "text": original_text[entity.start:entity.end],
            "score": round(entity.score, 3)
        })
    return formatted