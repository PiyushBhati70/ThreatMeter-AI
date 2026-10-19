
import ipaddress
import math
import re
import joblib

from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


# Locate the saved model inside the backend folder.
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "url_model.joblib"

saved_model = joblib.load(MODEL_PATH)
model = saved_model["model"]
FEATURE_NAMES = saved_model["feature_names"]

# These labels must match the dataset's label meanings.
PHISHING_LABEL = 0
LEGITIMATE_LABEL = 1


def extract_features(url):
    """Extract the same 42 features used during training."""
    url = str(url).strip()

    if not url:
        url = " "

    parsed_url = (
        url
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url)
        else "//" + url
    )

    parsed = urlparse(parsed_url)
    host = (parsed.hostname or "").lower()
    path = parsed.path or ""
    query = parsed.query or ""
    lower_url = url.lower()

    is_ip = 0
    try:
        ipaddress.ip_address(host)
        is_ip = 1
    except ValueError:
        pass

    counts = Counter(url)
    entropy = 0.0
    total = max(len(url), 1)

    for count in counts.values():
        probability = count / total
        entropy -= probability * math.log2(probability)

    digit_count = sum(c.isdigit() for c in url)

    features = {
        "url_length": len(url),
        "hostname_length": len(host),
        "path_length": len(path),
        "query_length": len(query),
        "dot_count": url.count("."),
        "hyphen_count": url.count("-"),
        "underscore_count": url.count("_"),
        "slash_count": url.count("/"),
        "question_count": url.count("?"),
        "equal_count": url.count("="),
        "ampersand_count": url.count("&"),
        "at_count": url.count("@"),
        "percent_count": url.count("%"),
        "digit_count": digit_count,
        "letter_count": sum(c.isalpha() for c in url),
        "special_char_count": sum(not c.isalnum() for c in url),
        "digit_ratio": digit_count / total,
        "subdomain_dot_count": max(host.count(".") - 1, 0),
        "has_https": int(parsed.scheme.lower() == "https"),
        "has_ip_address": is_ip,
        "has_port": int(parsed.port is not None) if parsed.port else 0,
        "has_punycode": int("xn--" in host),
        "has_at_symbol": int("@" in url),
        "has_double_slash_in_path": int("//" in path),
        "has_encoded_chars": int("%" in url),
        "hostname_has_hyphen": int("-" in host),
        "character_entropy": entropy,
    }

    words = [
        "login", "verify", "account", "secure", "update",
        "password", "signin", "bank", "wallet", "confirm",
        "paypal", "webscr", "auth", "invoice", "support",
    ]

    for word in words:
        features["word_" + word] = int(word in lower_url)

    return features


def classify_url(url):
    """Return a model-estimated phishing risk for a URL."""
    if not isinstance(url, str):
        raise ValueError("URL must be text.")

    url = url.strip()

    if not url:
        raise ValueError("Please enter a URL.")

    if len(url) > 2048:
        raise ValueError("URL must be 2048 characters or fewer.")

    candidate = (
        url
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url)
        else "https://" + url
    )

    try:
        parsed = urlparse(candidate)
        host = parsed.hostname

        if (
            parsed.scheme.lower() not in ("http", "https")
            or not host
            or "." not in host
            or any(c.isspace() for c in url)
        ):
            raise ValueError(
                "Please enter a valid HTTP or HTTPS URL."
            )

        # Accessing port also checks for malformed port values.
        _ = parsed.port

    except ValueError as exc:
        raise ValueError("The URL format is invalid.") from exc

    features = extract_features(url)

    # Preserve the exact feature order expected by the saved model.
    row = [[features[name] for name in FEATURE_NAMES]]

    probabilities = model.predict_proba(row)[0]
    class_probabilities = dict(
        zip(model.classes_, probabilities)
    )

    phishing_probability = float(
        class_probabilities[PHISHING_LABEL]
    )
    legitimate_probability = float(
        class_probabilities[LEGITIMATE_LABEL]
    )

    risk_score = round(phishing_probability * 100)
    safety_score = round(legitimate_probability * 100)

    if risk_score >= 50:
        label = "phishing"
    else:
        label = "legitimate"

    return {
        "url": url,
        "label": label,
        "score": risk_score,
        "phishing_probability": phishing_probability,
        "legitimate_probability": legitimate_probability,
        "safety_score": safety_score,
        "model_type": "Random Forest",
        "explanation": (
            "This is a machine-learning estimate based on URL "
            "characteristics. It does not guarantee that a website "
            "is safe or malicious."
        ),
    }
