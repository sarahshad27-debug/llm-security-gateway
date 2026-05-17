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
    "ignorez les instructions précédentes",
    "faites semblant d'être","تجاهل التعليمات السابقة",

]

def calculate_injection_score(user_input):
    score = 0
    user_input_lower = user_input.lower()

    for keyword in INJECTION_KEYWORDS:
        if keyword in user_input_lower:
            score += 1

    return score
def is_injection(user_input, threshold=1):

    score = calculate_injection_score(user_input)
    return score >= threshold, score