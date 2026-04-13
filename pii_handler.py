from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_custom import all_custom_recognizers


analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# Registering all the custom recognizers
for recognizer in all_custom_recognizers:
    analyzer.registry.add_recognizer(recognizer)
def detect_pii(text):
    results = analyzer.analyze(
        text=text,
        language="en"
    )
    return results

def anonymize_pii(text):
    detected = detect_pii(text)

    if not detected:
        return text, []
    anonymized = anonymizer.anonymize(text=text, analyzer_results=detected)
    return anonymized.text, detected
    return anonymized.text, detected  
