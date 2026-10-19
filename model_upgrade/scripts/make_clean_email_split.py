
from pathlib import Path
import re
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "processed"

train_path = DATA_DIR / "email_train.csv"
test_path = DATA_DIR / "email_test.csv"

train = pd.read_csv(train_path)
test = pd.read_csv(test_path)


def normalize(text):
    text = str(text).lower()
    return re.sub(r"\s+", " ", text).strip()


# Keep test examples and remove matching bodies from training.
test_keys = set(test["text"].map(normalize))
train_keys = train["text"].map(normalize)

overlap_mask = train_keys.isin(test_keys)
removed = int(overlap_mask.sum())
clean_train = train.loc[~overlap_mask].copy()

print("Original training rows:", len(train))
print("Test rows:", len(test))
print("Training rows removed due to test overlap:", removed)
print("Clean training rows:", len(clean_train))

# Save separate files. Do not overwrite the original datasets.
clean_train_path = DATA_DIR / "email_train_clean.csv"
clean_test_path = DATA_DIR / "email_test_clean.csv"

clean_train.to_csv(clean_train_path, index=False)
test.to_csv(clean_test_path, index=False)

print("\nSaved:")
print(clean_train_path)
print(clean_test_path)
print("\nOriginal CSV files were not changed.")
