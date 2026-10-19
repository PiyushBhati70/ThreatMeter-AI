
from pathlib import Path
import joblib

# Project root is the parent of the backend folder.
PROJECT_DIR = Path(__file__).resolve().parent.parent

MODEL_FILE = (
    PROJECT_DIR
    / "model_upgrade"
    / "models"
    / "threatmeter_email_model_clean_v1.joblib"
)


def load_model():
    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            f"Email model not found: {MODEL_FILE}"
        )
    return joblib.load(MODEL_FILE)


model = load_model()


def classify_email(text: str) -> dict:
    if not isinstance(text, str):
        raise TypeError("Email text must be a string.")

    text = text.strip()

    if not text:
        raise ValueError("Please enter email text.")

    prediction = int(model.predict([text])[0])
    probabilities = model.predict_proba([text])[0]
    
    
    classes = list(model.classes_)
    print("EMAIL MODEL CLASS MAPPING:", classes)
    print("EMAIL DEBUG - Model classes:", classes)
    print("EMAIL DEBUG - Predicted class:", prediction)
    print("EMAIL DEBUG - Probabilities:", probabilities.tolist())

    phishing_index = classes.index(1)
    phishing_probability = float(probabilities[phishing_index])

    print("EMAIL DEBUG - Phishing probability:", phishing_probability)


    if phishing_probability >= 0.80:
        confidence = "High"
    elif phishing_probability >= 0.60:
        confidence = "Medium"
    else:
        confidence = "Low"

    if prediction == 1:
        label = "phishing"
        explanation = (
            "The email text resembles patterns associated "
            "with phishing messages."
        )
    else:
        label = "legitimate"
        explanation = (
            "The email text resembles patterns associated "
            "with legitimate messages."
        )

    return {
        "label": label,
        "score": round(phishing_probability * 100, 2),
        "phishing_probability": phishing_probability,
        "confidence": confidence,
        "explanation": explanation,
    }
