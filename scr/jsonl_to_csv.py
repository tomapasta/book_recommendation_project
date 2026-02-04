import json
import pandas as pd
from pathlib import Path

# ===== paths =====
INPUT_JSONL = Path("data/raw/goodreads_books.jsonl")
OUTPUT_CSV = Path("data/processed/goodreads_books.csv")

OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

rows = []

with INPUT_JSONL.open("r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))

df = pd.DataFrame(rows)

if "genres" in df.columns:
    df["genres"] = df["genres"].apply(
        lambda x: ", ".join(x) if isinstance(x, list) else x
    )

df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

print(f"Saved CSV to: {OUTPUT_CSV}")
print(f"Shape: {df.shape}")
print(df.head(3))