# src/analyze_context_data_v2.py
import os
import pandas as pd

SEARCH_TERMS = ["ground", "venue", "stadium", "opponent", "against", "team", "match", "location"]

def scan_for_context_data(base_dir="data"):
    print(f"\n🔍 Scanning '{base_dir}' for context-related columns...\n")

    found = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_csv(file_path, nrows=3)
                    cols = [c for c in df.columns if any(term in c.lower() for term in SEARCH_TERMS)]
                    if cols:
                        print(f"✅ {file_path}\n   → Columns found: {cols}\n")
                        found.append((file_path, cols))
                except Exception as e:
                    print(f"⚠️ Could not read {file_path}: {e}")

    if not found:
        print("❌ No venue/opponent columns found in any CSVs.")
    else:
        print(f"\n✅ Found {len(found)} relevant files.")
    return found


if __name__ == "__main__":
    scan_for_context_data()
