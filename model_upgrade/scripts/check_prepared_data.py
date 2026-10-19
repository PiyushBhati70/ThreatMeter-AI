
from pathlib import Path
import pandas as pd

base = Path(__file__).resolve().parents[1]
folder = base / "data" / "processed"

for name in ["email_train.csv", "email_test.csv"]:
    path = folder / name

    print(f"\nChecking {name}...")

    if not path.exists():
        print("FILE NOT FOUND:", path)
        continue

    df = pd.read_csv(path)

    print("Rows:", len(df))
    print("Columns:", list(df.columns))
    print("Labels:", df["label"].value_counts().sort_index().to_dict())
    print("Empty messages:", df["text"].fillna("").str.strip().eq("").sum())
    print("Sample message:", repr(str(df.iloc[0]["text"])[:200]))

print("\nCheck complete. No model was changed.")
