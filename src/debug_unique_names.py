import pandas as pd

bat_file = "outputs/cleaned_data/odi_batting_merged.csv"
bowl_file = "outputs/cleaned_data/odi_bowling_merged.csv"

def main():
    print("\n📂 Loading merged batting and bowling files...")
    bat_df = pd.read_csv(bat_file, low_memory=False)
    bowl_df = pd.read_csv(bowl_file, low_memory=False)

    print("\n=== Unique Players (Batting) ===")
    print(bat_df["player"].dropna().unique()[:20])

    print("\n=== Unique Players (Bowling) ===")
    print(bowl_df["player"].dropna().unique()[:20])

    print("\n=== Unique Oppositions (Batting) ===")
    print(bat_df["opposition"].dropna().unique()[:20])

    print("\n=== Unique Oppositions (Bowling) ===")
    print(bowl_df["opposition"].dropna().unique()[:20])

    print("\n=== Unique Cleaned Player Names (player_clean) ===")
    if "player_clean" in bat_df.columns:
        print(bat_df["player_clean"].dropna().unique()[:20])
    if "player_clean" in bowl_df.columns:
        print(bowl_df["player_clean"].dropna().unique()[:20])

if __name__ == "__main__":
    main()
