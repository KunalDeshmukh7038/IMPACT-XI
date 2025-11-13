import pandas as pd
import os

# ---------- CONFIG ----------
OUTPUT_DIR = "outputs/cleaned_data"
FORMAT = "ODI"   # Can be ODI, T20, Test
# ----------------------------

def load_data():
    bat_file = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_match_batting.csv")
    bowl_file = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_match_bowling.csv")

    bat_df = pd.read_csv(bat_file)
    bowl_df = pd.read_csv(bowl_file)

    return pd.concat([bat_df, bowl_df], ignore_index=True)

def find_top_venues(player, opposition, top_n=10):
    df = load_data()

    # Filter player + opposition
    sub = df[
        (df["player"].str.contains(player, case=False, na=False)) &
        (df["opposition"].str.contains(opposition, case=False, na=False))
    ]

    if sub.empty:
        print(f"No records found for {player} vs {opposition} in {FORMAT}.")
        return

    # Group by venue
    venue_stats = (sub.groupby("venue")
                     .agg({"match_id":"nunique"})
                     .reset_index()
                     .rename(columns={"match_id":"matches"}))

    # Sort by number of matches
    venue_stats = venue_stats.sort_values("matches", ascending=False).head(top_n)

    print(f"\n=== Top Venues for {player} vs {opposition} ({FORMAT}) ===\n")
    for _, row in venue_stats.iterrows():
        print(f"- {row['venue']}: {row['matches']} matches")

if __name__ == "__main__":
    player = input("Enter player name: ")
    opposition = input("Enter opposition team: ")
    find_top_venues(player, opposition, top_n=10)
