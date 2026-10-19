
from pathlib import Path
import joblib
import pandas as pd

from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    accuracy_score,
)

ROOT = Path(__file__).resolve().parent

MODEL_PATH = (
    ROOT / "model_upgrade" / "models"
    / "threatmeter_email_model_clean_v1.joblib"
)
TEST_PATH = (
    ROOT / "model_upgrade" / "data" / "processed"
    / "email_test_clean.csv"
)

print("Loading model and test data...")
model = joblib.load(MODEL_PATH)
df = pd.read_csv(TEST_PATH).dropna(subset=["text", "label"])

X = df["text"].astype(str)
y = df["label"].astype(int)

# According to the training script: 1 = phishing, 0 = legitimate.
predictions = model.predict(X)
classes = list(model.classes_)
phishing_index = classes.index(1)
probabilities = model.predict_proba(X)[:, phishing_index]

print("\nTest rows:", len(df))
print("Label counts:")
print(y.value_counts().sort_index())

print("\nAccuracy:", round(accuracy_score(y, predictions), 4))
print("\nClassification report:")
print(classification_report(
    y, predictions,
    labels=[0, 1],
    target_names=["legitimate", "phishing"],
    digits=4,
    zero_division=0,
))

print("Confusion matrix (true rows, predicted columns):")
print(confusion_matrix(y, predictions, labels=[0, 1]))

# False negatives: actual phishing predicted as legitimate.
missed = df.loc[
    (y == 1) & (predictions == 0),
    ["text", "label"]
].copy()

missed["phishing_probability"] = probabilities[
    (y.to_numpy() == 1) & (predictions == 0)
]

print("\nMissed phishing emails:", len(missed))
print("\nFirst 10 false negatives:")
for _, row in missed.head(10).iterrows():
    print("\nProbability:", round(row["phishing_probability"], 4))
    print("Text:", str(row["text"])[:700])

# Save all false negatives for review.
output_path = ROOT / "email_false_negatives.csv"
missed.to_csv(output_path, index=False)
print("\nAll false negatives saved to:", output_path)
