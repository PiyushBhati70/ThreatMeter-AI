
from datasets import load_dataset
from pathlib import Path
import pandas as pd

DATASET_NAME = "JinqiangDing/seven-phishing-email-datasets"

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("Loading dataset...")
ds = load_dataset(DATASET_NAME)

def prepare_split(split_name):
    data = ds[split_name]
    df = data.to_pandas()

    # Keep the actual email body and its original label.
    df = df[["text", "label", "dataset_name"]].copy()

    # Normalize text and remove empty bodies.
    df["text"] = df["text"].fillna("").astype(str).str.strip()
    df = df[df["text"] != ""]

    # Remove exact duplicate bodies within this split.
    df = df.drop_duplicates(subset=["text"])

    # Do not guess what numeric labels mean yet.
    df["label"] = df["label"].astype(int)

    output_file = OUTPUT_DIR / f"email_{split_name}.csv"
    df.to_csv(output_file, index=False, encoding="utf-8")

    print(f"\n{split_name.upper()}")
    print("Rows saved:", len(df))
    print("Label counts:")
    print(df["label"].value_counts().sort_index())
    print("Saved to:", output_file)

prepare_split("train")
prepare_split("test")

print("\nPreparation complete. Original dataset and model unchanged.")
