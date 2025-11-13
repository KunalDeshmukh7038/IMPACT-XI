import pandas as pd
import os

# ---------- CONFIG ----------
OUTPUT_DIR = "outputs/cleaned_data"
FORMAT = "ODI"   # 🔄 Change to ODI, T20, or Test
# ----------------------------

def load_data():
    bat_file = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_match_batting.csv")
    bowl_file = os.path.join(OUTPUT_DIR, f"{FORMAT.lower()}_match_bowling.csv")

    bat_df = pd.read_csv(bat_file, parse_dates=["date"])
    bowl_df = pd.read_csv(bowl_file, parse_dates=["date"])

    return bat_df, bowl_df

def query_recent_form(player, opposition, last_n=5):
    bat_df, bowl_df = load_data()

    # Filter batting & bowling data
    bat_player = bat_df[(bat_df["player"].str.contains(player, case=False, na=False)) &
                        (bat_df["opposition"].str.contains(opposition, case=False, na=False))]

    bowl_player = bowl_df[(bowl_df["player"].str.contains(player, case=False, na=False)) &
                          (bowl_df["opposition"].str.contains(opposition, case=False, na=False))]

    print(f"\n=== {player} vs {opposition} - Last {last_n} {FORMAT} Matches ===")

    # ---- Batting ----
    if not bat_player.empty:
        bat_recent = (
            bat_player.groupby("match_id")[["runs", "balls", "dismissals"]]
            .sum()
            .reset_index()
        )
        dates = bat_player.groupby("match_id")["date"].first().reset_index()
        bat_recent = bat_recent.merge(dates, on="match_id")
        bat_recent = bat_recent.sort_values("date", ascending=True).tail(last_n)

        runs = bat_recent["runs"].sum()
        balls = bat_recent["balls"].sum()
        dismissals = bat_recent["dismissals"].sum()
        matches = bat_recent["match_id"].nunique()

        avg = runs / dismissals if dismissals > 0 else runs
        sr = (runs / balls * 100) if balls > 0 else 0

        print("\nBatting Stats:")
        print(f" Matches: {matches}")
        print(f" Runs: {runs}, Balls: {balls}, Average: {avg:.2f}, SR: {sr:.2f}")

        # Match-by-match breakdown
        print("\n📊 Match-by-Match Batting Breakdown:")
        for _, row in bat_recent.iterrows():
            avg_match = row["runs"] / row["dismissals"] if row["dismissals"] > 0 else row["runs"]
            sr_match = (row["runs"] / row["balls"] * 100) if row["balls"] > 0 else 0
            print(f" {row['date'].date()} | Runs={row['runs']} (Balls={row['balls']}), "
                  f"Dismissals={row['dismissals']}, Avg={avg_match:.2f}, SR={sr_match:.2f}")
    else:
        print("\nNo Batting Records Found.")

    # ---- Bowling ----
    if not bowl_player.empty:
        bowl_recent = (
            bowl_player.groupby("match_id")[["runs_conceded", "balls", "wickets"]]
            .sum()
            .reset_index()
        )
        dates = bowl_player.groupby("match_id")["date"].first().reset_index()
        bowl_recent = bowl_recent.merge(dates, on="match_id")
        bowl_recent = bowl_recent.sort_values("date", ascending=True).tail(last_n)

        runs_conceded = bowl_recent["runs_conceded"].sum()
        balls = bowl_recent["balls"].sum()
        wkts = bowl_recent["wickets"].sum()
        matches = bowl_recent["match_id"].nunique()

        avg = runs_conceded / wkts if wkts > 0 else runs_conceded
        econ = runs_conceded / (balls / 6) if balls > 0 else 0
        sr = balls / wkts if wkts > 0 else balls

        print("\nBowling Stats:")
        print(f" Matches: {matches}")
        print(f" Overs: {balls/6:.1f}, Runs: {runs_conceded}, Wickets: {wkts}, "
              f"Average: {avg:.2f}, Econ: {econ:.2f}, SR: {sr:.2f}")

        # Match-by-match breakdown
        print("\n📊 Match-by-Match Bowling Breakdown:")
        for _, row in bowl_recent.iterrows():
            avg_match = row["runs_conceded"] / row["wickets"] if row["wickets"] > 0 else row["runs_conceded"]
            econ_match = row["runs_conceded"] / (row["balls"] / 6) if row["balls"] > 0 else 0
            sr_match = row["balls"] / row["wickets"] if row["wickets"] > 0 else row["balls"]
            print(f" {row['date'].date()} | Overs={row['balls']/6:.1f}, Runs={row['runs_conceded']}, "
                  f"Wkts={row['wickets']}, Avg={avg_match:.2f}, Econ={econ_match:.2f}, SR={sr_match:.2f}")
    else:
        print("\nNo Bowling Records Found.")

if __name__ == "__main__":
    player = input("Enter player name: ")
    opposition = input("Enter opposition team: ")
    last_n = int(input("Enter number of recent matches: "))
    query_recent_form(player, opposition, last_n)
