from pathlib import Path
import joblib

try:
    from .database import initialize_database, save_analysis
except ImportError:
    from database import initialize_database, save_analysis

BASE_DIR = Path(__file__).resolve().parent
MODEL_FILE = BASE_DIR / "sms_message_model.joblib"


def load_model():
    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            f"SMS model not found: {MODEL_FILE}\n"
            "Run python train_model.py first."
        )
    return joblib.load(MODEL_FILE)


model = load_model()


def classify_message(message):
    if not isinstance(message, str):
        raise TypeError("Message must be text.")

    message = message.strip()

    if not message:
        raise ValueError("Please enter a message.")

    prediction = model.predict([message])[0]
    probabilities = model.predict_proba([message])[0]
    classes = list(model.classes_)

    # Probability of spam, regardless of the predicted class
    spam_index = classes.index("spam")
    spam_probability = float(probabilities[spam_index])

    score = float(
        probabilities[classes.index(prediction)]
    ) * 100

    if score >= 80:
        confidence = "High"
    elif score >= 60:
        confidence = "Medium"
    else:
        confidence = "Low"

    if prediction == "spam":
        explanation = (
            "This SMS resembles patterns found in spam messages."
        )
    else:
        explanation = (
            "This SMS resembles patterns found in legitimate messages."
        )

    return {
        "label": str(prediction),
        "score": round(score, 2),
        "spam_probability": spam_probability,
        "confidence": confidence,
        "explanation": explanation
    }


def main():
    initialize_database()

    print("\n=== THREATMETER SMS DETECTOR ===")
    print("Enter an SMS to check whether it may be spam.")
    print("Type 'exit' to close.\n")

    while True:
        try:
            message = input("Enter SMS: ").strip()

            if message.lower() == "exit":
                print("Thank you for using ThreatMeter!")
                break

            if not message:
                print("Please enter a message.\n")
                continue

            result = classify_message(message)

            try:
                save_analysis(message, result)
                saved = True
            except Exception as error:
                saved = False
                print("Database save warning:", error)

            print("\n--- ANALYSIS RESULT ---")
            print(f"Classification: {result['label'].upper()}")
            print(f"Model confidence: {result['score']}%")
            print(
                f"Estimated spam probability: "
                f"{result['spam_probability'] * 100:.2f}%"
            )
            print(f"Confidence level: {result['confidence']}")
            print(f"Explanation: {result['explanation']}")

            if saved:
                print("Analysis saved to database.")

            print("-----------------------\n")

        except (ValueError, TypeError) as error:
            print("Input error:", error, "\n")
        except KeyboardInterrupt:
            print("\nThreatMeter stopped.")
            break


if __name__ == "__main__":
    main()
