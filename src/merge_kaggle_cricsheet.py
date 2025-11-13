import os
import pandas as pd
import re
from rapidfuzz import process, fuzz

# ---------- CONFIG ----------
OUTPUT_DIR = "outputs/cleaned_data"
FORMAT = "ODI"
# ----------------------------

def clean_name(name: str) -> str:
    """Normalize player names for better matching."""
    if not isinstance(name, str):
        return ""
    # Remove country in brackets, dots, extra spaces
    name = re.sub(r"\(.*?\)", "", name)
    name = name.replace(".", "").strip().lower()
    return name

def load_data():
    """Load CricSheet parsed match files + Kaggle datasets."""
    bat_file = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_match_batting.csv")
    bowl_file = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_match_bowling.csv")
    kaggle_bat_file = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_batting_clean.csv")
    kaggle_bowl_file = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_bowling_clean.csv")

    bat_df = pd.read_csv(bat_file)
    bowl_df = pd.read_csv(bowl_file)
    kaggle_bat_df = pd.read_csv(kaggle_bat_file)
    kaggle_bowl_df = pd.read_csv(kaggle_bowl_file)

    # clean names
    bat_df["player_clean"] = bat_df["player"].apply(clean_name)
    bowl_df["player_clean"] = bowl_df["player"].apply(clean_name)
    kaggle_bat_df["player_clean"] = kaggle_bat_df["player"].apply(clean_name)
    kaggle_bowl_df["player_clean"] = kaggle_bowl_df["player"].apply(clean_name)

    return bat_df, bowl_df, kaggle_bat_df, kaggle_bowl_df

def build_fuzzy_map(source_names, target_names, score_cutoff=85):
    """
    Build mapping from source_names → closest match in target_names
    using RapidFuzz for fuzzy matching.
    """
    mapping = {}
    for s in set(source_names):
        match = process.extractOne(
            s, target_names, scorer=fuzz.WRatio, score_cutoff=score_cutoff
        )
        if match:
            mapping[s] = match[0]
    return mapping

def merge_data():
    bat_df, bowl_df, kaggle_bat_df, kaggle_bowl_df = load_data()

    # Build fuzzy match maps
    bat_map = build_fuzzy_map(bat_df["player_clean"], kaggle_bat_df["player_clean"])
    bowl_map = build_fuzzy_map(bowl_df["player_clean"], kaggle_bowl_df["player_clean"])

    # Apply mapping
    bat_df["kaggle_match"] = bat_df["player_clean"].map(bat_map)
    bowl_df["kaggle_match"] = bowl_df["player_clean"].map(bowl_map)

    # Merge with Kaggle stats
    bat_merged = pd.merge(
        bat_df,
        kaggle_bat_df,
        left_on="kaggle_match",
        right_on="player_clean",
        how="left",
        suffixes=("", "_career")
    )

    bowl_merged = pd.merge(
        bowl_df,
        kaggle_bowl_df,
        left_on="kaggle_match",
        right_on="player_clean",
        how="left",
        suffixes=("", "_career")
    )

    # Save merged
    bat_out = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_batting_merged.csv")
    bowl_out = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_bowling_merged.csv")

    bat_merged.to_csv(bat_out, index=False)
    bowl_merged.to_csv(bowl_out, index=False)

    print(f"✅ Merged CricSheet with Kaggle career stats")
    print(f"📊 Batting columns: {list(bat_merged.columns)}")
    print(f"📊 Bowling columns: {list(bowl_merged.columns)}")

    # Show sample
    print("\n🎯 Sample Batting Data for Kohli:")
    print(bat_merged[bat_merged["player"].str.contains("Kohli", case=False)].head())

    print("\n🎯 Sample Bowling Data for Bumrah:")
    print(bowl_merged[bowl_merged["player"].str.contains("Bumrah", case=False)].head())

if __name__ == "__main__":
    merge_data()
