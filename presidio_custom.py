

from presidio_analyzer import PatternRecognizer, Pattern

# 1. CNIC Detector
# Format: 35202-1234567-1
# ─────────────────────────────────────────
cnic_recognizer = PatternRecognizer(
    supported_entity="PAKISTAN_CNIC",
    patterns=[Pattern(
        name="cnic_pattern",
        regex=r"\b\d{5}-\d{7}-\d\b",
        score=0.9
    )]
)
# 2. City Detector
# Detects major cities
# ─────────────────────────────────────────
city_recognizer = PatternRecognizer(
    supported_entity="PAKISTAN_CITY",
    deny_list=[
        "Karachi", "Lahore", "Islamabad", "Rawalpindi",
        "Peshawar", "Quetta", "Multan", "Faisalabad",
        "Sialkot", "Gujranwala", "Hyderabad", "Abbottabad"
    ]
)

# 3. Salary / PKR Amount Detector
# Detects things like "Rs. 50,000" or "PKR 10000"
# ─────────────────────────────────────────
salary_recognizer = PatternRecognizer(
    supported_entity="PAKISTAN_SALARY",
    patterns=[Pattern(
        name="salary_pattern",
        regex=r"(Rs\.?\s?\d[\d,]*|PKR\s?\d[\d,]*)",
        score=0.85
    )]
)
# 4. Bank IBAN Detector
# Format: PK36SCBL0000001123456702
# ─────────────────────────────────────────
iban_recognizer = PatternRecognizer(
    supported_entity="PAKISTAN_IBAN",
    patterns=[Pattern(
        name="iban_pattern",
        regex=r"\bPK\d{2}[A-Z]{4}\d{16}\b",
        score=0.95
    )]
)
# 5. Educational Institute Detector
# Detects universities
# ─────────────────────────────────────────
institute_recognizer = PatternRecognizer(
    supported_entity="PAKISTAN_INSTITUTE",
    deny_list=[
        "FAST", "NUST", "COMSATS", "LUMS", "UET",
        "PIEAS", "IBA", "GCU", "PU", "QAU",
        "CIIT", "Air University", "Bahria University"
    ]
)
# 6. Student ID Detector
# Format: FA24-BCS-001
# ─────────────────────────────────────────
student_id_recognizer = PatternRecognizer(
    supported_entity="STUDENT_ID",
    patterns=[Pattern(
        name="student_id_pattern",
        regex=r"\b[A-Z]{2}\d{2}-[A-Z]{2,4}-\d{3}\b",
        score=0.9
    )]
)
# 7. API Key Detector
# Detects keys like sk-xxxx, pk_live_xxxx
# ─────────────────────────────────────────
api_key_recognizer = PatternRecognizer(
    supported_entity="API_KEY",
    patterns=[Pattern(
        name="api_key_pattern",
        regex=r"\b(sk-[a-zA-Z0-9]{20,}|pk_live_[a-zA-Z0-9]{20,}|api_key\s*=\s*['\"][a-zA-Z0-9]{10,}['\"])\b",
        score=0.95
    )]
)
# 8. JWT Token Detector
# JWT tokens always start with eyJ
# ─────────────────────────────────────────
jwt_recognizer = PatternRecognizer(
    supported_entity="JWT_TOKEN",
    patterns=[Pattern(
        name="jwt_pattern",
        regex=r"\beyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\b",
        score=0.97
    )]
)
# 9. Phone Number Detector
# Format: 0300-1234567 or +923001234567
# ─────────────────────────────────────────
phone_recognizer = PatternRecognizer(
    supported_entity="PAKISTAN_PHONE",
    patterns=[Pattern(
        name="phone_pattern",
        regex=r"(\+92|0)[0-9]{3}[-\s]?[0-9]{7}\b",
        score=0.9
    )]
)
# Exporting all recognizers as a list for easy access
# ─────────────────────────────────────────
all_custom_recognizers = [
    cnic_recognizer,
    city_recognizer,
    salary_recognizer,
    iban_recognizer,
    institute_recognizer,
    student_id_recognizer,
    api_key_recognizer,
    jwt_recognizer,
    phone_recognizer
]
