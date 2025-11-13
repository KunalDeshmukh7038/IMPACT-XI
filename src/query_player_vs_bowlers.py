import pandas as pd
import os

# ---------- CONFIG ----------
OUTPUT_DIR = "outputs/cleaned_data"
FORMAT = "ODI"   # 🔄 Change this if needed
# ----------------------------

def load_data():
    file = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_batter_vs_bowler.csv")
    if not os.path.exists(file):
        raise FileNotFoundError(f"{file} not found. Run the parser first.")
    return pd.read_csv(file)

def query_player_vs_bowlers(player, opposition):
    df = load_data()

    # Filter for player + opposition
    sub = df[(df["batter"].str.contains(player, case=False, na=False)) &
             (df["opposition"].str.contains(opposition, case=False, na=False))]

    print(f"\n=== {player} vs {opposition} ({FORMAT}) ===\n")

    if sub.empty:
        print("❌ No records found.")
        return

    # Overall summary
    runs = sub["runs"].sum()
    balls = sub["ball"].sum()
    dismissals = sub["out"].sum()
    matches = sub["match_id"].nunique()

    avg = runs / dismissals if dismissals > 0 else runs
    sr = (runs / balls * 100) if balls > 0 else 0

    print("Overall Batting Stats:")
    print(f"Matches: {matches}")
    print(f"Runs: {runs}, Balls: {balls}, Average: {avg:.2f}, SR: {sr:.1f}\n")

    # Group by bowler
    bowler_stats = (sub.groupby("bowler")
                      .agg({"runs":"sum", "ball":"sum", "out":"sum"})
                      .reset_index())

    bowler_stats["average"] = bowler_stats.apply(
        lambda row: row["runs"]/row["out"] if row["out"]>0 else row["runs"], axis=1)
    bowler_stats["sr"] = bowler_stats.apply(
        lambda row: (row["runs"]/row["ball"]*100) if row["ball"]>0 else 0, axis=1)

    # Sort by Avg first, then SR
    ranked = bowler_stats.sort_values(["average", "sr"], ascending=[False, False])

    print("Breakdown vs Bowlers (ranked best → worst):")
    for _, row in ranked.iterrows():
        print(f"- {row['bowler']}: Runs={row['runs']}, Balls={row['ball']}, "
              f"Outs={row['out']}, Avg={row['average']:.1f}, SR={row['sr']:.1f}")

    # Best & Worst summary
    if not ranked.empty:
        best = ranked.iloc[0]
        worst = ranked.iloc[-1]

        print(f"\n✅ Best: {best['bowler']} (Avg {best['average']:.1f}, SR {best['sr']:.1f})")
        print(f"⚠️ Worst: {worst['bowler']} (Avg {worst['average']:.1f}, dismissed {int(worst['out'])} times)")

if __name__ == "__main__":
    player = input("Enter player name: ")
    opposition = input("Enter opposition team: ")
    query_player_vs_bowlers(player, opposition)
