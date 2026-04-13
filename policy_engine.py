from injection_detector import is_injection
from pii_handler import anonymize_pii

INJECTION_THRESHOLD = 1  
PII_MASK = True           

def process_input(user_input):
    """
    Main function — takes user input and returns a policy decision.
    """

    result = {
        "original_input": user_input,
        "decision": None,        # ALLOW / MASK / BLOCK
        "cleaned_input": None,
        "injection_score": 0,    # how suspicious was it
        "pii_found": [],         # what PII was detected
        "reason": ""             # explanation of the decision
    }

    #  Check for injection/jailbreak
    injected, score = is_injection(user_input, threshold=INJECTION_THRESHOLD)
    result["injection_score"] = score

    if injected:
        result["decision"] = "BLOCK"
        result["reason"] = "Prompt injection or jailbreak attempt detected"
        result["cleaned_input"] = None
        return result

    #Check for PII
    cleaned_text, pii_found = anonymize_pii(user_input)
    result["pii_found"] = [str(p) for p in pii_found]

    if pii_found and PII_MASK:
        result["decision"] = "MASK"
        result["reason"] = "PII detected and masked"
        result["cleaned_input"] = cleaned_text
        return result

    # If All is clear, allow the input
    result["decision"] = "ALLOW"
    result["reason"] = "Input is clean"
    result["cleaned_input"] = user_input
    return result
