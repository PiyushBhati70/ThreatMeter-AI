
from backend.url_detector import classify_url

test_urls = [
    "https://www.google.com",
    "https://www.wikipedia.org",
    "http://paypal.com.security-check.example/",
    "http://192.0.2.1/login/verify",
]

for url in test_urls:
    try:
        result = classify_url(url)
        print("\nURL:", url)
        print("Label:", result["label"])
        print("Phishing probability:", result["phishing_probability"])
        print("Risk score:", result["score"])
    except Exception as exc:
        print("\nURL:", url)
        print("ERROR:", exc)
