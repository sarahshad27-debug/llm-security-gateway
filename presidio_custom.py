from presidio_analyzer import PatternRecognizer, Pattern, RecognizerResult

# 1. CNIC
# Format: 35202-1234567-1
cnic_recognizer = PatternRecognizer(
    supported_entity="PAKISTAN_CNIC",
    patterns=[Pattern(
        name="cnic_pattern",
        regex=r"\b\d{5}-\d{7}-\d\b",
        score=0.9
    )],
    context=["cnic", "national identity", "identity card", "ID card", "NIC"]
)

# 2. Pakistani Phone
# Format: 0300-1234567 or +923001234567
phone_recognizer = PatternRecognizer(
    supported_entity="PAKISTAN_PHONE",
    patterns=[Pattern(
        name="phone_pattern",
        regex=r"(\+92|0)[0-9]{3}[-\s]?[0-9]{7}\b",
        score=0.9
    )],
    context=["phone", "call", "mobile", "contact", "number", "whatsapp"]
)

# 3. Student ID
# Format: FA24-BCS-001
student_id_recognizer = PatternRecognizer(
    supported_entity="STUDENT_ID",
    patterns=[Pattern(
        name="student_id_pattern",
        regex=r"\b[A-Z]{2}\d{2}-[A-Z]{2,4}-\d{3}\b",
        score=0.85
    )],
    context=["student ID", "registration", "reg no", "student number", "roll number", "ID is", "ID:"]
)

# 4. API Key
# Detects: sk-xxxx, pk_live_xxxx, generic api_key=, Bearer tokens
api_key_recognizer = PatternRecognizer(
    supported_entity="API_KEY",
    patterns=[
        Pattern(name="sk_key",       regex=r"\bsk-[a-zA-Z0-9]{20,}\b",                               score=0.95),
        Pattern(name="pk_live_key",  regex=r"\bpk_live_[a-zA-Z0-9]{20,}\b",                          score=0.95),
        Pattern(name="generic_key",  regex=r"api[_\s]?key\s*[=:]\s*['\"]?[a-zA-Z0-9\-_]{10,}['\"]?", score=0.90),
        Pattern(name="bearer_token", regex=r"Bearer\s+[a-zA-Z0-9\-._~+/]{20,}",                      score=0.90),
    ],
    context=["API key", "key", "token", "secret", "credential", "authorization", "auth"]
)

# 5. JWT Token
# JWT tokens always start with eyJ
jwt_recognizer = PatternRecognizer(
    supported_entity="JWT_TOKEN",
    patterns=[Pattern(
        name="jwt_pattern",
        regex=r"\beyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\b",
        score=0.97
    )],
    context=["token", "JWT", "authorization", "bearer", "auth"]
)

# 6. Pakistani Bank IBAN
# Format: PK36SCBL0000001123456702
iban_recognizer = PatternRecognizer(
    supported_entity="PAKISTAN_IBAN",
    patterns=[Pattern(
        name="iban_pattern",
        regex=r"\bPK\d{2}[A-Z]{4}\d{16}\b",
        score=0.95
    )],
    context=["IBAN", "bank account", "account number", "transfer"]
)

# 7. PKR Salary / Amount
# Detects: Rs. 50,000 or PKR 10000
salary_recognizer = PatternRecognizer(
    supported_entity="PAKISTAN_SALARY",
    patterns=[Pattern(
        name="salary_pattern",
        regex=r"(Rs\.?\s?\d[\d,]*|PKR\s?\d[\d,]*)",
        score=0.85
    )],
    context=["salary", "income", "pay", "earn", "payment", "amount", "wage"]
)

# 8. Pakistani Cities
city_recognizer = PatternRecognizer(
    supported_entity="PAKISTAN_CITY",
    deny_list=[
        "Karachi", "Lahore", "Islamabad", "Rawalpindi",
        "Peshawar", "Quetta", "Multan", "Faisalabad",
        "Sialkot", "Gujranwala", "Hyderabad", "Abbottabad",
        "Wah", "Attock", "Taxila", "Chakwal"
    ]
)

# 9. Pakistani Passport
# Format: AB-123456789
passport_recognizer = PatternRecognizer(
    supported_entity="PAKISTAN_PASSPORT",
    patterns=[Pattern(
        name="passport_pattern",
        regex=r"\b[A-Z]{2}-\d{9}\b",
        score=0.9
    )],
    context=["passport", "travel document", "passport number"]
)

# 10. Pakistani Universities / Institutes
institute_recognizer = PatternRecognizer(
    supported_entity="PAKISTAN_INSTITUTE",
    deny_list=[
        "FAST", "NUST", "COMSATS", "LUMS", "UET",
        "PIEAS", "IBA", "GCU", "PU", "QAU",
        "CIIT", "Air University", "Bahria University"
    ]
)


# All recognizers list (imported by pii_handler.py)
all_custom_recognizers = [
    cnic_recognizer,
    phone_recognizer,
    student_id_recognizer,
    api_key_recognizer,
    jwt_recognizer,
    iban_recognizer,
    salary_recognizer,
    city_recognizer,
    passport_recognizer,
    institute_recognizer,
]


# Context-Aware Score Booster
# Boosts confidence when context keywords appear near a detected entity.
# Called by pii_handler.py after initial Presidio detection.

CONTEXT_BOOST_MAP = {
    "PAKISTAN_CNIC":     (["cnic", "national id", "identity card", "nic number"],  0.10),
    "STUDENT_ID":        (["student id", "registration", "reg no", "roll number"], 0.10),
    "API_KEY":           (["api key", "secret key", "token", "credential", "auth"], 0.05),
    "PAKISTAN_PHONE":    (["phone", "mobile", "contact", "call me", "whatsapp"],   0.08),
    "PAKISTAN_IBAN":     (["iban", "bank account", "account number"],              0.08),
    "JWT_TOKEN":         (["jwt", "bearer", "token", "auth"],                      0.05),
    "PAKISTAN_SALARY":   (["salary", "income", "pay", "earn", "wage"],             0.05),
    "PAKISTAN_PASSPORT": (["passport", "travel document"],                         0.08),
}


def apply_context_boost(text: str, results: list) -> list:
    text_lower = text.lower()
    boosted = []

    for result in results:
        boost = 0.0
        if result.entity_type in CONTEXT_BOOST_MAP:
            context_words, boost_amount = CONTEXT_BOOST_MAP[result.entity_type]
            for word in context_words:
                if word in text_lower:
                    boost = boost_amount
                    break

        boosted.append(RecognizerResult(
            entity_type=result.entity_type,
            start=result.start,
            end=result.end,
            score=min(1.0, result.score + boost)
        ))

    return boosted