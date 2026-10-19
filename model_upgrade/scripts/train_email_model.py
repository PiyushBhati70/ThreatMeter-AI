
from pathlib import Path
import json
import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
)
from sklearn.pipeline import Pipeline

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "processed"
MODEL_DIR = BASE_DIR / "models"
REPORT_DIR = BASE_DIR / "reports"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

train_path = DATA_DIR / "email_train.csv"
test_path = DATA_DIR / "email_test.csv"

print("Loading prepared email data...")
train_df = pd.read_csv(train_path).dropna(subset=["text", "label"])
test_df = pd.read_csv(test_path).dropna(subset=["text", "label"])

X_train = train_df["text"].astype(str)
y_train = train_df["label"].astype(int)
X_test = test_df["text"].astype(str)
y_test = test_df["label"].astype(int)

print("Training rows:", len(X_train))
print("Test rows:", len(X_test))

# Dataset mapping: 0 = legitimate, 1 = phishing/spam.
model = Pipeline([
    ("tfidf", TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        max_features=200_000,
        sublinear_tf=True,
        min_df=2,
    )),
    ("classifier", LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42,
    )),
])

print("\nTraining new email model...")
model.fit(X_train, y_train)

print("\nEvaluating on the held-out email test set...")
predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)
report = classification_report(
    y_test,
    predictions,
    labels=[0, 1],
    target_names=["legitimate", "phishing"],
    digits=4,
    zero_division=0,
)
matrix = confusion_matrix(y_test, predictions, labels=[0, 1])

model_path = MODEL_DIR / "threatmeter_email_model_v1.joblib"
report_path = REPORT_DIR / "email_model_report.txt"
metrics_path = REPORT_DIR / "email_model_metrics.json"

joblib.dump(model, model_path)

report_text = (
    f"Accuracy: {accuracy:.4f}\n\n"
    f"Confusion matrix (true rows, predicted columns):\n{matrix}\n\n"
    f"{report}"
)

report_path.write_text(report_text, encoding="utf-8")
metrics_path.write_text(
    json.dumps({"accuracy": accuracy}, indent=2),
    encoding="utf-8",
)

print("\n=== RESULTS ===")
print(report_text)
print("\nNew model saved to:", model_path)
print("Report saved to:", report_path)
print("\nExisting ThreatMeter model was not modified.")
