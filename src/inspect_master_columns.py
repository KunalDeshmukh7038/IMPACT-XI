# src/inspect_master_columns.py
import pandas as pd
import os

MASTER_DIR = "outputs/cleaned_data"
FORMATS = ["odi", "t20", "test"]

print(f"🔍 Inspecting master datasets in: {MASTER_DIR}\n")

for fmt in FORMATS:
    path = os.path.join(MASTER_DIR, f"{fmt}_master.csv")

    if not os.path.exists(path):
        print(f"❌ {fmt.upper()} file not found: {path}\n")
        continue

    print(f"\n🏏 {fmt.upper()} MASTER FILE")
    print("=" * 60)
    df = pd.read_csv(path)

    print(f"📄 Shape: {df.shape}")
    print("📋 Columns:")
    print(df.columns.tolist())

    print("\n🔹 Sample Rows (first 3):")
    print(df.head(3).to_string(index=False))

    print("\n" + "-" * 60)
