
from pathlib import Path

import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    confusion_matrix,
    ConfusionMatrixDisplay,
    precision_recall_curve,
    average_precision_score,
    classification_report,
)

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data" / "processed"
MODELS = BASE / "models"
REPORTS = BASE / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

model_path = MODELS / "threatmeter_email_model_v1.joblib"
train_path = DATA / "email_train.csv"
test_path = DATA / "email_test.csv"

for path in [model_path, train_path, test_path]:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

print("Loading model and datasets...")
model = joblib.load(model_path)
train = pd.read_csv(train_path)
test = pd.read_csv(test_path)

X_test = test["text"].fillna("").astype(str)
y_test = test["label"].astype(int)

print("Generating predictions...")
pred = model.predict(X_test)
probabilities = model.predict_proba(X_test)

classes = list(model.classes_)
phishing_index = classes.index(1)
phishing_prob = probabilities[:, phishing_index]

# 1. Confusion matrix heatmap
cm = confusion_matrix(y_test, pred, labels=[0, 1])
display = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=["Legitimate", "Phishing"],
)
display.plot(cmap="Blues", values_format="d")
plt.title("ThreatMeter Email Model - Confusion Matrix")
plt.tight_layout()
plt.savefig(REPORTS / "confusion_matrix.png", dpi=200)
plt.close()

# 2. Precision-recall curve
precision, recall, _ = precision_recall_curve(
    y_test, phishing_prob, pos_label=1
)
ap = average_precision_score(y_test, phishing_prob)

plt.figure(figsize=(8, 5))
plt.plot(recall, precision, label=f"Average precision = {ap:.4f}")
plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Phishing Precision-Recall Curve")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(REPORTS / "precision_recall_curve.png", dpi=200)
plt.close()

# 3. Dataset class distribution
fig, axes = plt.subplots(1, 2, figsize=(11, 5))

for ax, frame, title in [
    (axes[0], train, "Training Dataset"),
    (axes[1], test, "Test Dataset"),
]:
    counts = frame["label"].value_counts().reindex(
        [0, 1], fill_value=0
    )
    bars = ax.bar(
        ["Legitimate (0)", "Phishing (1)"],
        counts.values,
    )
    ax.bar_label(bars, fmt="%.0f")
    ax.set_title(title)
    ax.set_ylabel("Number of messages")
    ax.tick_params(axis="x", rotation=12)

fig.suptitle("ThreatMeter Email Dataset Distribution")
fig.tight_layout()
fig.savefig(REPORTS / "dataset_distribution.png", dpi=200)
plt.close(fig)

# 4. Export incorrect predictions
error_mask = pred != y_test.to_numpy()
errors = test.loc[
    error_mask, ["text", "label", "dataset_name"]
].copy()

errors["predicted_label"] = pred[error_mask]
errors["phishing_probability"] = phishing_prob[error_mask]

errors.to_csv(
    REPORTS / "misclassified_examples.csv",
    index=False,
    encoding="utf-8",
)

# 5. Save classification report
report = classification_report(
    y_test,
    pred,
    labels=[0, 1],
    target_names=["Legitimate", "Phishing"],
    digits=4,
    zero_division=0,
)

(REPORTS / "classification_report.txt").write_text(
    report, encoding="utf-8"
)

print("\n=== GRAPHICS AND REPORTS CREATED ===")
for filename in [
    "confusion_matrix.png",
    "precision_recall_curve.png",
    "dataset_distribution.png",
    "misclassified_examples.csv",
    "classification_report.txt",
]:
    print(REPORTS / filename)

print("\nAverage precision:", round(ap, 4))
print("Misclassified messages:", int(error_mask.sum()))
print("\nDone! Your original model and frontend were not changed.")
