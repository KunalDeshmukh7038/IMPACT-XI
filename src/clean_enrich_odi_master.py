# src/clean_enrich_odi_master.py
import pandas as pd
import os
import re
from fuzzywuzzy import process
from tqdm import tqdm

tqdm.pandas()

# ----------------------------------
# 🔹 Helper Functions
# ----------------------------------

def clean_player_name(name):
    """Remove country info and unwanted characters from player names."""
    if pd.isna(name):
        return ""
    name = re.sub(r"\(.*?\)", "", str(name))  # remove "(INDIA)" etc.
    name = re.sub(r"[^a-zA-Z\s.]", "", name)  # remove unwanted chars
    return name.strip().lower()


def fuzzy_match_name(name, choices, threshold=85):
    """Find best fuzzy match for a player name."""
    if not name or not choices:
        return None
    match, score = process.extractOne(name, choices)
    return match if score >= threshold else None


# ----------------------------------
# 🔹 Main Function
# ----------------------------------

def main():
    base_file = "outputs/cleaned_data/odi_master.csv"
    save_file = "outputs/cleaned_data/odi_master_final.csv"

    if not os.path.exists(base_file):
        print(f"❌ Base file not found: {base_file}")
        return

    print(f"✅ Loaded base ODI master: {base_file}")
    base_df = pd.read_csv(base_file)
    base_df["clean_name"] = base_df["name"].apply(clean_player_name)

    # Load external datasets
    paths = {
        "odi_data": "data/Batting/ODI_data.csv",
        "bowling_odi": "data/Bowling/Bowling_ODI.csv",
        "odi_batting": "data/kaggle_datasets/ODI_batting.csv",
        "odi_bowling": "data/kaggle_datasets/ODI_bowling.csv",
        "cricketers": "data/kaggle_datasets/cricketers.csv"
    }

    dfs = {}
    for key, path in paths.items():
        if os.path.exists(path):
            dfs[key] = pd.read_csv(path)
            print(f"📄 Loaded {key} - Shape: {dfs[key].shape}")
        else:
            print(f"⚠️ Missing file: {path}")

    # Clean player columns
    if "odi_data" in dfs:
        dfs["odi_data"]["clean_name"] = dfs["odi_data"]["Player"].apply(clean_player_name)
    if "bowling_odi" in dfs:
        dfs["bowling_odi"]["clean_name"] = dfs["bowling_odi"]["Player"].apply(clean_player_name)
    if "cricketers" in dfs:
        dfs["cricketers"]["clean_name"] = dfs["cricketers"]["Name"].apply(clean_player_name)

    # ----------------------------------
    # 🔹 Fuzzy Match + Merge
    # ----------------------------------

    def merge_with_fuzzy(base, other, other_cols, source_name):
        matches = 0
        for idx, row in tqdm(base.iterrows(), total=len(base), desc=f"Merging {source_name}"):
            name = row["clean_name"]
            match = fuzzy_match_name(name, other["clean_name"].tolist(), threshold=87)
            if match:
                matched_row = other[other["clean_name"] == match].iloc[0]
                for col in other_cols:
                    if col not in base.columns:
                        base[col] = None
                    val = matched_row[col]
                    if pd.notna(val):
                        base.at[idx, col] = val
                matches += 1
        print(f"✅ {matches} players matched and merged from {source_name}")
        return base

    # Merge ODI_data (batting stats)
    if "odi_data" in dfs:
        other_cols = ["Runs", "Ave", "HS", "BF", "SR", "Mat", "Inns", "100", "50"]
        base_df = merge_with_fuzzy(base_df, dfs["odi_data"], other_cols, "odi_data")

    # Merge Bowling_ODI (bowling stats)
    if "bowling_odi" in dfs:
        other_cols = ["Wkts", "Ave", "Econ", "SR", "BBI", "4", "5"]
        base_df = merge_with_fuzzy(base_df, dfs["bowling_odi"], other_cols, "bowling_odi")

    # Merge ODI_batting (on id)
    if "odi_batting" in dfs:
        base_df = base_df.merge(
            dfs["odi_batting"],
            on="id",
            how="left",
            suffixes=("", "_odi_batting")
        )
        print("✅ Merged odi_batting on id")

    # Merge ODI_bowling (on id)
    if "odi_bowling" in dfs:
        base_df = base_df.merge(
            dfs["odi_bowling"],
            on="id",
            how="left",
            suffixes=("", "_odi_bowling")
        )
        print("✅ Merged odi_bowling on id")

    # Merge cricketers (for Country and DOB)
    if "cricketers" in dfs:
        other_cols = ["Country", "Date_Of_Birth"]
        base_df = merge_with_fuzzy(base_df, dfs["cricketers"], other_cols, "cricketers")

    # ----------------------------------
    # 🔹 Final Cleaning
    # ----------------------------------
    base_df.drop(columns=["clean_name"], inplace=True, errors="ignore")
    base_df = base_df.loc[:, ~base_df.columns.duplicated()]
    base_df.replace(["-", "–", "NaN"], pd.NA, inplace=True)

    # Save final dataset
    os.makedirs("outputs/cleaned_data", exist_ok=True)
    base_df.to_csv(save_file, index=False)
    print(f"\n💾 Saved enriched ODI master → {save_file}")
    print(f"Final shape: {base_df.shape}")


if __name__ == "__main__":
    main()
