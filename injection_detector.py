<<<<<<< HEAD
=======
# This file checks if a user's message is a jailbreak or prompt injection attempt

>>>>>>> 236d651ce38f5e861f8db3a99d6c3b7c9c7ddb78
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
<<<<<<< HEAD
    user_input_lower = user_input.lower()

    for keyword in INJECTION_KEYWORDS:
        if keyword in user_input_lower:
            score += 1
=======
    user_input_lower = user_input.lower()  # converts to lowercase for  matching

    for keyword in INJECTION_KEYWORDS:
        if keyword in user_input_lower:
            score += 1  # adds 1 point for every suspicious word
>>>>>>> 236d651ce38f5e861f8db3a99d6c3b7c9c7ddb78

    return score
def is_injection(user_input, threshold=1):

    score = calculate_injection_score(user_input)
<<<<<<< HEAD
    return score >= threshold, score
=======
    return score >= threshold, score  
>>>>>>> 236d651ce38f5e861f8db3a99d6c3b7c9c7ddb78
