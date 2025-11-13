import os
import pandas as pd

BASE_DIR = "data"

print(f"🔍 Scanning for CSV column names in '{BASE_DIR}'...\n")

for root, _, files in os.walk(BASE_DIR):
    for file in files:
        if file.endswith(".csv") and ("t20" in file.lower() or "test" in file.lower()):
            path = os.path.join(root, file)
            try:
                df = pd.read_csv(path, nrows=2)
                print(f"📘 {file} → Columns: {list(df.columns)}")
            except Exception as e:
                print(f"⚠️ Could not read {file}: {e}")

print("\n✅ Done scanning!")
