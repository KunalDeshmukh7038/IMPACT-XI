import os
import pandas as pd

# Root folder where all your data is stored
DATA_ROOT = "data"   # <- change this if your folder name is different

def inspect_csv(file_path):
    """Print basic info and sample rows for a CSV file"""
    try:
        df = pd.read_csv(file_path, low_memory=False)
    except Exception as e:
        print(f"❌ Could not read {file_path}: {e}")
        return

    print(f"\n📂 File: {file_path}")
    print(f"   Shape: {df.shape[0]} rows × {df.shape[1]} cols")
    print(f"   Columns: {list(df.columns)}")

    # Show first 5 rows
    print("\n   Sample rows:")
    print(df.head(5).to_string(index=False))

def main():
    print(f"🔎 Scanning folder: {DATA_ROOT}\n")

    for root, _, files in os.walk(DATA_ROOT):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                inspect_csv(file_path)

if __name__ == "__main__":
    main()
