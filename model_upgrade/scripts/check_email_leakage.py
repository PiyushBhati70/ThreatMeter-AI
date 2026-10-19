
from pathlib import Path
import hashlib
import re
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "processed"

train = pd.read_csv(DATA_DIR / "email_train.csv")
test = pd.read_csv(DATA_DIR / "email_test.csv")


def normalize(text):
    text = str(text).lower()
    return re.sub(r"\s+", " ", text).strip()


def fingerprint(text):
    return hashlib.sha256(
        normalize(text).encode("utf-8")
    ).hexdigest()


train_hashes = train["text"].map(fingerprint)
test_hashes = test["text"].map(fingerprint)

overlap = set(train_hashes) & set(test_hashes)

print("=== EMAIL DATA LEAKAGE CHECK ===")
print("Training rows:", len(train))
print("Testing rows:", len(test))
print("Unique training message hashes:", train_hashes.nunique())
print("Unique test message hashes:", test_hashes.nunique())
print("Exact normalized messages appearing in both:", len(overlap))

if overlap:
    print(
        "WARNING: Exact duplicates exist across splits. "
        "Investigate before trusting the test score."
    )
else:
    print(
        "No exact normalized duplicates found across splits. "
        "Near-duplicates and source leakage still need checking."
    )

print("\nDataset sources in training:")
print(train["dataset_name"].value_counts(dropna=False))

print("\nDataset sources in testing:")
print(test["dataset_name"].value_counts(dropna=False))
