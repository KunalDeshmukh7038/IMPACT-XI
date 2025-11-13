import pandas as pd
import os

# ---------- CONFIG ----------
OUTPUT_DIR = "outputs/cleaned_data"
FORMAT = "odi"   # 🔄 Change if you want T20 or Test later
# ----------------------------

def load_merged_data():
    bat_file = os.path.join(OUTPUT_DIR, f"{FORMAT}_batting_merged.csv")
    bowl_file = os.path.join(OUTPUT_DIR, f"{FORMAT}_bowling_merged.csv")

    bat_df = pd.read_csv(bat_file)
    bowl_df = pd.read_csv(bowl_file)

    return bat_df, bowl_df

def debug_player(player_name):
    bat_df, bowl_df = load_merged_data()

    # Filter by name
    bat_player = bat_df[bat_df["player"].str.contains(player_name, case=False, na=False)]
    bowl_player = bowl_df[bowl_df["player"].str.contains(player_name, case=False, na=False)]

    print(f"\n🔎 Checking merged data for: {player_name}\n")

    # Show batting records
    if not bat_player.empty:
        print("=== Batting Sample Matches ===")
        print(bat_player.head(5)[[
            "date", "venue", "opposition", "runs", "balls",
            "runs_career", "hundreds", "fifties", "average"
        ]])
    else:
        print("❌ No batting records found")

    # Show bowling records
    if not bowl_player.empty:
        print("\n=== Bowling Sample Matches ===")
        print(bowl_player.head(5)[[
            "date", "venue", "opposition", "balls", "runs_conceded", "wickets",
            "wickets_career", "best_bowling", "economy", "strike_rate"
        ]])
    else:
        print("❌ No bowling records found")

if __name__ == "__main__":
    player = input("Enter player name: ")
    debug_player(player)
