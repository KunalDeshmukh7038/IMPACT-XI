import pandas as pd
import os

# ---------- CONFIG ----------
OUTPUT_DIR = "outputs/cleaned_data"
FORMAT = "ODI"   # Can switch to T20 or Test later
# ----------------------------

def load_data():
    bat_file = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_match_batting.csv")
    bowl_file = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_match_bowling.csv")

    bat_df = pd.read_csv(bat_file)
    bowl_df = pd.read_csv(bowl_file)

    return bat_df, bowl_df

def query_player_vs_venue(player, venue):
    bat_df, bowl_df = load_data()

    # Filter batting data
    bat_player = bat_df[(bat_df["player"].str.contains(player, case=False, na=False)) &
                        (bat_df["venue"].str.contains(venue, case=False, na=False))]

    # Filter bowling data
    bowl_player = bowl_df[(bowl_df["player"].str.contains(player, case=False, na=False)) &
                          (bowl_df["venue"].str.contains(venue, case=False, na=False))]

    print(f"\n=== {player} at {venue} ({FORMAT}) ===\n")

    # ---- Batting Summary ----
    if not bat_player.empty:
        runs = bat_player["runs"].sum()
        balls = bat_player["balls"].sum()
        dismissals = bat_player["dismissals"].sum()
        matches = bat_player["match_id"].nunique()

        avg = runs / dismissals if dismissals > 0 else runs
        sr = (runs / balls * 100) if balls > 0 else 0

        print("Batting Stats:")
        print(f" Matches: {matches}")
        print(f" Runs: {runs}, Balls: {balls}, Average: {avg:.2f}, SR: {sr:.2f}")
    else:
        print("No Batting Records Found.")

    # ---- Bowling Summary ----
    if not bowl_player.empty:
        runs_conceded = bowl_player["runs_conceded"].sum()
        balls = bowl_player["balls"].sum()
        wkts = bowl_player["wickets"].sum()
        matches = bowl_player["match_id"].nunique()

        avg = runs_conceded / wkts if wkts > 0 else runs_conceded
        econ = runs_conceded / (balls/6) if balls > 0 else 0
        sr = balls / wkts if wkts > 0 else balls

        print("\nBowling Stats:")
        print(f" Matches: {matches}")
        print(f" Overs: {balls/6:.1f}, Runs: {runs_conceded}, Wickets: {wkts}, "
              f"Average: {avg:.2f}, Econ: {econ:.2f}, SR: {sr:.2f}")
    else:
        print("\nNo Bowling Records Found.")

if __name__ == "__main__":
    player = input("Enter player name: ")
    venue = input("Enter venue: ")
    query_player_vs_venue(player, venue)
