import pandas as pd
import os

def compare_columns(base_file, compare_files):
    print(f"✅ Base file: {base_file}\n")

    # Load base dataset
    base_df = pd.read_csv(base_file)
    base_cols = set(base_df.columns)

    for file in compare_files:
        if not os.path.exists(file):
            print(f"❌ File not found: {file}")
            continue

        print(f"\n📄 Comparing with: {file}")
        df = pd.read_csv(file)
        cols = set(df.columns)

        common = base_cols.intersection(cols)
        only_in_base = base_cols - cols
        only_in_other = cols - base_cols

        print(f"✅ Common columns ({len(common)}): {sorted(common)}")
        print(f"➕ Columns only in {os.path.basename(file)} ({len(only_in_other)}): {sorted(only_in_other)}")
        print(f"➖ Columns only in base file ({len(only_in_base)}): {sorted(only_in_base)}")
        print("-" * 80)

def main():
    base_file = "outputs/cleaned_data/odi_master.csv"
    compare_files = [
        "data/Batting/ODI_data.csv",
        "data/Bowling/Bowling_ODI.csv",
        "data/kaggle_datasets/ODI_batting.csv",
        "data/kaggle_datasets/ODI_bowling.csv",
        "data/kaggle_datasets/cricketers.csv",
        "data/kaggle_datasets/ODI_all_round.csv"

    ]

    compare_columns(base_file, compare_files)

if __name__ == "__main__":
    main()
