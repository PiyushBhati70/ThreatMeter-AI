
from datasets import load_dataset
from collections import Counter

name = "JinqiangDing/seven-phishing-email-datasets"

print("Loading email dataset...")
ds = load_dataset(name)

print("\nDataset splits:")
print(ds)

for split_name, data in ds.items():
    print(f"\nSplit: {split_name}")
    print("Rows:", len(data))
    print("Columns:", data.column_names)

    if "label" in data.column_names:
        print("Label distribution:", Counter(data["label"]))

    if "text" in data.column_names:
        print("\nExample email body:")
        for text in data["text"][:3]:
            print(repr((text or "")[:500]))

    break
