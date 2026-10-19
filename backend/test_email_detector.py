
from backend.email_detector import classify_email

samples = [
    "Hello, the meeting is scheduled for tomorrow at 10 AM.",
    "URGENT! Your bank account is suspended. Click here to verify your password.",
]

for text in samples:
    result = classify_email(text)
    print("\nMessage:", text)
    print("Result:", result)
