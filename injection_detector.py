# This file checks if a user's message is a jailbreak or prompt injection attempt

INJECTION_KEYWORDS = [
    "ignore previous instructions",
    "forget your rules",
    "you are now",
    "pretend you are",
    "act as",
    "jailbreak",
    "bypass",
    "do anything now",
    "dan mode",
    "ignore all instructions",
]

def calculate_injection_score(user_input):
    """
    Gives a score based on how suspicious the input looks.
    Higher score = more dangerous.
    """
    score = 0
    user_input_lower = user_input.lower()  # converts to lowercase for  matching

    for keyword in INJECTION_KEYWORDS:
        if keyword in user_input_lower:
            score += 1  # adds 1 point for every suspicious word

    return score


def is_injection(user_input, threshold=1):
    """
    Returns True if the message looks like an attack.
    Threshold = how many suspicious phrases before we block.
    """
    score = calculate_injection_score(user_input)
    return score >= threshold, score  
