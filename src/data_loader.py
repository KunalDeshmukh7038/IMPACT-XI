import pandas as pd
import os

# Paths (adjust if needed)
BASE_DIR = "data/kaggle_datasets"
PLAYERS_FILE = os.path.join(BASE_DIR, "all_players.csv")
BAT_FILE = os.path.join(BASE_DIR, "ODI_batting.csv")
BOWL_FILE = os.path.join(BASE_DIR, "ODI_bowling.csv")
ALLROUND_FILE = os.path.join(BASE_DIR, "ODI_all_round.csv")

OUTPUT_FILE = "outputs/cleaned_data/odi_master.csv"


def load_and_merge():
    # Load datasets
    players = pd.read_csv(PLAYERS_FILE)
    batting = pd.read_csv(BAT_FILE)
    bowling = pd.read_csv(BOWL_FILE)
    allround = pd.read_csv(ALLROUND_FILE)

    # Ensure IDs are consistent (convert to int where possible)
    players["id"] = players["id"].astype(str)
    batting["id"] = batting["id"].astype(str)
    bowling["id"] = bowling["id"].astype(str)
    allround["id"] = allround["id"].astype(str)

    # Merge step by step
    merged = players.merge(batting, on="id", how="left", suffixes=("", "_bat"))
    merged = merged.merge(bowling, on="id", how="left", suffixes=("", "_bowl"))
    merged = merged.merge(allround, on="id", how="left", suffixes=("", "_allround"))

    # Keep only relevant columns
    cols_to_keep = [
        "id", "name", "country_id", "playing_role", "bating_style", "bowling_style",
        # Batting stats
        "matches", "innings", "runs", "average_score", "strike_rate", "100s", "50",
        # Bowling stats
        "wk", "bwa", "bwe", "bwsr",
        # Allrounder performance
        "bta", "bwa_allround", "wk_allround"
    ]

    # Some columns need renaming because merges added suffixes
    rename_map = {
        "bwa": "bowling_avg",
        "bwe": "bowling_econ",
        "bwsr": "bowling_sr",
        "wk": "wickets",
        "bta": "batting_avg_allround",
        "bwa_allround": "bowling_avg_allround",
        "wk_allround": "wickets_allround"
    }

    # Select available columns only
    final = merged[[c for c in cols_to_keep if c in merged.columns]].rename(columns=rename_map)

    # Save cleaned file
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    final.to_csv(OUTPUT_FILE, index=False)

    print(f"✅ Master ODI dataset saved at: {OUTPUT_FILE}")
    print(f"Shape: {final.shape}")
    print("Sample rows:\n", final.head(10))


if __name__ == "__main__":
    load_and_merge()
