import os
import pandas as pd

BASE_DIR = "data"  # change if your dataset folder path differs

print(f"\n🔍 Scanning '{BASE_DIR}' for context-related columns...\n")
context_columns = ["ground", "venue", "opposition", "team", "against", "host_country"]

for root, _, files in os.walk(BASE_DIR):
    for file in files:
        if file.endswith(".csv"):
            file_path = os.path.join(root, file)
            try:
                df = pd.read_csv(file_path, nrows=5)
                cols = [c.lower() for c in df.columns]
                hits = [c for c in context_columns if any(c in col for col in cols)]
                if hits:
                    print(f"✅ {file_path}")
                    print(f"   → Columns found: {hits}\n")
            except Exception as e:
                print(f"⚠️ Could not read {file_path}: {e}")
