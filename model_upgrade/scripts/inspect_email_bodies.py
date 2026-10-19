
from datasets import load_dataset
from collections import Counter

name = "JinqiangDing/seven-phishing-email-datasets"
ds = load_dataset(name)

print("TRAIN LABEL COUNTS:")
print(Counter(ds["train"]["label"]))

print("\nTEST LABEL COUNTS:")
print(Counter(ds["test"]["label"]))

print("\nSAMPLE ROWS:")
for i in range(5):
    row = ds["train"][i]
    print("\nLabel:", row["label"])
    print("Subject:", repr(row["subject"]))
    print("Body:", repr((row["text"] or "")[:250]))
    print("Source:", row["dataset_name"])

print("\nEMPTY BODY CHECK:")
for split_name in ["train", "test"]:
    data = ds[split_name]
    empty = sum(
        not (text or "").strip()
        for text in data["text"]
    )
    print(split_name, "empty bodies:", empty, "/", len(data))

print("\n=== LABEL FEATURE INFORMATION ===")
print(ds["train"].features["label"])

print("\n=== DATASET DESCRIPTION ===")
print(ds["train"].info.description)