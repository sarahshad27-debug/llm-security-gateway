import requests

tests = [
    ("CNIC", "my cnic is 35202-1234567-1"),
    ("City", "I live in Rawalpindi"),
    ("Salary", "my salary is Rs. 85,000"),
    ("IBAN", "my bank account is PK36SCBL0000001123456702"),
    ("Institute", "I study at COMSATS"),
    ("Student ID", "my id is FA24-BCS-001"),
    ("API Key", "my key is sk-abcdefghijklmnopqrstuvwxyz123456"),
    ("JWT", "token: eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyIn0.abc123"),
    ("Phone", "call me at 0300-1234567"),
]

for name, message in tests:
    response = requests.post(
        "http://127.0.0.1:5000/check",
        json={"message": message}
    )
    data = response.json()
    print(f"Test - {name}:")
    print(f"  Decision : {data['decision']}")
    print(f"  Cleaned  : {data['cleaned_input']}")
    print()