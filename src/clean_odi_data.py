import os
import pandas as pd

# Input files
BATTING_FILE = "data/Batting/ODI_data.csv"
BOWLING_FILE = "data/Bowling/Bowling_ODI.csv"

# Output folder
OUTPUT_FOLDER = "outputs/cleaned_data/"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def clean_batting():
    print("Reading ODI Batting CSV...")
    df = pd.read_csv(BATTING_FILE)

    # Drop junk column
    df = df.drop(columns=["Unnamed: 13"], errors="ignore")

    # Keep only useful columns
    keep_cols = ["Player", "Mat", "Inns", "NO", "Runs", "HS", "Ave", "BF", "SR", "100", "50", "0"]
    df = df[keep_cols]

    # Standardize column names
    df = df.rename(columns={
        "Player": "player",
        "Mat": "matches",
        "Inns": "innings",
        "NO": "not_outs",
        "Runs": "runs",
        "HS": "high_score",
        "Ave": "average",
        "BF": "balls_faced",
        "SR": "strike_rate",
        "100": "hundreds",
        "50": "fifties",
        "0": "ducks"
    })

    out_file = os.path.join(OUTPUT_FOLDER, "odi_batting_clean.csv")
    df.to_csv(out_file, index=False)
    print(f"Cleaned ODI batting saved to {out_file}")
    return df

def clean_bowling():
    print("Reading ODI Bowling CSV...")
    df = pd.read_csv(BOWLING_FILE)

    # Drop junk column
    df = df.drop(columns=["Unnamed: 13"], errors="ignore")

    # Keep only useful columns
    keep_cols = ["Player", "Mat", "Inns", "Balls", "Runs", "Wkts", "BBI", "Ave", "Econ", "SR", "4", "5"]
    df = df[keep_cols]

    # Standardize column names
    df = df.rename(columns={
        "Player": "player",
        "Mat": "matches",
        "Inns": "innings",
        "Balls": "balls_bowled",
        "Runs": "runs_conceded",
        "Wkts": "wickets",
        "BBI": "best_bowling",
        "Ave": "average",
        "Econ": "economy",
        "SR": "strike_rate",
        "4": "four_wkts",
        "5": "five_wkts"
    })

    out_file = os.path.join(OUTPUT_FOLDER, "odi_bowling_clean.csv")
    df.to_csv(out_file, index=False)
    print(f"Cleaned ODI bowling saved to {out_file}")
    return df

if __name__ == "__main__":
    bat_df = clean_batting()
    bowl_df = clean_bowling()

    print("\nSample Batting Data:")
    print(bat_df.head())

    print("\nSample Bowling Data:")
    print(bowl_df.head())
