# src/scan_datasets.py
import os
import pandas as pd

def scan_csv_files(base_dir="data/kaggle_datasets"):
    summary = []

    print(f"🔍 Scanning directory: {base_dir}\n")

    # Walk through all subfolders recursively
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith(".csv"):
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_csv(file_path, nrows=5)  # Read only first 5 rows for speed
                    info = {
                        "File": file,
                        "Path": file_path,
                        "Rows (approx)": sum(1 for _ in open(file_path, encoding="utf-8")) - 1,
                        "Columns": len(df.columns),
                        "Column Names": list(df.columns)
                    }
                    summary.append(info)
                    print(f"✅ Found: {file}")
                    print(f"   Rows: {info['Rows (approx)']}, Columns: {info['Columns']}")
                    print(f"   Columns: {', '.join(df.columns[:6])} ...\n")
                except Exception as e:
                    print(f"⚠️ Could not read {file}: {e}\n")

    if not summary:
        print("⚠️ No CSV files found in this directory.")
    else:
        print(f"\n📊 Summary: Found {len(summary)} CSV files total.")

    # Save summary for reference
    if summary:
        summary_df = pd.DataFrame(summary)
        os.makedirs("outputs/logs", exist_ok=True)
        summary_df.to_csv("outputs/logs/dataset_scan_summary.csv", index=False)
        print("\n💾 Summary saved to outputs/logs/dataset_scan_summary.csv")

if __name__ == "__main__":
    scan_csv_files("kaggle_dataset")
