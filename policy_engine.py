import yaml
import os
import json
import uuid
import time
from injection_detector import calculate_injection_score
from semantic_detector import get_semantic_score
from pii_handler import anonymize_pii, has_secrets, format_pii_entities
from language_detector import get_language_info

# Load config
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config/gateway_config.yaml")

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

config = load_config()
thresholds = config["thresholds"]
weights = config["weights"]
pii_config = config["pii"]
log_config = config["logging"]

# Audit logger
os.makedirs(os.path.dirname(log_config["audit_log_path"]), exist_ok=True)

def write_audit_log(entry: dict):
    if log_config.get("enabled", True):
        with open(log_config["audit_log_path"], "a") as f:
            f.write(json.dumps(entry) + "\n")

# Main pipeline
def process_input(user_input: str, language: str = "auto", input_id: str = None) -> dict:
    start_time = time.time()

    if not input_id:
        input_id = str(uuid.uuid4())[:8]

    # Step 1: Language detection + translation
    lang_info = get_language_info(user_input)
    detected_lang = lang_info["detected_language"]
    text_for_analysis = lang_info["translated_text"]  # English translation for ML

    # Step 2: Rule-based detection (runs on ORIGINAL text — catches multilingual keywords)
    rule_raw_score = calculate_injection_score(user_input)
    # Normalize: treat 1 match as 0.6, 2+ as 0.85, 3+ as 1.0
    if rule_raw_score == 0:
        rule_score = 0.0
    elif rule_raw_score == 1:
        rule_score = 0.60
    elif rule_raw_score == 2:
        rule_score = 0.85
    else:
        rule_score = 1.0

    # Step 3: Semantic detection (runs on translated English text)
    semantic_score = get_semantic_score(text_for_analysis)

    # Step 4: PII detection (runs on original text)
    cleaned_text, detected_entities = anonymize_pii(
        user_input,
        language=detected_lang,
        min_confidence=pii_config["min_confidence"]
    )
    pii_entities = format_pii_entities(detected_entities, user_input)
    secrets_found = has_secrets(detected_entities)

    # Step 5: Final risk calculation
    # Base: max of rule and semantic scores
    # Add pii_weight if PII found, secret_weight if secrets found
    final_risk = max(rule_score, semantic_score)
    if detected_entities:
        final_risk += weights["pii_weight"]
    if secrets_found:
        final_risk += weights["secret_weight"]
    final_risk = round(min(final_risk, 1.0), 4)

    # Step 6: Policy decision + reason codes
    reason_codes = []

    if rule_score >= 0.60:
        reason_codes.append("RULE_INJECTION")
    if semantic_score >= thresholds["semantic_injection_threshold"]:
        reason_codes.append("SEMANTIC_INJECTION")
    if any(e["type"] in ["API_KEY", "JWT_TOKEN"] for e in pii_entities):
        reason_codes.append("SECRET_EXTRACTION")
    if any(e["type"] == "PAKISTAN_CNIC" for e in pii_entities):
        reason_codes.append("CNIC_DETECTED")
    if lang_info["was_translated"]:
        reason_codes.append(f"MULTILINGUAL_{detected_lang.upper()}")
    if detected_entities:
        reason_codes.append("PII_DETECTED")

    # Determine decision
    if final_risk >= thresholds["block_threshold"] or (
        rule_score >= 0.60 and semantic_score >= thresholds["semantic_injection_threshold"]
    ):
        decision = "BLOCK"
        safe_text = None
    elif detected_entities and final_risk >= thresholds["mask_threshold"]:
        decision = "MASK"
        safe_text = cleaned_text
    else:
        decision = "ALLOW"
        safe_text = user_input

    latency_ms = round((time.time() - start_time) * 1000, 2)

    result = {
        "input_id": input_id,
        "language": detected_lang,
        "rule_score": rule_score,
        "semantic_score": semantic_score,
        "pii_entities": pii_entities,
        "final_risk": final_risk,
        "decision": decision,
        "safe_text": safe_text,
        "reason_codes": reason_codes,
        "latency_ms": latency_ms
    }

    write_audit_log(result)
    return result