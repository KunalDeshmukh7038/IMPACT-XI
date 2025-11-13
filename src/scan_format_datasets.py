import os
import pandas as pd

def scan_for_formats(base_dir="data"):
    results = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith(".csv"):
                file_path = os.path.join(root, file)
                lower_name = file.lower()
                if "t20" in lower_name:
                    file_type = "T20"
                elif "test" in lower_name:
                    file_type = "Test"
                elif "odi" in lower_name:
                    file_type = "ODI"
                else:
                    file_type = "Other"
                results.append({"Folder": root, "File": file, "Format": file_type})
    
    if results:
        df = pd.DataFrame(results)
        print("\n📊 CSV Files Found in 'data' Folder:\n")
        print(df.to_string(index=False))
    else:
        print(f"⚠️ No CSV files found inside '{base_dir}'.")

if __name__ == "__main__":
    base_dir = "data"
    print(f"🔍 Scanning for T20/Test/ODI datasets in: {base_dir}\n")
    scan_for_formats(base_dir)
