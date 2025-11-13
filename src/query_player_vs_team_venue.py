import pandas as pd
import os

# ---------- CONFIG ----------
OUTPUT_DIR = "outputs/cleaned_data"
FORMAT = "ODI"   # Can switch to T20 or Test later
# ----------------------------

def load_data():
    bat_file = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_match_batting.csv")
    bowl_file = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_match_bowling.csv")
    vs_bowler_file = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_batter_vs_bowler.csv")

    bat_df = pd.read_csv(bat_file)
    bowl_df = pd.read_csv(bowl_file)
    vs_bowler_df = pd.read_csv(vs_bowler_file)

    return bat_df, bowl_df, vs_bowler_df

def query_player_vs_team_venue(player, opposition, venue):
    bat_df, bowl_df, vs_bowler_df = load_data()

    print(f"\n=== {player} vs {opposition} at {venue} ({FORMAT}) ===\n")

    # ---------------- Batting Summary ----------------
    bat_player = bat_df[
        (bat_df["player"].str.contains(player, case=False, na=False)) &
        (bat_df["opposition"].str.contains(opposition, case=False, na=False)) &
        (bat_df["venue"].str.contains(venue, case=False, na=False))
    ]

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

    # ---------------- Bowling Summary ----------------
    bowl_player = bowl_df[
        (bowl_df["player"].str.contains(player, case=False, na=False)) &
        (bowl_df["opposition"].str.contains(opposition, case=False, na=False)) &
        (bowl_df["venue"].str.contains(venue, case=False, na=False))
    ]

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

    # ---------------- Breakdown vs Bowlers ----------------
    vs_bowler = vs_bowler_df[
        (vs_bowler_df["batter"].str.contains(player, case=False, na=False)) &
        (vs_bowler_df["opposition"].str.contains(opposition, case=False, na=False)) &
        (vs_bowler_df["venue"].str.contains(venue, case=False, na=False))
    ]

    if not vs_bowler.empty:
        bowler_stats = (vs_bowler.groupby("bowler")
                          .agg({"runs":"sum", "ball":"sum", "out":"sum"})
                          .reset_index())

        bowler_stats["average"] = bowler_stats.apply(
            lambda row: row["runs"]/row["out"] if row["out"]>0 else row["runs"], axis=1)
        bowler_stats["sr"] = bowler_stats.apply(
            lambda row: (row["runs"]/row["ball"]*100) if row["ball"]>0 else 0, axis=1)

        ranked = bowler_stats.sort_values(["average", "sr"], ascending=[False, False])

        print("\nBreakdown vs Bowlers at Venue:")
        for _, row in ranked.iterrows():
            print(f"- {row['bowler']}: Runs={row['runs']}, Balls={row['ball']}, "
                  f"Outs={row['out']}, Avg={row['average']:.1f}, SR={row['sr']:.1f}")

        best = ranked.iloc[0]
        worst = ranked.iloc[-1]

        print(f"\n✅ Best: {best['bowler']} (Avg {best['average']:.1f}, SR {best['sr']:.1f})")
        print(f"⚠️ Worst: {worst['bowler']} (Avg {worst['average']:.1f}, dismissed {int(worst['out'])} times)")
    else:
        print("\nNo Batter-vs-Bowler Records Found at this venue.")

if __name__ == "__main__":
    player = input("Enter player name: ")
    opposition = input("Enter opposition team: ")
    venue = input("Enter venue: ")
    query_player_vs_team_venue(player, opposition, venue)
