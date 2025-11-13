# src/debug_check_oppositions.py
import pandas as pd
import os

OUTPUT_DIR = "outputs/cleaned_data"
FORMAT = "ODI"

def main():
    bowl_file = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_match_bowling.csv")
    df = pd.read_csv(bowl_file)

    player = input("Enter player name: ")

    # Flexible search for player
    df_player = df[df["player"].str.contains(player, case=False, na=False)]

    if df_player.empty:
        print(f"No bowling records found for {player}")
        return

    print(f"\nBowling records found for {player}: {len(df_player)} rows")
    print("\nUnique opposition values:")
    print(df_player["opposition"].unique())

if __name__ == "__main__":
    main()
