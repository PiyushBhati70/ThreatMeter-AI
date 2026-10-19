
from pathlib import Path
import joblib

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "models" / "threatmeter_email_model_clean_v1.joblib"

print("Loading clean email model...")
model = joblib.load(MODEL_PATH)

samples = [
    "Hello, the meeting is scheduled for tomorrow at 10 AM. Please review the attached agenda.",
    "URGENT! Your bank account has been suspended. Click here immediately to verify your password and restore access.",
    "Hi team, please find the project report attached. Let me know if you need any changes.",
    "Congratulations! You have won a prize. Send your bank details now to claim your reward.",
]

print("\n=== CLEAN MODEL PREDICTIONS ===")

for text in samples:
    prediction = int(model.predict([text])[0])
    probabilities = model.predict_proba([text])[0]
    phishing_index = list(model.classes_).index(1)
    phishing_probability = float(probabilities[phishing_index])

    label = "PHISHING" if prediction == 1 else "LEGITIMATE"

    print("\nMessage:", text)
    print("Prediction:", label)
    print(f"Phishing probability: {phishing_probability:.2%}")

print("\nClean model loaded and tested successfully.")
