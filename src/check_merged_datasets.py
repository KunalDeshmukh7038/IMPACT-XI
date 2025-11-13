# src/check_merged_datasets.py
import os
import pandas as pd

merged_info = {}
base_path = "outputs/cleaned_data"

for fmt in ["odi", "t20", "test"]:
    bat_path = os.path.join(base_path, f"{fmt}_batting_merged.csv")
    bowl_path = os.path.join(base_path, f"{fmt}_bowling_merged.csv")
    merged_info[fmt.upper()] = {"Batting": os.path.exists(bat_path), "Bowling": os.path.exists(bowl_path)}

print("\n🔍 Checking merged datasets availability...\n")
for fmt, status in merged_info.items():
    print(f"{fmt} → Batting: {'✅' if status['Batting'] else '❌'}, Bowling: {'✅' if status['Bowling'] else '❌'}")

print("\nDetailed column check for available files:\n")
for fmt in ["odi", "t20", "test"]:
    for kind in ["batting", "bowling"]:
        path = os.path.join(base_path, f"{fmt}_{kind}_merged.csv")
        if os.path.exists(path):
            df = pd.read_csv(path, nrows=3)
            print(f"{fmt.upper()} {kind.title()} Columns → {list(df.columns)}\n")
